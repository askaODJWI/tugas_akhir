import re
import json
import requests
from pathlib import Path
from time import sleep

try:
    import pandas as pd
except Exception as e:
    pd = None

HEADERS_FILE = "headers.txt"
EXCEL_FILE = "city_url_list.xlsx"
URL_COL_NAME = "city_url"
OUTPUT_DIR = Path("hasil_scraping")
JSON_DIR = OUTPUT_DIR / "per_city_json"
HTML_DUMPS = OUTPUT_DIR / "html_dumps"
OUTPUT_DIR.mkdir(exist_ok=True)
JSON_DIR.mkdir(exist_ok=True)
HTML_DUMPS.mkdir(exist_ok=True)

BASE_URL = "https://www.olx.co.id/api/relevance/v4/search"
CATEGORY = "5158"  # kategori rumah/apartemen
PAGE_SIZE = 20
SAFE_PAGE_LIMIT = 25  # batas kalau server memotong pagination
SLEEP_BETWEEN_REQS = 0.4


def load_headers(path):
    headers = {}
    with open(path, "r", encoding="utf-8") as f:
        lines = [l.rstrip("\n") for l in f.readlines()]
    key = None
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if key is None:
            key = s.lower()
        else:
            headers[key] = s
            key = None
    # buang pseudo-headers yang dimulai dengan ':'
    for k in list(headers.keys()):
        if k.startswith(":"):
            headers.pop(k)
    print(f"{len(headers)} header berhasil dimuat dari {path}")
    return headers


def extract_location_id_from_url(url):
    """
    Cari pattern _g<digits> di URL (contoh: /surabaya-kota_g4000216/).
    Kembalikan id sebagai string atau None.
    """
    if not url or not isinstance(url, str):
        return None
    m = re.search(r"_g(\d+)", url)
    return m.group(1) if m else None


def fetch_page_for_location(headers, location_id, page_num, platform="web-desktop"):
    params = {
        "category": CATEGORY,
        "facet_limit": 100,
        "location": location_id,
        "page": page_num,
        "platform": platform,
    }
    res = requests.get(BASE_URL, headers=headers, params=params, timeout=45)
    res.raise_for_status()
    return res


def scrape_city(headers, city_name, url, max_pages=1000):
    loc_id = extract_location_id_from_url(url)
    if not loc_id:
        print(f"   Gagal ekstrak location id dari URL: {url}")
        return [], False

    print(f"\n   Memproses kota: {city_name} -> {url} (loc_id={loc_id})")
    all_ads = []
    page = 1
    needs_split = False

    while True:
        try:
            res = fetch_page_for_location(headers, loc_id, page)
            # jika response text HTML (bukan JSON), simpan dump untuk analisa
            ct = res.headers.get("Content-Type", "")
            if "application/json" not in ct:
                dump_path = (
                    HTML_DUMPS / f"{city_name.replace(' ', '_')}_page{page}_raw.html"
                )
                with open(dump_path, "wb") as f:
                    f.write(res.content)
                print(f"      Response bukan JSON, saved HTML: {dump_path}")
                break

            data = res.json()
            ads = data.get("data", []) if isinstance(data, dict) else []

            if not ads:
                print(f"      Tidak ada data di halaman {page}")
                break

            print(f"      {len(ads)} iklan diambil dari halaman {page}")
            all_ads.extend(ads)

            # deteksi akhir : jika kurang dari satu page penuh
            if len(ads) < PAGE_SIZE:
                print(f"      Halaman {page} kemungkinan terakhir.")
                break

            page += 1
            if page > SAFE_PAGE_LIMIT:
                # kemungkinan API memang membatasi depth per query
                print(
                    f"      Mencapai SAFE_PAGE_LIMIT ({SAFE_PAGE_LIMIT}) pada kota ini — perlu dipecah (location sub, price/time)."
                )
                needs_split = True
                break

            if page > max_pages:
                print(f"      Mencapai batas max_pages ({max_pages}). Stop.")
                break

            sleep(SLEEP_BETWEEN_REQS)

        except requests.exceptions.RequestException as rexc:
            print(f"      Request error pada halaman {page}: {rexc}")
            # simpan HTML/response jika ada
            try:
                dump_path = (
                    HTML_DUMPS / f"{city_name.replace(' ', '_')}_page{page}_err.html"
                )
                with open(dump_path, "wb") as f:
                    f.write(
                        rexc.response.content
                        if getattr(rexc, "response", None) is not None
                        else b""
                    )
                print(f"      Saved failing HTML to: {dump_path}")
            except Exception:
                pass
            break
        except Exception as exc:
            print(f"      Error halaman {page}: {exc}")
            break

    # simpan hasil per-kota
    out_path = JSON_DIR / f"olx_{city_name.replace(' ', '_')}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_ads, f, ensure_ascii=False, indent=2)

    print(f"   Selesai: {city_name}, total iklan: {len(all_ads)}")
    return all_ads, needs_split


def main():
    if not Path(HEADERS_FILE).exists():
        print(f"File {HEADERS_FILE} tidak ditemukan. Taruh header DevTools di sana.")
        return

    headers = load_headers(HEADERS_FILE)

    if pd is None:
        print(
            "Modul pandas tidak tersedia. Untuk membaca Excel, install openpyxl + pandas:"
        )
        print("   pip install pandas openpyxl")
        return

    if not Path(EXCEL_FILE).exists():
        print(f"File Excel {EXCEL_FILE} tidak ditemukan di folder ini.")
        return

    # baca excel
    try:
        df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
    except Exception as e:
        print("Gagal membaca Excel. Pastikan openpyxl ada dan file benar. Error:", e)
        return

    if URL_COL_NAME not in df.columns:
        print(
            f"Kolom '{URL_COL_NAME}' tidak ketemu di Excel. Kolom tersedia: {list(df.columns)}"
        )
        return

    total_all = 0
    needs_split_list = []

    # iterasi tiap baris di Excel
    for idx, row in df.iterrows():
        url = str(row[URL_COL_NAME]).strip()
        if not url or url.lower() in ("nan", "none"):
            continue
        # buat city name friendly
        city_name = (
            row.get("city", None) or row.get("name", None) or url.split("/")[3]
            if len(url.split("/")) > 3
            else f"city_{idx}"
        )
        city_name = str(city_name).strip()
        ads, needs_split = scrape_city(headers, city_name, url)
        total_all += len(ads)
        if needs_split:
            needs_split_list.append((city_name, url))

    print("\nSemua kota selesai. Total iklan yang dikumpulkan:", total_all)
    if needs_split_list:
        print(
            "Beberapa kota perlu dipecah lebih jauh (contoh: price/date partition). Daftar:"
        )
        for c, u in needs_split_list:
            print("   -", c, "->", u)
    else:
        print("Tidak ada kota yang butuh split lebih lanjut.")


if __name__ == "__main__":
    main()
