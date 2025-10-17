import json
import requests
from pathlib import Path
from time import sleep

LOCATIONS = {
    "jawa_timur": "2000011",
    "jawa_barat": "2000009",
    "jakarta_dki": "2000007",
    "banten": "2000004",
}

BASE_URL = "https://www.olx.co.id/api/relevance/v4/search"
HEADERS_FILE = "headers.txt"
OUTPUT_DIR = Path("hasil_scraping")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_headers(path):
    headers = {}
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]

    key = None
    for line in lines:
        if not line:
            continue
        if key is None:
            key = line.strip().lower()
        else:
            headers[key] = line.strip()
            key = None

    for k in list(headers.keys()):
        if k.startswith(":"):
            headers.pop(k)

    print(f"{len(headers)} header berhasil dimuat dari {path}")
    return headers


def scrape_olx_province(province, location_id, headers):
    all_ads = []
    page_num = 1

    print(f"\nMemproses provinsi: {province}")

    while True:
        try:
            url = (
                f"{BASE_URL}?category=5158&facet_limit=100&location={location_id}"
                f"&page={page_num}&platform=web-desktop"
            )
            res = requests.get(url, headers=headers, timeout=45)
            res.raise_for_status()
            data = res.json()

            ads = data.get("data", []) if isinstance(data, dict) else []

            if not ads:
                print(f"     Tidak ada data di halaman {page_num}")
                break

            print(f"     {len(ads)} iklan diambil dari halaman {page_num}")
            all_ads.extend(ads)

            if len(ads) < 20:
                print(f"     Halaman {page_num} kemungkinan terakhir.")
                break

            page_num += 1
            sleep(0.5)

        except Exception as e:
            print(f"     Error halaman {page_num}: {e}")
            break

    output_path = OUTPUT_DIR / f"olx_{province}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_ads, f, ensure_ascii=False, indent=2)

    print(f"Selesai: {province}, total iklan: {len(all_ads)}")
    return all_ads


def main():
    headers = load_headers(HEADERS_FILE)
    total_all = 0

    for prov, loc_id in LOCATIONS.items():
        ads = scrape_olx_province(prov, loc_id, headers)
        total_all += len(ads)

    print("\nSemua provinsi selesai diekstraksi!")
    print(f"Total keseluruhan iklan: {total_all}")


if __name__ == "__main__":
    main()
