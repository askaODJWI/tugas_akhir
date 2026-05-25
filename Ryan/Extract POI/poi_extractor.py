import pandas as pd
import requests
import time
import random
import os
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "..", "Scraping Iklan", "dataset_properti.csv")
CHECKPOINT_FILE = os.path.join(BASE_DIR, "poi_progress_checkpoint.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "dataset_properti_with_poi.csv")

RADIUS_METER = 1250

CATEGORIES_COUNT = [
    "POI_Pendidikan",
    "POI_Kesehatan_Kebugaran",
    "POI_Transportasi",
    "POI_Perbelanjaan",
    "POI_Olahraga_Rekreasi",
    "POI_Tempat_Ibadah",
    "POI_Makanan_Minuman",
    "POI_Fasilitas_Keuangan",
]

CATEGORIES_DETAIL = [f"Detail_{cat}" for cat in CATEGORIES_COUNT]


def kuesioner_kategori_poi(tags):
    amenity = tags.get("amenity", "")
    shop = tags.get("shop", "")
    highway = tags.get("highway", "")
    leisure = tags.get("leisure", "")
    railway = tags.get("railway", "")
    aeroway = tags.get("aeroway", "")

    if amenity in ["school", "university", "kindergarten", "college", "library"]:
        return "POI_Pendidikan"
    elif amenity in ["hospital", "clinic", "pharmacy", "doctors", "dentist"]:
        return "POI_Kesehatan_Kebugaran"
    elif (
        amenity == "bus_station"
        or highway == "bus_stop"
        or railway in ["station", "halt", "subway_entrance"]
        or aeroway == "aerodrome"
    ):
        return "POI_Transportasi"
    elif shop != "" or amenity == "market":
        return "POI_Perbelanjaan"
    elif leisure in [
        "park",
        "sports_centre",
        "fitness_centre",
        "playground",
        "stadium",
        "pitch",
    ]:
        return "POI_Olahraga_Rekreasi"
    elif amenity == "place_of_worship":
        return "POI_Tempat_Ibadah"
    elif amenity in ["restaurant", "cafe", "fast_food", "food_court", "bar"]:
        return "POI_Makanan_Minuman"
    elif amenity in ["bank", "atm"]:
        return "POI_Fasilitas_Keuangan"

    return None


def fetch_poi_data(lat, lon, max_retries=3):
    overpass_url = "https://overpass-api.de/api/interpreter"
    headers = {
        "User-Agent": "Riset_TA_Sistem_Rekomendasi_ITS_5026221087/2.0 (ryanrajata@gmail.com)",
        "Referer": "http://localhost/",
        "Accept": "application/json",
    }

    query = f"""
    [out:json][timeout:60];
    (
      node(around:{RADIUS_METER},{lat},{lon})["amenity"];
      node(around:{RADIUS_METER},{lat},{lon})["shop"];
      node(around:{RADIUS_METER},{lat},{lon})["highway"];
      node(around:{RADIUS_METER},{lat},{lon})["leisure"];
      node(around:{RADIUS_METER},{lat},{lon})["railway"];
      node(around:{RADIUS_METER},{lat},{lon})["aeroway"];
      way(around:{RADIUS_METER},{lat},{lon})["amenity"];
      way(around:{RADIUS_METER},{lat},{lon})["shop"];
      way(around:{RADIUS_METER},{lat},{lon})["highway"];
      way(around:{RADIUS_METER},{lat},{lon})["leisure"];
      way(around:{RADIUS_METER},{lat},{lon})["railway"];
      way(around:{RADIUS_METER},{lat},{lon})["aeroway"];
    );
    out tags center;
    """

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(
                overpass_url, data={"data": query}, headers=headers, timeout=70
            )
            if response.status_code == 200:
                return response.json().get("elements", []), True
            elif response.status_code == 429:
                print(
                    f"      -> [429 Rate Limit] Server OSM sibuk. Sleeping 30 detik..."
                )
                time.sleep(30)
            else:
                print(f"      -> Error HTTP {response.status_code}. Mencoba kembali...")
        except requests.exceptions.RequestException as e:
            print(f"      -> Kendala koneksi jaringan: {e}")
        time.sleep(5)
    return [], False


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File input tidak ditemukan di path: {os.path.abspath(INPUT_FILE)}")
        return

    df_properti = pd.read_csv(INPUT_FILE)
    df_coords = (
        df_properti[["Latitude", "Longitude"]].drop_duplicates().reset_index(drop=True)
    )

    processed_coords = set()
    file_exists = os.path.isfile(CHECKPOINT_FILE)

    if file_exists:
        with open(CHECKPOINT_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                processed_coords.add(f"{row['Latitude']},{row['Longitude']}")

    print(
        f"Mengekstrak fitur Semantik & Densitas POI untuk {len(df_coords)} koordinat unik..."
    )

    with open(CHECKPOINT_FILE, mode="a", newline="", encoding="utf-8") as f:
        header = ["Latitude", "Longitude"] + CATEGORIES_COUNT + CATEGORIES_DETAIL
        writer = csv.DictWriter(f, fieldnames=header)

        if not file_exists or os.stat(CHECKPOINT_FILE).st_size == 0:
            writer.writeheader()

        for idx, row in df_coords.iterrows():
            lat, lon = row["Latitude"], row["Longitude"]
            coord_key = f"{lat},{lon}"

            if coord_key in processed_coords:
                continue

            print(f"[{idx+1}/{len(df_coords)}] Mengekstrak koordinat ({lat}, {lon})...")
            elements, success = fetch_poi_data(lat, lon)

            if success:
                counts = {cat: 0 for cat in CATEGORIES_COUNT}
                names = {cat: set() for cat in CATEGORIES_COUNT}

                for element in elements:
                    tags = element.get("tags", {})
                    category = kuesioner_kategori_poi(tags)
                    if category:
                        counts[category] += 1
                        poi_name = tags.get("name", "").strip()
                        if poi_name:
                            names[category].add(poi_name)

                result_row = {"Latitude": lat, "Longitude": lon}
                result_row.update(counts)

                for cat in CATEGORIES_COUNT:
                    detail_key = f"Detail_{cat}"
                    result_row[detail_key] = ", ".join(sorted(names[cat]))

                writer.writerow(result_row)
                f.flush()

                processed_coords.add(coord_key)
                print(
                    f"      -> Ditemukan {sum(counts.values())} POI. Semantic Text berhasil ditarik."
                )
            else:
                print(f"      -> Melewati koordinat ini setelah beberapa kali gagal.")

            time.sleep(random.uniform(2.0, 4.0))

    # Merge ke Dataset Utama
    df_poi_results = pd.read_csv(CHECKPOINT_FILE)
    df_final = pd.merge(
        df_properti, df_poi_results, on=["Latitude", "Longitude"], how="left"
    )
    df_final[CATEGORIES_COUNT] = df_final[CATEGORIES_COUNT].fillna(0).astype(int)
    df_final[CATEGORIES_DETAIL] = df_final[CATEGORIES_DETAIL].fillna("")

    df_final.to_csv(OUTPUT_FILE, index=False)
    print(f"\nProses Selesai. Cek file di: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
