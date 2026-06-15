import pandas as pd
import os
import time
from transformers import pipeline
from tqdm import tqdm

# Progress bar
tqdm.pandas()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "dataset_properti_corpus.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "dataset_properti_final.csv")

# Model
MODEL_NAME = "mdhugol/indonesia-bert-sentiment-classification"


sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME,
    truncation=True,
    max_length=512,
)


def analyze_and_score_sentiment(text):
    # Handle missing values
    if not isinstance(text, str) or text.strip() == "":
        return 3  # Skor Netral jika deskripsi kosong

    try:
        # Melakukan prediksi
        result = sentiment_pipeline(text)[0]
        label = result["label"]

        # Mapping label (mdhugol --> 1-5)
        if label == "LABEL_2":
            return 5
        elif label == "LABEL_1":
            return 3
        elif label == "LABEL_0":
            return 1
        else:
            return 3

    except Exception as e:
        # Failsafe jika ada error
        return 3


def main():

    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} tidak ditemukan!")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"Total baris yang akan diproses: {len(df)}")

    start_time = time.time()

    df["Skor_Sentimen"] = df["Deskripsi"].progress_apply(analyze_and_score_sentiment)

    end_time = time.time()

    print(f"\nAnalisis Sentimen selesai dalam {round(end_time - start_time, 2)} detik.")

    # Distribusi sentimen
    distribusi = df["Skor_Sentimen"].value_counts().to_dict()
    print("Distribusi Skor Sentimen:")
    print(f" - Positif (Skor 5) : {distribusi.get(5, 0)} iklan")
    print(f" - Netral  (Skor 3) : {distribusi.get(3, 0)} iklan")
    print(f" - Negatif (Skor 1) : {distribusi.get(1, 0)} iklan")

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Proses selesai. Cek file {os.path.basename(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()
