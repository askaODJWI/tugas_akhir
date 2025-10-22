from pathlib import Path
import json
import pandas as pd
import re

INPUT_DIR = Path("../../Scraping/hasil_scraping/per_district_json")
OUTPUT_CSV = Path("olx_merged.csv")
OUTPUT_PARQUET = Path("olx_merged.parquet")
DEBUG_SAMPLE_OUT = Path("debug_samples_extracted.json")


def _safe(d, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default)
    return cur


def parse_price(ad):
    # Many variants: price -> value -> raw, or price -> value.raw, or price.value.display
    p = ad.get("price")
    if isinstance(p, dict):
        val = p.get("value")
        if isinstance(val, dict):
            raw = val.get("raw") or val.get("amount")
            disp = val.get("display")
            curr = _safe(val, "currency", "iso_4217") or _safe(val, "currency", "pre")
            return raw, disp, curr
        # maybe price.value is number
        if isinstance(p.get("value"), (int, float)):
            return p.get("value"), None, None
        # fallback: price may directly have raw
        raw = p.get("raw") or p.get("value")
        return raw, None, None
    # fallback: search top-level keys
    for key in ("price_raw", "price", "amount"):
        if key in ad and isinstance(ad[key], (int, float)):
            return ad[key], None, None
    return None, None, None


def parse_images(ad):
    imgs = ad.get("images") or ad.get("gallery") or []
    urls = []
    if isinstance(imgs, list):
        for it in imgs:
            if isinstance(it, str):
                urls.append(it)
            elif isinstance(it, dict):
                # prefer url, then full.url, then big.url
                u = it.get("url") or _safe(it, "full", "url") or _safe(it, "big", "url")
                if u:
                    urls.append(u)
    return urls


def parse_locations(ad):
    # Prefer 'locations' list with dict containing lat/lon
    lat = lon = None
    locs = ad.get("locations")
    if isinstance(locs, list) and len(locs) > 0 and isinstance(locs[0], dict):
        loc0 = locs[0]
        lat = loc0.get("lat") or loc0.get("latitude")
        lon = loc0.get("lon") or loc0.get("longitude")
    # fallback: direct lat/lon keys somewhere
    if lat is None or lon is None:
        if "lat" in ad and "lon" in ad:
            lat = ad.get("lat")
            lon = ad.get("lon")
    # resolved names
    res = (
        ad.get("locations_resolved")
        or ad.get("location_resolved")
        or ad.get("address")
        or {}
    )
    country = res.get("COUNTRY_name") or res.get("country") or None
    province = res.get("ADMIN_LEVEL_1_name") or res.get("province") or None
    city = res.get("ADMIN_LEVEL_3_name") or res.get("city") or None
    sublocal = res.get("SUBLOCALITY_LEVEL_1_name") or res.get("sublocality") or None
    # address-like parameter in parameters sometimes present under key 'p_alamat'
    return (lat, lon, country, province, city, sublocal)


def parse_parameters(ad):
    params = ad.get("parameters") or ad.get("attributes") or []
    pmap = {}
    if isinstance(params, list):
        for p in params:
            if not isinstance(p, dict):
                continue
            key = p.get("key") or p.get("name") or p.get("k")
            # some keys have prefix like 'parameter-external_source_url' in sample
            if not key:
                continue
            # value candidates
            val = (
                p.get("absoluteValue")
                or p.get("value")
                or p.get("value_name")
                or p.get("formatted_value")
            )
            # if multi-value: collect as comma string
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
    # try to extract some useful standardized fields
    out = {
        "property_type": pmap.get("type") or pmap.get("property_type"),
        "building_area_m2": _to_float(
            pmap.get("p_sqr_building")
            or pmap.get("building_area")
            or pmap.get("luas_bangunan")
        ),
        "land_area_m2": _to_float(
            pmap.get("p_sqr_land") or pmap.get("land_area") or pmap.get("luas_tanah")
        ),
        "bedrooms": _to_int(
            pmap.get("p_bedroom") or pmap.get("p_bedrooms") or pmap.get("bedroom")
        ),
        "bathrooms": _to_int(pmap.get("p_bathroom") or pmap.get("bathroom")),
        "floor": _to_int(pmap.get("p_floor") or pmap.get("floor")),
        "external_source_url": pmap.get("external_source_url")
        or pmap.get("external_source_label"),
        "p_alamat": pmap.get("p_alamat") or None,
        "raw_params": pmap,
    }
    return out


