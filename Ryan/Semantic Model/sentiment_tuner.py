import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "dataset_properti_final.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "dataset_properti_tuned.csv")

POSITIVE_LEXICON = [
    "bebas banjir",
    "bebas dari banjir",
    "tidak banjir",
    "strategis",
    "sangat strategis",
    "super strategis",
    "lokasi strategis",
    "akses strategis",
    "lokasi prime",
    "lokasi prima",
    "kawasan prima",
    "kawasan prime",
    "mewah",
    "luxury",
    "premium",
    "gres",
    "gress",
    "brand new",
    "rumah baru",
    "apartemen baru",
    "bangunan baru",
    "asri",
    "lingkungan asri",
    "terawat",
    "lingkungan terawat",
    "lingkungan aman",
    "full furnish",
    "full furnished",
    "fully furnish",
    "fully furnished",
    "high quality furnished",
    "tidak macet",
    "bebas macet",
    "cuan",
    "baru renov",
    "baru renovasi",
    "baru direnov",
    "baru direnovasi",
    "sudah renov",
    "sudah renovasi",
    "sudah direnov",
    "sudah direnovasi",
    "full renov",
    "full renovasi",
    "tanpa perlu renov",
    "tanpa perlu renovasi",
    "tidak perlu renov",
    "tidak perlu renovasi",
    "tdk perlu renovasi",
    "tidak sengketa",
    "tidak dalam sengketa",
    "tidak bocor",
    "anti bocor",
    "jalan lebar",
    "jalanan lebar",
    "rindang",
    "lingkungan rindang",
    "siap huni",
    "akses mobil",
]

NEGATIVE_LEXICON = [
    "butuh renov",
    "butuh renovasi",
    "perlu renov",
    "perlu renovasi",
    "perlu perbaikan",
    "perlukan renov",
    "perlukan renovasi",
    "perlukan perbaikan",
    "hitung tanah",
    "jual lahan",
    "jual tanah kosong",
    "rusak",
    "retak",
    "retakan",
    "atap jebol",
    "tembok jebol",
    "plafon jebol",
    "atap bocor",
    "plafon bocor",
    "tambal",
    "tambalan",
    "tambal sulam",
    "sengketa",
    "lahan sengketa",
    "tanah sengketa",
    "sengketa lahan",
    "sengketa tanah",
    "rawan",
    "rawan banjir",
    "rentan",
    "rentan banjir",
    "rumah tua",
    "bangunan tua",
    "apartemen tua",
    "terbengkalai",
    "usang",
    "jual rugi",
]

SORTED_POS_LEXICON = sorted(POSITIVE_LEXICON, key=len, reverse=True)
SORTED_NEG_LEXICON = sorted(NEGATIVE_LEXICON, key=len, reverse=True)


def apply_error_correction(row):
    text = str(row["Deskripsi"]).lower()
    bert_score = row["Skor_Sentimen"]

    has_positive = False

    for pos_word in SORTED_POS_LEXICON:
        if re.search(rf"\b{pos_word}\b", text):
            has_positive = True
            text = re.sub(rf"\b{pos_word}\b", " [POS] ", text)

    for neg_word in SORTED_NEG_LEXICON:
        if re.search(rf"\b{neg_word}\b", text):
            return 1

    if has_positive:
        return 5

    if bert_score == 1:
        return 3

    return bert_score


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} tidak ditemukan!")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Memuat {len(df)} baris data...")

    df["Skor_Sentimen"] = df.apply(apply_error_correction, axis=1)

    # Hitung distribusi
    distribusi = df["Skor_Sentimen"].value_counts().to_dict()
    print(f" - Positif (Skor 5) : {distribusi.get(5, 0)} iklan")
    print(f" - Netral  (Skor 3) : {distribusi.get(3, 0)} iklan")
    print(f" - Negatif (Skor 1) : {distribusi.get(1, 0)} iklan")

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nProses selesai. Cek file {os.path.basename(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()
