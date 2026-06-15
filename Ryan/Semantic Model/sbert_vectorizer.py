import pandas as pd
import numpy as np
import os
import time
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(
    BASE_DIR, "..", "POI Extraction", "dataset_properti_with_poi.csv"
)
OUTPUT_CSV = os.path.join(BASE_DIR, "dataset_properti_corpus.csv")
OUTPUT_NPY = os.path.join(BASE_DIR, "semantic_embeddings.npy")

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


def main():
    df = pd.read_csv(INPUT_FILE)

    poi_columns = [
        "Detail_POI_Pendidikan",
        "Detail_POI_Kesehatan_Kebugaran",
        "Detail_POI_Transportasi",
        "Detail_POI_Perbelanjaan",
        "Detail_POI_Olahraga_Rekreasi",
        "Detail_POI_Tempat_Ibadah",
        "Detail_POI_Makanan_Minuman",
        "Detail_POI_Fasilitas_Keuangan",
        "Detail_POI_Lainnya",
    ]

    def build_corpus(row):
        parts = []
        if pd.notna(row["Judul"]):
            parts.append(str(row["Judul"]))
        if pd.notna(row["Deskripsi"]):
            parts.append(str(row["Deskripsi"]))
        if pd.notna(row["Fasilitas"]):
            parts.append("Fasilitas internal: " + str(row["Fasilitas"]))

        poi_texts = []
        for col in poi_columns:
            if pd.notna(row[col]) and str(row[col]).strip() != "":
                nama_kategori = col.replace("Detail_POI_", "").replace("_", " ")
                poi_texts.append(f"{nama_kategori} terdekat yaitu {str(row[col])}")

        if poi_texts:
            parts.append("Fasilitas lingkungan sekitar: " + "; ".join(poi_texts))

        return ". ".join(parts)

    start_time = time.time()
    df["Korpus_Properti"] = df.apply(build_corpus, axis=1)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Proses konstruksi korpus selesai. Cek file {os.path.basename(OUTPUT_CSV)}")

    model = SentenceTransformer(MODEL_NAME)

    corpus_list = df["Korpus_Properti"].tolist()

    embeddings = model.encode(
        corpus_list, show_progress_bar=True, convert_to_numpy=True
    )
    np.save(OUTPUT_NPY, embeddings)

    end_time = time.time()
    print(f"\nDimensi Matriks SBERT: {embeddings.shape}")
    print(f"Vektorisasi selesai dalam {round(end_time - start_time, 2)} detik.")
    print(f"Proses vektorisasi selesai. Cek file {os.path.basename(OUTPUT_NPY)}")


if __name__ == "__main__":
    main()