def _to_float(x):
    if x is None:
        return None
    try:
        # remove non-digit except dot and comma
        s = str(x)
        s = re.sub(r"[^\d\.,\-]", "", s)
        s = s.replace(",", "")
        return float(s)
    except:
        return None


def _to_int(x):
    f = _to_float(x)
    if f is None:
        return None
    try:
        return int(round(f))
    except:
        return None


def process_file(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        j = json.loads(text)
    except Exception:
        # try as JSON-lines
        items = []
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                items.append(json.loads(ln))
            except:
                continue
        j = items
    # extract list of ads:
    if isinstance(j, dict):
        # find key that contains list-of-dict
        for k in ("ads", "results", "items", "data", "hits"):
            if k in j and isinstance(j[k], list):
                ads = j[k]
                break
        else:
            # maybe j itself is one ad -> wrap
            ads = [j]
    elif isinstance(j, list):
        ads = j
    else:
        ads = [j]

    rows = []
    for ad in ads:
        if not isinstance(ad, dict):
            continue
        # ad id
        ad_id = ad.get("ad_id") or ad.get("id") or ad.get("ads_id")
        title = ad.get("title") or ad.get("name")
        description = ad.get("description") or ad.get("desc")
        price_raw, price_display, currency = parse_price(ad)
        imgs = parse_images(ad)
        images_count = len(imgs)
        first_image = imgs[0] if imgs else None
        lat, lon, country, province, city, sublocal = parse_locations(ad)
        params = parse_parameters(ad)
        main_info = ad.get("main_info")
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
            "building_area_m2": params.get("building_area_m2"),
            "land_area_m2": params.get("land_area_m2"),
            "bedrooms": params.get("bedrooms"),
            "bathrooms": params.get("bathrooms"),
            "floor": params.get("floor"),
            "external_source_url": params.get("external_source_url"),
            "p_alamat": params.get("p_alamat"),
            "raw_parameters": json.dumps(
                params.get("raw_params", {}), ensure_ascii=False
            ),
            "source_file": path.name,
        }
        rows.append(row)
    return rows


def main():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(INPUT_DIR.glob("*.json"))
    if not files:
        print("No JSON files found in", INPUT_DIR)
        return
    all_rows = []
    # limit debug sample extraction for inspection
    debug_samples = []
    for f in files:
        print("Processing", f.name)
        rows = process_file(f)
        print(f"  -> extracted {len(rows)} ads from {f.name}")
        all_rows.extend(rows)
        # collect up to 20 raw examples for inspection
        if len(debug_samples) < 20:
            debug_samples.extend(rows[: 20 - len(debug_samples)])
    if not all_rows:
        print("No rows extracted.")
        return
    df = pd.DataFrame(all_rows)
    # dedupe by ad_id (some files may contain same ad)
    if "ad_id" in df.columns:
        df = df.drop_duplicates(subset=["ad_id"])
    # save debug small sample of extracted rows
    DEBUG_SAMPLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEBUG_SAMPLE_OUT.write_text(
        json.dumps(debug_samples, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Save CSV and parquet
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    try:
        df.to_parquet(OUTPUT_PARQUET, index=False)
    except Exception:
        pass

    # Print summary of non-null counts to help diagnosis
    print("\nSaved", OUTPUT_CSV, "rows:", len(df))
    print("\nNon-null counts per column:")
    print(df.notnull().sum().sort_values(ascending=False))

    # show sample rows
    print("\nSample rows (first 3):")
    print(df.head(3).to_dict(orient="records"))


if __name__ == "__main__":
    main()
