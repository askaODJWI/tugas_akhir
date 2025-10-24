# copy-paste seluruh blok ini ke satu cell di notebook (atau simpan sebagai dataset_builder.py)
import json, re
from pathlib import Path
from ast import literal_eval
import pandas as pd
import numpy as np

# ---------- CONFIG ----------
INPUT_DIR = Path(
    "../../Scraping/hasil_scraping/per_district_json"
)  # ubah ke folder JSON hasil scrapingmu
OUTPUT_XLSX = Path("raw_dataset.xlsx")
DEBUG_SAMPLE_JSON = Path("debug_samples_extracted.json")
THRESH_FLOOR = 50  # batas wajar jumlah lantai (ubah kalau perlu)
MAX_SAMPLE_DEBUG = 30

# ---------- helper utils ----------
_re_digits = re.compile(r"[^\d\.\-]")


def sanitize_text(s):
    """Remove problematic control chars for Excel; normalize whitespace."""
    if s is None:
        return None
    if not isinstance(s, str):
        s = str(s)
    # remove null bytes and most C0 control chars except newline/tab
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", s)
    # normalize multiple whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _safe(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur


def _to_float_loose(x):
    if x is None:
        return None
    try:
        s = str(x)
        s = re.sub(r"[^\d\.,\-]", "", s)
        s = s.replace(",", "")
        return float(s)
    except:
        return None


def _to_int_loose(x):
    f = _to_float_loose(x)
    if f is None:
        return None
    try:
        return int(round(f))
    except:
        return None


# ---------- parsing building/land from main_info ----------
_maininfo_area_re = re.compile(r"([0-9]{1,4}(?:[.,][0-9]+)?)\s*m(?:2|²)?\b", re.I)


def parse_area_from_maininfo(main_info):
    if not main_info or not isinstance(main_info, str):
        return None
    m = _maininfo_area_re.search(main_info)
    if m:
        try:
            return float(m.group(1).replace(",", "."))
        except:
            return None
    return None


# ---------- floor extraction from description/title/params ----------
_floor_token_re = re.compile(r"(?:lantai|lt|lt\.|floor)[\s:\-]*(\d{1,3})\b", re.I)
_floor_after_num_re = re.compile(r"\b(\d{1,3})\s*(?:lantai|lt|lt\.|floor)\b", re.I)


def extract_floor_from_text(txt):
    if not txt or not isinstance(txt, str):
        return None
    txt = txt.lower()
    m = _floor_token_re.search(txt)
    if m:
        return int(m.group(1))
    m = _floor_after_num_re.search(txt)
    if m:
        return int(m.group(1))
    return None


# ---------- parse functions (price, images, locations, parameters) ----------
def parse_price(ad):
    p = ad.get("price")
    if isinstance(p, dict):
        val = p.get("value")
        if isinstance(val, dict):
            raw = val.get("raw") or val.get("amount")
            disp = val.get("display")
            curr = _safe(val, "currency", "iso_4217") or _safe(val, "currency", "pre")
            return raw, disp, curr
        if isinstance(p.get("value"), (int, float)):
            return p.get("value"), None, None
        raw = p.get("raw") or p.get("value")
        return raw, None, None
    # fallback
    for key in ("price_raw", "price", "amount"):
        if key in ad and isinstance(ad[key], (int, float)):
            return ad[key], None, None
    return None, None, None


def parse_images(ad):
    imgs = ad.get("images") or ad.get("gallery") or []
    out = []
    if isinstance(imgs, list):
        for it in imgs:
            if isinstance(it, str):
                out.append(it)
            elif isinstance(it, dict):
                u = it.get("url") or _safe(it, "full", "url") or _safe(it, "big", "url")
                if u:
                    out.append(u)
    return out


def parse_locations(ad):
    lat = lon = None
    locs = ad.get("locations") or ad.get("Locations")
    if isinstance(locs, list) and locs:
        first = locs[0]
        if isinstance(first, dict):
            lat = first.get("lat") or first.get("latitude")
            lon = first.get("lon") or first.get("longitude")
    if (lat is None or lon is None) and "lat" in ad and "lon" in ad:
        lat = ad.get("lat")
        lon = ad.get("lon")
    # resolved names from locations_resolved or address
    res = (
        ad.get("locations_resolved")
        or ad.get("location_resolved")
        or ad.get("address")
        or {}
    )
    country = res.get("COUNTRY_name") or res.get("country") or None
    province = res.get("ADMIN_LEVEL_1_name") or res.get("province") or None
    city = res.get("ADMIN_LEVEL_3_name") or res.get("city") or None
    sublocal = (
        res.get("SUBLOCALITY_LEVEL_1_name")
        or res.get("SUBLOCALITY_LEVEL_1_name")
        or res.get("SUBLOCALITY_LEVEL_1_name")
        or res.get("SUBLOCALITY_LEVEL_1_name")
        or res.get("sublocality")
        or res.get("SUBLOCALITY_LEVEL_1_name")
    )
    # some JSON uses different names; fallback attempts above
    return lat, lon, country, province, city, sublocal


