import requests
import json
import time


# Fungsi bantu parsing headers.txt
def load_headers_from_txt(path="headers.txt"):
    """
    Membaca file headers.txt dari DevTools (format dua baris per header),
    mengubahnya menjadi dict siap pakai untuk requests.
    """
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

    # Hapus pseudo-header HTTP/2
    for k in list(headers.keys()):
        if k.startswith(":"):
            headers.pop(k)

    return headers


# Konfigurasi lokasi target
LOCATIONS = {
    "jawa_timur": "2000011",
    "jawa_barat": "2000009",
    "jakarta_dki": "2000007",
    "banten": "2000004",
}

MAX_PAGES = 12
BASE_API = "https://www.olx.co.id/api/relevance/v4/search"


# Fungsi utama scraping
def scrape_olx_api():
    headers = load_headers_from_txt("headers.txt")
    session = requests.Session()
    session.headers.update(headers)

    all_data = {}

    for province, loc_id in LOCATIONS.items():
        province_data = {}
        print(f"🔹 Memproses provinsi: {province}")

        for page_num in range(1, MAX_PAGES + 1):
            params = {
                "category": "5158",
                "location": loc_id,
                "page": page_num,
                "limit": 50,
                "platform": "web-mobile",
            }

            try:
                r = session.get(BASE_API, params=params, timeout=45)
                r.raise_for_status()
                data = r.json()

                # Deteksi semua kemungkinan struktur JSON OLX
                if isinstance(data, list):
                    ads = data
                elif isinstance(data, dict):
                    if isinstance(data.get("data"), list):
                        ads = data["data"]
                    elif isinstance(data.get("data"), dict):
                        ads = data["data"].get("ad", [])
                    else:
                        ads = []
                else:
                    ads = []

                # Cek hasil
                if ads:
                    province_data[f"page_{page_num}"] = ads
                    print(f"     {len(ads)} iklan diambil dari halaman {page_num}")
                else:
                    print(f"     Tidak ada data di halaman {page_num}")

                time.sleep(3)

            except Exception as e:
                print(f"     Error halaman {page_num}: {e}")

        filename = f"olx_{province}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(province_data, f, ensure_ascii=False, indent=2)

        all_data[province] = province_data
        print(f"Selesai: {province}, total halaman: {len(province_data)}\n")

    print("Semua provinsi selesai diekstraksi!")
    return all_data


# Eksekusi
if __name__ == "__main__":
    scrape_olx_api()
