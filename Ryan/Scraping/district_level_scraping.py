"""
Usage:
  python district_level_scraper_robust.py
  python district_level_scraper_robust.py --batch-size 7 --start-index 0
"""

import argparse
import json
import random
import signal
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests

# CONFIG
BASE_URL = "https://www.olx.co.id/api/relevance/v4/search"
CATEGORY = "5158"
PER_CITY_JSON_DIR = Path("hasil_scraping") / "per_city_json"
OUTPUT_DIR = Path("hasil_scraping") / "per_district_json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HEADERS_FILE = "headers.txt"
HTML_DUMPS = Path("hasil_scraping") / "district_html_dumps"
HTML_DUMPS.mkdir(parents=True, exist_ok=True)

PAGE_SIZE = 20
SAFE_PAGE_LIMIT = 45  # threshold untuk tandai needs_split
REQUEST_TIMEOUT = 60
MAX_RETRIES = 6
BACKOFF_BASE = 1.0
SLEEP_BETWEEN_REQUESTS = 0.15
SESSION = None  # will be requests.Session() later

# Global progress flag to handle graceful shutdown
SHOULD_STOP = False


def signal_handler(sig, frame):
    global SHOULD_STOP
    print("\n[!] Received interrupt — will finish current work and exit gracefully...")
    SHOULD_STOP = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def load_headers(path: str) -> Dict[str, str]:
    headers = {}
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]

    key = None
    for line in lines:
        if not line.strip():
            continue
        if key is None:
            key = line.strip().lower()
        else:
            headers[key] = line.strip()
            key = None
    # remove pseudo headers
    for k in list(headers.keys()):
        if k.startswith(":"):
            headers.pop(k, None)
    print(f"{len(headers)} header berhasil dimuat dari {path}")
    return headers


def extract_district_ids_from_city_json(json_path: Path) -> Dict[str, Optional[str]]:
    district_map: Dict[str, Optional[str]] = {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"   Gagal buka {json_path}: {e}")
        return district_map

    for ad in data:
        if not isinstance(ad, dict):
            continue
        locs = ad.get("locations") or []
        if isinstance(locs, list):
            for l in locs:
                if isinstance(l, dict):
                    did = (
                        l.get("district_id") or l.get("districtId") or l.get("district")
                    )
                    if did:
                        lr = ad.get("locations_resolved") or {}
                        sample = None
                        if isinstance(lr, dict):
                            sample = (
                                lr.get("SUBLOCALITY_LEVEL_1_name")
                                or lr.get("ADMIN_LEVEL_3_name")
                                or lr.get("SUBLOCALITY_NAME")
                            )
                        district_map[str(did)] = sample
        # fallback
        if not district_map:
            lr = ad.get("locations_resolved") or {}
            if isinstance(lr, dict):
                did = lr.get("SUBLOCALITY_LEVEL_1_id") or lr.get("district_id")
                if did:
                    sample = (
                        lr.get("SUBLOCALITY_LEVEL_1_name")
                        or lr.get("ADMIN_LEVEL_3_name")
                        or lr.get("SUBLOCALITY_NAME")
                    )
                    district_map[str(did)] = sample
    return district_map


def fetch_page_for_location(
    session: requests.Session, location_id: str, page_num: int
) -> requests.Response:
    params = {
        "category": CATEGORY,
        "facet_limit": 100,
        "location": location_id,
        "page": page_num,
        "platform": "web-desktop",
    }
    attempt = 0
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            res = session.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT)
            # handle server-side rate-limit hints
            if res.status_code == 429:
                # too many requests — aggressive backoff
                sleep_for = BACKOFF_BASE * (2**attempt) + random.random() * 2.0
                print(
                    f"         429 received, backing off {sleep_for:.1f}s (attempt {attempt})"
                )
                time.sleep(sleep_for)
                continue
            if 500 <= res.status_code < 600:
                # server error — retry
                sleep_for = BACKOFF_BASE * (2**attempt) + random.random() * 1.0
                print(
                    f"         server error {res.status_code}, backoff {sleep_for:.1f}s (attempt {attempt})"
                )
                time.sleep(sleep_for)
                continue
            res.raise_for_status()
            return res
        except requests.exceptions.RequestException as e:
            if attempt >= MAX_RETRIES:
                raise
            sleep_for = BACKOFF_BASE * (2**attempt) + random.random() * 0.5
            print(
                f"         retry {attempt}/{MAX_RETRIES} after error: {e}. backoff={sleep_for:.1f}s"
            )
            time.sleep(sleep_for)
    raise RuntimeError("Exhausted retries")


def scrape_location(
    session: requests.Session, location_id: str, out_dir: Path
) -> Tuple[List[dict], bool]:
    all_ads = []
    page = 1
    needs_split = False
    while True:
        if SHOULD_STOP:
            print("    -> received stop signal, terminating this location early.")
            break
        try:
            res = fetch_page_for_location(session, location_id, page)
        except Exception as e:
            print(f"      Request error pada halaman {page} (loc {location_id}): {e}")
            break

        content_type = res.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            # simpan dump untuk analisa (mungkin captcha/HTML)
            dump_path = HTML_DUMPS / f"loc_{location_id}_page{page}.html"
            with open(dump_path, "wb") as fw:
                fw.write(res.content)
            print(f"      Response bukan JSON, dump disimpan: {dump_path}")
            break

        try:
            data = res.json()
        except Exception as e:
            print(f"      Gagal decode JSON untuk loc {location_id} page {page}: {e}")
            break

        ads = data.get("data", []) if isinstance(data, dict) else []
        if not ads:
            # selesai pages
            break

        print(f"      {len(ads)} iklan diambil dari halaman {page}")
        all_ads.extend(ads)

        if len(ads) < PAGE_SIZE:
            break

        page += 1
        if page > SAFE_PAGE_LIMIT:
            print(
                f"      Mencapai SAFE_PAGE_LIMIT ({SAFE_PAGE_LIMIT}) — tandai needs_split."
            )
            needs_split = True
            break

        time.sleep(SLEEP_BETWEEN_REQUESTS + random.random() * 0.2)

    # save per-location JSON (even if empty) to out_dir
    out_path = out_dir / f"loc_{location_id}.json"
    with open(out_path, "w", encoding="utf-8") as fw:
        json.dump(all_ads, fw, ensure_ascii=False, indent=2)

    return all_ads, needs_split