def parse_parameters(ad):
    params = ad.get("parameters") or ad.get("attributes") or []
    pmap = {}
    if isinstance(params, list):
        for p in params:
            if not isinstance(p, dict):
                continue
            key = p.get("key") or p.get("name") or p.get("k") or p.get("key_name")
            if not key:
                continue
            # pick sensible value
            val = (
                p.get("absoluteValue")
                or p.get("value")
                or p.get("value_name")
                or p.get("formatted_value")
            )
            # multip-value
            if val is None and "values" in p and isinstance(p["values"], list):
                vals = []
                for vv in p["values"]:
                    if isinstance(vv, dict):
                        vv_val = vv.get("value") or vv.get("label") or None
                        if vv_val:
                            vals.append(str(vv_val))
                    else:
                        vals.append(str(vv))
                if vals:
                    val = ", ".join(vals)
            if val is not None:
                pmap[str(key)] = val
    # standardize to expected columns (safe conversions)
    out = {}
    out["raw_params"] = pmap
    out["property_type"] = pmap.get("type") or pmap.get("property_type")
    out["building_area_m2"] = _to_float_loose(
        pmap.get("p_sqr_building")
        or pmap.get("building_area")
        or pmap.get("luas_bangunan")
    )
    out["land_area_m2"] = _to_float_loose(
        pmap.get("p_sqr_land") or pmap.get("land_area") or pmap.get("luas_tanah")
    )
    out["bedrooms"] = _to_int_loose(
        pmap.get("p_bedroom") or pmap.get("p_bedrooms") or pmap.get("bedroom")
    )
    out["bathrooms"] = _to_int_loose(pmap.get("p_bathroom") or pmap.get("bathroom"))
    # floor: be conservative (int) - don't accept giant values here (we'll sanitize later)
    out["floor_param"] = _to_int_loose(
        pmap.get("p_floor") or pmap.get("floor") or pmap.get("p_floor_label")
    )
    out["external_source_url"] = pmap.get("external_source_url") or pmap.get(
        "external_source_label"
    )
    out["p_alamat"] = pmap.get("p_alamat") or None
    return out


# ---------- process one file (returns list of rows) ----------
def process_file(path):
    txt = path.read_text(encoding="utf-8", errors="replace")
    # try to load JSON robustly (object, list, or ndjson)
    try:
        j = json.loads(txt)
    except Exception:
        items = []
        for ln in txt.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except:
                # last-resort: try literal_eval fallback (less safe)
                try:
                    items.append(literal_eval(ln))
                except:
                    continue
        j = items
    # find array of ads or wrap
    if isinstance(j, dict):
        for k in ("ads", "results", "items", "data", "hits"):
            if k in j and isinstance(j[k], list):
                ads = j[k]
                break
        else:
            ads = [j]
    elif isinstance(j, list):
        ads = j
    else:
        ads = [j]

    rows = []
    for ad in ads:
        if not isinstance(ad, dict):
            continue
        ad_id = ad.get("ad_id") or ad.get("id") or ad.get("ads_id") or ad.get("adId")
        title = sanitize_text(ad.get("title") or ad.get("name"))
        description = sanitize_text(ad.get("description") or ad.get("desc"))
        price_raw, price_display, currency = parse_price(ad)
        imgs = parse_images(ad)
        images_count = len(imgs)
        first_image = imgs[0] if imgs else None
        lat, lon, country, province, city, sublocal = parse_locations(ad)
        params = parse_parameters(ad)
        main_info = ad.get("main_info") or ad.get("mainInfo") or None
        created_at = (
            ad.get("created_at") or ad.get("created_at_first") or ad.get("created")
        )
        user_id = ad.get("user_id") or ad.get("user")
        user_name = ad.get("user_name") or None
        status = (
            _safe(ad, "status", "display")
            if isinstance(ad.get("status"), dict)
            else ad.get("status")
        )
        # try to extract areas from main_info if params unknown
        building_area = params.get("building_area_m2") or parse_area_from_maininfo(
            main_info
        )
        land_area = params.get("land_area_m2") or parse_area_from_maininfo(main_info)
        row = {
            "ad_id": ad_id,
            "title": title,
            "description": description,
            "price_raw": price_raw,
            "price_display": price_display,
            "currency": currency,
            "images_count": images_count,
            "first_image_url": first_image,
            "main_info": main_info,
            "created_at": created_at,
            "user_id": user_id,
            "user_name": user_name,
            "status": status,
            "country_name": country,
            "province_name": province,
            "city_name": city,
            "sublocality_name": sublocal,
            "lat": lat,
            "lon": lon,
            "property_type": params.get("property_type"),
            "building_area_m2": building_area,
            "land_area_m2": land_area,
            "bedrooms": params.get("bedrooms"),
            "bathrooms": params.get("bathrooms"),
            # keep param-extracted floor in a separate column; do NOT trust blindly
            "floor_param": params.get("floor_param"),
            "external_source_url": params.get("external_source_url"),
            "p_alamat": params.get("p_alamat"),
            "raw_parameters": json.dumps(
                params.get("raw_params", {}), ensure_ascii=False
            ),
            "source_file": path.name,
        }
        rows.append(row)
    return rows


