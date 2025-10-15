import requests
import json
import time

LOCATIONS = {
    "jawa_timur": "2000011",
    "jawa_barat": "2000009",
    "jakarta_dki": "2000007",
    "banten": "2000004",
}

MAX_PAGES = 3
BASE_API = "https://www.olx.co.id/api/relevance/v4/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.117 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.olx.co.id/",
}


def scrape_olx_api():
    all_data = {}

    for province, loc_id in LOCATIONS.items():
        province_data = {}
        print(f"🔹 Memproses provinsi: {province}")

        for page_num in range(1, MAX_PAGES + 1):
            params = {
                "facet_limit": 100,
                "location": loc_id,
                "category": "5158",  # rumah & apartemen
                "page": page_num,
                "limit": 50,
            }

            try:
                resp = requests.get(
                    BASE_API, params=params, headers=HEADERS, timeout=30
                )
                resp.raise_for_status()
                data = resp.json()

                # pastikan ada hasil
                elements = data.get("data", {}).get("ad", [])
                if elements:
                    province_data[f"page_{page_num}"] = elements
                    print(
                        f"     ✅ {len(elements)} iklan diambil dari halaman {page_num}"
                    )
                else:
                    print(f"     ⚠️ Tidak ada data di halaman {page_num}")

                time.sleep(2)

            except Exception as e:
                print(f"     ⚠️ Error halaman {page_num}: {e}")

        filename = f"olx_{province}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(province_data, f, ensure_ascii=False, indent=2)
        all_data[province] = province_data
        print(f"✅ Selesai: {province}, total halaman: {len(province_data)}\n")

    print("🎉 Semua provinsi selesai diekstraksi!")
    return all_data


if __name__ == "__main__":
    scrape_olx_api()
