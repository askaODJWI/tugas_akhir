import json
import time
import random
import csv
import os
from playwright.sync_api import sync_playwright

# ID Lokasi Target
LOCATION_MAP = {
    "Jakarta Selatan": "4000030",
    "Jakarta Timur": "4000031",
    "Jakarta Utara": "4000032",
    "Jakarta Barat": "4000028",
    "Jakarta Pusat": "4000029",
    "Bogor Kab.": "4000004",
    "Bogor Kota": "4000021",
    "Depok Kota": "4000024",
    "Tangerang Selatan Kota": "4000080",
    "Tangerang Kota": "4000079",
    "Tangerang Kab.": "4000076",
    "Bekasi Kota": "4000020",
    "Bekasi Kab.": "4000003",
    "Surabaya Kota": "4000216",
}


def main():
    master_filename = "dataset_properti_raw.csv"

    if os.path.exists(master_filename):
        print(f"Menghapus {master_filename} lama untuk sesi baru...")
        os.remove(master_filename)

    for location_name, location_id in LOCATION_MAP.items():
        print(f"\n>>> Target Lokasi: {location_name} (ID: {location_id})")

        scrape_olx_playwright(
            location_name=location_name,
            location_id=location_id,
            max_pages=50,
            filename=master_filename,
        )

    print("\n=== Scraping Finished ===")
    print(f"Cek file: {master_filename}")


def extract_physical_data(parameters_list):
    """Ekstraksi atribut fisik dari JSON OLX"""
    data = {
        "Luas_bangunan": "",
        "Luas_tanah": "",
        "Kamar_tidur": "",
        "Kamar_Mandi": "",
        "parameter-external_source_url": "",
        "Tipe": "",
        "Fasilitas": "",
        "Lantai": "",
    }

    if not isinstance(parameters_list, list):
        return data

    for p in parameters_list:
        if not isinstance(p, dict):
            continue

        key = p.get("key")
        value = p.get("value")

        if key == "p_sqr_building":
            data["Luas_bangunan"] = value
        elif key == "p_sqr_land":
            data["Luas_tanah"] = value
        elif key == "p_bedroom":
            data["Kamar_tidur"] = value
        elif key == "p_bathroom":
            data["Kamar_Mandi"] = value
        elif key == "external_source_url":
            data["parameter-external_source_url"] = value
        elif key == "type":
            data["Tipe"] = value
        elif key == "p_facility":
            data["Fasilitas"] = p.get("absoluteValue", "")
        elif key == "p_floor":
            data["Lantai"] = value

    return data


def scrape_olx_playwright(location_name, location_id, max_pages, filename):
    fieldnames = [
        "ad_id",
        "title",
        "price",
        "lat",
        "lon",
        "Provinsi",
        "Kota/kabupaten",
        "Kecamatan",
        "Luas_bangunan",
        "Luas_tanah",
        "Kamar_tidur",
        "Kamar_Mandi",
        "parameter-external_source_url",
        "Tipe",
        "Fasilitas",
        "Lantai",
        "description",
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                permissions=[],
            )
            page = context.new_page()

            try:
                page.goto(
                    "https://www.olx.co.id/dijual-rumah-apartemen_c5158",
                    wait_until="domcontentloaded",
                    timeout=60000,
                )
            except Exception as e:
                print(f"  [Peringatan] Gagal memuat halaman utama sempurna: {e}")

            time.sleep(8)

            for page_num in range(1, max_pages + 1):
                print(
                    f"  -> Mengekstrak {location_name} - Halaman {page_num}/{max_pages}..."
                )

                api_url = (
                    f"https://www.olx.co.id/api/relevance/v5/search?"
                    f"category=5158&facet_limit=100&location={location_id}&location_facet_limit=20"
                    f"&page={page_num}&platform=web-mobile&relaxedFilters=true&user=199592abc68x70f96fd4"
                )

                try:
                    page.goto(api_url, wait_until="domcontentloaded", timeout=60000)
                    time.sleep(6)

                    raw_json_text = page.locator("body").inner_text()

                    try:
                        res_json = json.loads(raw_json_text)
                    except json.JSONDecodeError:
                        print(f"  Gagal membaca JSON. Berhenti di halaman ini.")
                        break

                    ads = res_json.get("data", [])
                    if not ads:
                        print(
                            f"  Tidak ada data lagi di halaman {page_num}. Beralih ke kota berikutnya."
                        )
                        break

                    page_data = []
                    for ad in ads:
                        if not isinstance(ad, dict):
                            continue

                        raw_desc = ad.get("description", "")
                        clean_desc = (
                            raw_desc.replace("\n", " ").replace("\r", " ").strip()
                            if raw_desc
                            else ""
                        )

                        # Ekstraksi Koordinat
                        locations_list = ad.get("locations") or []
                        latitude = longitude = ""
                        if locations_list and isinstance(locations_list[0], dict):
                            latitude = locations_list[0].get("lat", "")
                            longitude = locations_list[0].get("lon", "")

                        # Ekstraksi Lokasi Geografis
                        loc_res = ad.get("locations_resolved") or {}
                        provinsi = loc_res.get("ADMIN_LEVEL_1_name", "")
                        kota_kab = loc_res.get("ADMIN_LEVEL_3_name", "")
                        kecamatan = loc_res.get("SUBLOCALITY_LEVEL_1_name", "")

                        # Ekstraksi Harga
                        price_dict = ad.get("price") or {}
                        value_dict = price_dict.get("value") or {}
                        raw_price = value_dict.get("raw", "")

                        item = {
                            "ad_id": ad.get("id", ""),
                            "title": ad.get("title", ""),
                            "price": raw_price,
                            "lat": latitude,
                            "lon": longitude,
                            "Provinsi": provinsi,
                            "Kota/kabupaten": kota_kab,
                            "Kecamatan": kecamatan,
                            "description": clean_desc,
                        }

                        # Ekstraksi Parameter Fisik
                        params_list = ad.get("parameters") or []
                        physical_info = extract_physical_data(params_list)

                        item.update(physical_info)
                        page_data.append(item)

                    writer.writerows(page_data)
                    print(f"     Sukses menyimpan {len(page_data)} iklan.")

                except Exception as e:
                    print(f"  Terjadi kegagalan pada halaman {page_num}: {e}")

                time.sleep(random.uniform(2.0, 4.0))

            browser.close()


if __name__ == "__main__":
    main()
