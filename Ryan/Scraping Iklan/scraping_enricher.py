import csv
import os
import time
import random
import re
from playwright.sync_api import sync_playwright


def enrich_lamudi_data(input_filename, output_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_filename)
    output_path = os.path.join(script_dir, output_filename)

    debug_dir = os.path.join(script_dir, "debug_check")
    os.makedirs(debug_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"[ERROR] File {input_filename} tidak ditemukan.")
        return

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        new_cols = [
            "Fasilitas_Indoor",
            "Karakteristik_bangunan",
            "Kelurahan/desa",
            "Kamar_Mandi_Tamu",
            "Sertifikat",
            "Daya_Listrik (Watt)",
            "Arah_Hadap",
        ]
        for col in new_cols:
            if col not in fieldnames:
                fieldnames.append(col)

        rows = list(reader)

    print(f"Total data yang akan diproses: {len(rows)} baris.")

    # Fungsi Bantuan Konversi Fractions to Decimal
    def parse_lantai(val_str):
        if not val_str:
            return None
        val_str = val_str.strip().replace(",", ".")

        fractions = {"½": 0.5, "¼": 0.25, "¾": 0.75}
        for frac, f_val in fractions.items():
            if frac in val_str:
                base = val_str.replace(frac, "").strip()
                if base.isdigit():
                    return str(float(base) + f_val)
                else:
                    return str(f_val)

        if "/" in val_str:
            parts = val_str.split()
            try:
                if len(parts) == 2:
                    base = float(parts[0])
                    num, den = parts[1].split("/")
                    return str(base + float(num) / float(den))
                elif len(parts) == 1:
                    num, den = parts[0].split("/")
                    return str(float(num) / float(den))
            except Exception:
                return val_str

        return val_str

    with open(output_path, mode="w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                permissions=[],
            )
            page = context.new_page()

            for index, row in enumerate(rows):
                url = row.get("parameter-external_source_url", "").strip()
                desc = row.get("description", "")
                tipe_properti = row.get("Tipe", "").strip().lower()

                row["Fasilitas_Indoor"] = row.get("Fasilitas_Indoor", "")
                row["Karakteristik_bangunan"] = row.get("Karakteristik_bangunan", "")
                row["Kelurahan/desa"] = row.get("Kelurahan/desa", "")
                row["Kamar_Mandi_Tamu"] = ""

                # Imputasi Luas Bangunan
                lb_str = row.get("Luas_bangunan", "").strip()

                try:
                    lb_val = float(lb_str) if lb_str else 0.0
                except ValueError:
                    lb_val = 0.0

                if lb_val == 0.0:
                    pattern_lb = r"(?i)\b(?:luas\s+bangunan|lb)\s*[:\-+~=]*\s*(\d+(?:\.\d{3})*(?:[.,]\d+)?)"
                    match_lb = re.search(pattern_lb, desc)

                    if match_lb:
                        raw_lb = match_lb.group(1).replace(".", "").replace(",", ".")
                        row["Luas_bangunan"] = raw_lb
                        lb_str = raw_lb

                # Imputasi Luas Tanah
                lt_str = row.get("Luas_tanah", "").strip()

                try:
                    lt_val = float(lt_str) if lt_str else 0.0
                except ValueError:
                    lt_val = 0.0

                if lt_val == 0.0 and tipe_properti == "rumah":
                    row["Luas_tanah"] = lb_str

                # Imputasi Data Lantai
                lantai_value = row.get("Lantai", "").strip()

                if not lantai_value:
                    raw_lantai = None

                    number_pattern = r"\d+[ \t]+\d+/\d+|\d*[½¼¾]|\d+(?:[.,]\d+)?"

                    pattern_high = rf"(?i)(?<!\w)({number_pattern})[ \t]*(?:lantai|tingkat)\b|\b(?:lantai|tingkat)[ \t]*[:\-]?[ \t]*({number_pattern})"
                    match_high = re.search(pattern_high, desc)

                    if match_high:
                        val = match_high.group(1) or match_high.group(2)
                        raw_lantai = parse_lantai(val)
                    else:
                        pattern_low = rf"(?i)(?<!\d[.,])(?<![xX\*\-][ \t])(?<![xX\*\-])({number_pattern})[ \t]*lt\b|\blt[ \t]*[:\-]?[ \t]*({number_pattern})(?![ \t]*[xX\*])"
                        matches_low = re.findall(pattern_low, desc)

                        for m in matches_low:
                            val = m[0] or m[1]
                            try:
                                parsed_val = parse_lantai(val)
                                val_float = float(parsed_val)
                                if (
                                    lt_val is not None and val_float == lt_val
                                ) or val_float > 10:
                                    continue
                                else:
                                    raw_lantai = parsed_val
                                    break
                            except ValueError:
                                continue

                    if raw_lantai:
                        row["Lantai"] = raw_lantai
                    else:
                        row["Lantai"] = "1.0"

                # Ekstraksi Sertifikat
                cert_matches = re.findall(
                    r"(?i)\b(SHM|HGB|SHGB|SHMSRS|PPJB|Petok\s*D|Strata\s*Title|Hak\s*Milik|IMB|AJB|PBG|BPHTB|BBN|PPh)\b",
                    desc,
                )
                if cert_matches:
                    unique_certs = sorted(list(set([c.upper() for c in cert_matches])))
                    row["Sertifikat"] = ", ".join(unique_certs)
                else:
                    row["Sertifikat"] = ""

                # Ekstraksi Daya Listrik
                listrik_pattern = r"(?i)(?:(?:pln|listrik)\s*[:\-]?\s*)?(\d{1,2}(?:\.\d{3})|\d{3,5})\s*(?:watt|watts|w|va)\b|\b(?:pln|listrik)\s*[:\-]?\s*(\d{1,2}(?:\.\d{3})|\d{3,5})\b"

                listrik_matches = re.findall(listrik_pattern, desc)

                if listrik_matches:
                    extracted_listrik = []
                    for m in listrik_matches:
                        raw_listrik = m[0] or m[1]
                        extracted_listrik.append(raw_listrik.replace(".", ""))

                    unique_listrik = list(dict.fromkeys(extracted_listrik))
                    row["Daya_Listrik (Watt)"] = " + ".join(unique_listrik)
                else:
                    row["Daya_Listrik (Watt)"] = ""

                # Ekstraksi Arah Hadap
                arah_pattern_nc = r"(?:barat\s*daya|barat\s*laut|timur\s*laut|tenggara|utara|selatan|timur|barat)"
                arah_pattern = r"\b(barat\s*daya|barat\s*laut|timur\s*laut|tenggara|utara|selatan|timur|barat)\b"

                hadap_match = re.search(
                    r"(?i)\b(?:hadap|arah|menghadap|posisi|hook)\b\s*[:\-\(]?\s*((?:"
                    + arah_pattern_nc
                    + r"\s*(?:dan|&|/|\-|,|\))?\s*)+)",
                    desc,
                )

                if hadap_match:
                    found_dirs = re.findall(
                        r"(?i)" + arah_pattern, hadap_match.group(1)
                    )
                else:
                    safe_desc = re.sub(
                        r"(?i)\b(surabaya|jakarta|sidoarjo|bogor|depok|tangerang|bekasi|jawa|dki|banten|jl\.?|jalan|raya|desa|kelurahan|kecamatan|semolowaru|kota|kabupaten|provinsi)\s+(utara|selatan|timur|barat|pusat)\b",
                        "",
                        desc,
                    )
                    found_dirs = re.findall(r"(?i)" + arah_pattern, safe_desc)

                if found_dirs:
                    unique_dirs = sorted(
                        list(set([re.sub(r"\s+", " ", d.title()) for d in found_dirs]))
                    )
                    row["Arah_Hadap"] = ", ".join(unique_dirs)
                else:
                    row["Arah_Hadap"] = ""

                if url and "lamudi.co.id" in url:
                    print(
                        f"[{index+1}/{len(rows)}] Mengunjungi Lamudi: {row['title'][:30]}..."
                    )
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)

                        page.evaluate("""
                            const scrollInterval = setInterval(() => {
                                window.scrollBy(0, 300);
                            }, 500);
                            setTimeout(() => clearInterval(scrollInterval), 5000);
                        """)
                        time.sleep(6)

                        # Ekstraksi Lokasi Tambahan
                        try:
                            page.wait_for_selector("#view-map__text", timeout=5000)
                            location_text = page.locator("#view-map__text").inner_text()

                            if location_text:
                                parts = [p.strip() for p in location_text.split(",")]
                                if len(parts) >= 3:
                                    row["Kecamatan"] = parts[-3]
                                if len(parts) >= 4:
                                    row["Kelurahan/desa"] = parts[-4]
                        except Exception:
                            pass

                        # Ekstraksi Kamar Mandi Tamu
                        kamar_mandi_tamu = page.evaluate("""() => {
                            let el = document.querySelector('[data-test="half-bathrooms-value"]');
                            if (el && el.innerText) {
                                let match = el.innerText.match(/\\d+/);
                                return match ? match[0] : "";
                            }
                            return "";
                        }""")
                        if kamar_mandi_tamu:
                            row["Kamar_Mandi_Tamu"] = kamar_mandi_tamu

                        # Ekstraksi Fasilitas
                        indoor_elements = page.evaluate("""() => {
                            let items = document.querySelectorAll("#facilities__options .facilities__item");
                            if (items.length === 0) items = document.querySelectorAll("#facilities__options li");
                            let textArray = Array.from(items).map(el => el.innerText.replace(/\\n/g, ' ').trim()).filter(t => t.length > 0);
                            return [...new Set(textArray)];
                        }""")
                        if indoor_elements:
                            row["Fasilitas_Indoor"] = ", ".join(indoor_elements)

                        building_elements = page.evaluate("""() => {
                            let items = document.querySelectorAll("#facilities__options-building .facilities__item");
                            if (items.length === 0) items = document.querySelectorAll("#facilities__options-building li");
                            let textArray = Array.from(items).map(el => el.innerText.replace(/\\n/g, ' ').trim()).filter(t => t.length > 0);
                            return [...new Set(textArray)];
                        }""")
                        if building_elements:
                            row["Karakteristik_bangunan"] = ", ".join(building_elements)

                    except Exception as e:
                        print(f"   -> [ERROR] Gagal memproses URL: {e}")

                    time.sleep(random.uniform(2.5, 5.0))
                else:
                    print(f"[{index+1}/{len(rows)}] Dilewati (Bukan link Lamudi)")

                writer.writerow(row)

            browser.close()
            print(f"\n[SELESAI] Cek file {output_filename}")


if __name__ == "__main__":
    enrich_lamudi_data("pilot_testing.csv", "pilot_testing_enriched.csv")