def combine_and_save_city(city_label: str, collected_ads: List[dict], out_dir: Path):
    unique = {}
    for ad in collected_ads:
        aid = ad.get("id") or ad.get("ads_id") or ad.get("ad_id")
        if not aid:
            continue
        unique[str(aid)] = ad
    combined = list(unique.values())
    out_combined = out_dir / f"olx_combined_{city_label}.json"
    with open(out_combined, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    return len(combined)


def load_progress(path: Path) -> Dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_progress(path: Path, data: Dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def run(args):
    global SESSION
    if not Path(HEADERS_FILE).exists():
        print("File headers.txt tidak ditemukan.")
        return

    headers = load_headers(HEADERS_FILE)
    session = requests.Session()
    session.headers.update(headers)
    SESSION = session

    # list city JSON files sorted (alphabetical)
    city_json_files = sorted(PER_CITY_JSON_DIR.glob("olx_*.json"))
    if not city_json_files:
        print(
            "Tidak ada olx_*.json di folder per_city_json. Jalankan city-level dahulu."
        )
        return

    # apply batch slicing if requested
    start = args.start_index or 0
    if args.end_index is not None:
        end = args.end_index
    elif args.batch_size:
        end = min(len(city_json_files), start + args.batch_size)
    else:
        end = len(city_json_files)

    city_json_files = city_json_files[start:end]
    print(f"Processing city files {start}..{end-1} (count {len(city_json_files)})")

    grand_total = 0
    for jf in city_json_files:
        city_label = jf.stem.replace("olx_", "")
        print(f"\nMemproses file kota: {city_label} -> {jf}")
        city_out_dir = OUTPUT_DIR / city_label
        city_out_dir.mkdir(parents=True, exist_ok=True)

        # load progress checkpoint for this city
        progress_file = city_out_dir / "progress.json"
        progress = load_progress(progress_file)
        processed_districts = set(progress.get("processed_districts", []))

        district_map = extract_district_ids_from_city_json(jf)
        if not district_map:
            print("   Tidak ditemukan district/sub-lokal pada file ini. Lewati.")
            continue

        print(
            f"   Ditemukan {len(district_map)} district/sub-lokal. Mulai scrape per-district..."
        )

        city_ads_collected = []
        needs_split_list = []

        # iterate sorted to be deterministic
        for district_id, sample_name in sorted(
            district_map.items(), key=lambda x: x[0]
        ):
            if SHOULD_STOP:
                print("Received stop signal — saving progress and breaking outer loop.")
                break

            if district_id in processed_districts:
                # skip already processed
                print(f"   - skipping district {district_id} (already processed)")
                # if a per-location file exists, load and add to collected
                loc_file = city_out_dir / f"loc_{district_id}.json"
                if loc_file.exists():
                    try:
                        with open(loc_file, "r", encoding="utf-8") as fr:
                            ads = json.load(fr)
                            city_ads_collected.extend(
                                ads if isinstance(ads, list) else []
                            )
                    except Exception:
                        pass
                continue

            print(f"   - scraping district {district_id} (sample: {sample_name})")
            try:
                ads, needs_split = scrape_location(session, district_id, city_out_dir)
            except Exception as e:
                print(f"      Gagal scrape district {district_id}: {e}")
                ads, needs_split = [], False

            print(f"      selesai district {district_id}, iklan: {len(ads)}")
            processed_districts.add(district_id)
            # update progress on disk frequently
            progress["processed_districts"] = sorted(processed_districts)
            save_progress(progress_file, progress)

            city_ads_collected.extend(ads)
            if needs_split:
                needs_split_list.append((district_id, sample_name))

            # politeness
            time.sleep(0.2 + random.random() * 0.4)

        # combine & save per-city combined file
        unique_count = combine_and_save_city(city_label, city_ads_collected, OUTPUT_DIR)
        print(
            f"   Selesai {city_label}: total unik iklan dari semua district = {unique_count}"
        )
        grand_total += unique_count

        # save needs_split list
        if needs_split_list:
            ns_path = city_out_dir / "needs_split.json"
            with open(ns_path, "w", encoding="utf-8") as f:
                json.dump(
                    [{"district_id": d, "sample_name": s} for d, s in needs_split_list],
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            print(f"   District yang perlu dipecah disimpan ke: {ns_path}")

        if SHOULD_STOP:
            print("Terminated by user request; saving final progress and exiting.")
            break

    print("\nSelesai semua (dalam batch). Total terkumpul:", grand_total)
    print("Per-district JSONs di:", OUTPUT_DIR)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--start-index", type=int, help="Index file kota untuk mulai (0-indexed)"
    )
    p.add_argument("--end-index", type=int, help="Index file kota akhir (exclusive)")
    p.add_argument(
        "--batch-size",
        type=int,
        help="Jika diberikan: proses maksimal N file kota mulai dari start-index",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args)
