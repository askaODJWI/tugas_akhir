import pandas as pd
import numpy as np
import os
import time
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(
    BASE_DIR, "..", "POI Extraction", "dataset_properti_with_poi.csv"
)
OUTPUT_CSV = os.path.join(BASE_DIR, "dataset_properti_corpus.csv")
OUTPUT_EMBEDDING = os.path.join(BASE_DIR, "semantic_embeddings.npy")
OUTPUT_SCALED_POI = os.path.join(BASE_DIR, "scaled_poi_density.npy")

# Model SBERT (Multilingual)
SBERT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


# Corpus Construction
def build_property_corpus(row):
    tipe = str(row.get("Tipe_Properti", "properti")).strip()
    judul = str(row.get("Judul", "")).strip()
    deskripsi = str(row.get("Deskripsi", "")).strip()
    fasilitas = str(row.get("Fasilitas", "")).strip()

    poi_mapping = {
        "pendidikan": "Detail_POI_Pendidikan",
        "kesehatan": "Detail_POI_Kesehatan_Kebugaran",
        "transportasi": "Detail_POI_Transportasi",
        "perbelanjaan": "Detail_POI_Perbelanjaan",
        "olahraga dan rekreasi": "Detail_POI_Olahraga_Rekreasi",
        "tempat ibadah": "Detail_POI_Tempat_Ibadah",
        "makanan dan minuman": "Detail_POI_Makanan_Minuman",
        "fasilitas keuangan": "Detail_POI_Fasilitas_Keuangan",
    }

    poi_texts = []
    for name, col in poi_mapping.items():
        val = str(row.get(col, "")).strip()
        if val and val.lower() != "nan":
            poi_texts.append(f"fasilitas {name} terdekat yaitu {val}")

    corpus_parts = [f"Sebuah {tipe} dengan judul: {judul}."]

    if fasilitas and fasilitas.lower() != "nan":
        corpus_parts.append(f"Fasilitas yang disediakan meliputi: {fasilitas}.")

    if deskripsi and deskripsi.lower() != "nan":
        corpus_parts.append(f"Deskripsi properti: {deskripsi[:1000]}")

    if poi_texts:
        corpus_parts.append(
            "Lingkungan sekitar memiliki akses ke " + "; ".join(poi_texts) + "."
        )

    return " ".join(corpus_parts)


def main():

    if not os.path.exists(INPUT_FILE):
        print(f"File dataset {INPUT_FILE} tidak ditemukan!")
        return

    print("\nMembaca dataset...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Total data: {len(df)} properti.")

    print("\nMembangun korpus naratif untuk setiap properti...")
    df["Korpus_Properti"] = df.apply(build_property_corpus, axis=1)

    print("\nMelakukan normalisasi pada densitas POI...")
    poi_density_cols = [
        "POI_Pendidikan",
        "POI_Kesehatan_Kebugaran",
        "POI_Transportasi",
        "POI_Perbelanjaan",
        "POI_Olahraga_Rekreasi",
        "POI_Tempat_Ibadah",
        "POI_Makanan_Minuman",
        "POI_Fasilitas_Keuangan",
    ]
    scaler = MinMaxScaler()
    scaled_densities = scaler.fit_transform(df[poi_density_cols].fillna(0))

    print(f"\nMemuat model SBERT: {SBERT_MODEL_NAME} ...")
    model = SentenceTransformer(SBERT_MODEL_NAME)

    print("\nMelakukan vektorisasi teks korpus (Embedding Generation)...")
    start_time = time.time()

    embeddings = model.encode(
        df["Korpus_Properti"].tolist(), show_progress_bar=True, convert_to_numpy=True
    )

    end_time = time.time()
    print(f"   Vektorisasi selesai dalam {round(end_time - start_time, 2)} detik.")
    print(f"   Dimensi vektor yang dihasilkan: {embeddings.shape}")

    print("\nMenyimpan hasil...")
    df.to_csv(OUTPUT_CSV, index=False)

    np.save(OUTPUT_EMBEDDING, embeddings)

    np.save(OUTPUT_SCALED_POI, scaled_densities)

    print("File yang dihasilkan:")
    print(f"- Dataset + Korpus : {OUTPUT_CSV}")
    print(f"- Vektor SBERT     : {OUTPUT_EMBEDDING}")
    print(f"- Densitas POI     : {OUTPUT_SCALED_POI}")


if __name__ == "__main__":
    main()
