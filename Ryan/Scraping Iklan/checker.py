import csv
import os
import time
import random
from playwright.sync_api import sync_playwright


def enrich_lamudi_data(input_filename, output_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, input_filename)
    output_path = os.path.join(script_dir, output_filename)

    debug_dir = os.path.join(script_dir, "debug_screenshots")
    os.makedirs(debug_dir, exist_ok=True)

    if not os.path.exists(input_path):
        print(f"[ERROR] File {input_filename} tidak ditemukan.")
        return

    with open(input_path, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if "Fasilitas_Indoor" not in fieldnames:
            fieldnames += ["Fasilitas_Indoor", "Karakteristik_bangunan"]
        rows = list(reader)

    print(f"Total data yang akan diproses: {len(rows)} baris.")

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
                row["Fasilitas_Indoor"] = ""
                row["Karakteristik_bangunan"] = ""

                if url and "lamudi.co.id" in url:
                    print(
                        f"[{index+1}/{len(rows)}] Mengunjungi Lamudi: {row['title'][:30]}..."
                    )
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=60000)

                        # PERBAIKAN 1: Smooth Scroll perlahan ke bawah untuk memicu Lazy Load
                        page.evaluate(
                            """
                            const scrollInterval = setInterval(() => {
                                window.scrollBy(0, 300);
                            }, 500);
                            setTimeout(() => clearInterval(scrollInterval), 5000);
                        """
                        )
                        time.sleep(6)  # Tunggu proses smooth scroll selesai

                        # PERBAIKAN 2: Explicit Wait. Tunggu maksimal 8 detik sampai container fasilitas muncul di HTML.
                        try:
                            page.wait_for_selector(".facilities", timeout=8000)
                        except Exception:
                            print(
                                "   -> [INFO] Timeout: Elemen '.facilities' lambat/tidak muncul."
                            )

                        # Ekstraksi dengan selector yang lebih tahan banting (mencari div yang id-nya mengandung kata tersebut)
                        indoor_elements = page.evaluate(
                            """() => {
                            let items = document.querySelectorAll("[id*='facilities_options'] .facilities_item, [id*='facilities_options'] li");
                            // Filter keluar yang masuk kategori building
                            let indoorItems = Array.from(items).filter(el => !el.closest('[id*="building"]'));
                            return indoorItems.map(el => el.innerText.replace(/\\n/g, ' ').trim()).filter(txt => txt.length > 0);
                        }"""
                        )

                        if indoor_elements:
                            row["Fasilitas_Indoor"] = ", ".join(indoor_elements)

                        building_elements = page.evaluate(
                            """() => {
                            let items = document.querySelectorAll("[id*='facilities_options-building'] .facilities_item, [id*='facilities_options-building'] li");
                            return Array.from(items).map(el => el.innerText.replace(/\\n/g, ' ').trim()).filter(txt => txt.length > 0);
                        }"""
                        )

                        if building_elements:
                            row["Karakteristik_bangunan"] = ", ".join(building_elements)

                        print(
                            f"   -> Sukses! Indoor: {len(indoor_elements)} item | Bangunan: {len(building_elements)} item"
                        )

                        # PERBAIKAN 3: HTML State Dumping
                        if len(indoor_elements) == 0 and len(building_elements) == 0:
                            debug_pic = os.path.join(
                                debug_dir, f"debug_lamudi_{index+1}.png"
                            )
                            debug_html = os.path.join(
                                debug_dir, f"debug_lamudi_{index+1}.html"
                            )  # Simpan HTML

                            page.screenshot(path=debug_pic)
                            with open(debug_html, "w", encoding="utf-8") as f:
                                f.write(
                                    page.content()
                                )  # Simpan apa yang sebenarnya dilihat bot di level kode

                            print(
                                f"   -> [DEBUG] Item kosong. Gambar & File HTML disimpan di folder: {debug_dir}"
                            )

                    except Exception as e:
                        print(f"   -> [ERROR] Gagal memproses URL: {e}")

                    time.sleep(random.uniform(2.5, 5.0))
                else:
                    print(
                        f"[{index+1}/{len(rows)}] Dilewati (Tidak ada link Lamudi valid)"
                    )

                writer.writerow(row)

            browser.close()
            print(f"\n[SELESAI] Data berhasil disimpan ke {output_filename}")


if __name__ == "__main__":
    enrich_lamudi_data("pilot_testing.csv", "pilot_testing_checker.csv")