# ---------- master routine ----------
def build_dataset(
    input_dir=INPUT_DIR, out_xlsx=OUTPUT_XLSX, debug_json=DEBUG_SAMPLE_JSON
):
    input_dir = Path(input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"Input dir not found: {input_dir}")
    files = sorted(input_dir.glob("*.json"))
    all_rows = []
    debug_samples = []
    for f in files:
        print("Processing", f.name)
        rows = process_file(f)
        print("  ->", len(rows), "ads")
        all_rows.extend(rows)
        if len(debug_samples) < MAX_SAMPLE_DEBUG:
            debug_samples.extend(rows[: max(0, MAX_SAMPLE_DEBUG - len(debug_samples))])
    if not all_rows:
        raise RuntimeError("No ads extracted")

    df = pd.DataFrame(all_rows)
    # dedupe: prefer ad_id, else external_source_url, else first_image_url
    if "ad_id" in df.columns:
        df = df.drop_duplicates(subset=["ad_id"])
    # try also dedupe by external url if available
    if "external_source_url" in df.columns:
        df = df.drop_duplicates(subset=["external_source_url"], keep="first")
    # coerce numeric columns
    for c in (
        "price_raw",
        "building_area_m2",
        "land_area_m2",
        "bedrooms",
        "bathrooms",
        "lat",
        "lon",
    ):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # sanitize text columns again (ensure no remaining control chars)
    for c in ("title", "description", "p_alamat"):
        if c in df.columns:
            df[c] = df[c].apply(sanitize_text)

    # FLOOR: robust finalization:
    # start from floor_param (if exists & reasonable), else try extracting from description/title/main_info
    df["floor_from_param"] = pd.to_numeric(df.get("floor_param"), errors="coerce")
    df["floor_from_text"] = df.apply(
        lambda r: extract_floor_from_text(r.get("description") or "")
        or extract_floor_from_text(r.get("title") or ""),
        axis=1,
    )
    # if floor equals building/land area -> treat suspicious and drop (we'll use text candidate)
    eq_building = (
        df["floor_from_param"].notna()
        & df["building_area_m2"].notna()
        & (df["floor_from_param"] == df["building_area_m2"])
    )
    eq_land = (
        df["floor_from_param"].notna()
        & df["land_area_m2"].notna()
        & (df["floor_from_param"] == df["land_area_m2"])
    )
    suspicious = eq_building | eq_land | (df["floor_from_param"] > THRESH_FLOOR)
    print("floor suspicious (eq area or >THRESH):", suspicious.sum())
    df.loc[suspicious, "floor_from_param"] = np.nan

    # final floor: prefer param then text; enforce <= THRESH_FLOOR
    def choose_floor(row):
        v = row.get("floor_from_param")
        if pd.notna(v) and 0 <= v <= THRESH_FLOOR:
            return int(v)
        v2 = row.get("floor_from_text")
        if v2 is not None and 0 <= v2 <= THRESH_FLOOR:
            return int(v2)
        return pd.NA

    df["floor"] = df.apply(choose_floor, axis=1).astype("Int64")

    # build full_address: prefer p_alamat > combination of city+sub locality
    def build_full_addr(r):
        pa = r.get("p_alamat")
        if pa:
            return pa
        parts = []
        if r.get("sublocality_name"):
            parts.append(r.get("sublocality_name"))
        if r.get("city_name"):
            parts.append(r.get("city_name"))
        if r.get("province_name"):
            parts.append(r.get("province_name"))
        return ", ".join(parts) if parts else None

    df["full_address"] = df.apply(build_full_addr, axis=1)

    # save debug sample
    debug_json.write_text(
        json.dumps(debug_samples, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Save to Excel (openpyxl)
    df.to_excel(out_xlsx, index=False, engine="openpyxl")
    print("Saved processed dataset to:", out_xlsx)
    return df


# ---------- run ----------
if __name__ == "__main__":
    df = build_dataset()
