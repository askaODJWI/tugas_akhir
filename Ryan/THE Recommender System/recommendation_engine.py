import pandas as pd
import numpy as np
import os
import time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_FILE = os.path.join(
    BASE_DIR, "..", "Semantic & Sentiment Analysis", "dataset_properti_corpus.csv"
)
EMBEDDING_FILE = os.path.join(
    BASE_DIR, "..", "Semantic & Sentiment Analysis", "semantic_embeddings.npy"
)
SBERT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

df_properti = pd.read_csv(CORPUS_FILE)

embeddings = np.load(EMBEDDING_FILE)

print(f"Memuat model ({SBERT_MODEL_NAME})...")
model = SentenceTransformer(SBERT_MODEL_NAME)


def get_recommendations(positive_query, negative_feedbacks, top_n=5):
    print(f"\n[Menganalisis Pencarian] Kueri: '{positive_query}'")
    if negative_feedbacks:
        print(f"[Menganalisis Penolakan] Menghindari: {negative_feedbacks}")

    start_time = time.time()

    # Vektorisasi Kueri Positif Pengguna
    query_vector = model.encode([positive_query], convert_to_numpy=True)

    # Cosine Similarity
    similarities = cosine_similarity(query_vector, embeddings)[0]

    df_results = df_properti.copy()
    df_results["Similarity_Score"] = similarities

    # Negative Feedback Handling
    if negative_feedbacks:
        for neg_term in negative_feedbacks:
            neg_term_lower = neg_term.lower().strip()

            # Mendeteksi kata negatif pada Korpus_Properti
            mask_contains_negative = (
                df_results["Korpus_Properti"]
                .str.lower()
                .str.contains(neg_term_lower, na=False)
            )

            # Memberikan penalti
            df_results.loc[mask_contains_negative, "Similarity_Score"] -= 1.0
            df_results.loc[mask_contains_negative, "Eliminasi_Karena"] = neg_term

    # Mengurutkan properti berdasarkan skor kemiripan
    df_ranked = df_results.sort_values(by="Similarity_Score", ascending=False).head(
        top_n
    )

    end_time = time.time()
    print(
        f"Rekomendasi selesai diproses dalam {round(end_time - start_time, 3)} detik.\n"
    )

    return df_ranked


if __name__ == "__main__":

    # Skenario
    query_pengguna = "Saya mencari rumah yang aman untuk keluarga, dekat dengan stasiun kereta atau KRL, dan dekat fasilitas kesehatan."
    feedback_negatif = ["pasar tradisional", "pasar", "pemakaman"]

    rekomendasi = get_recommendations(
        positive_query=query_pengguna, negative_feedbacks=feedback_negatif, top_n=3
    )

    for i, row in enumerate(rekomendasi.itertuples(), 1):
        print(
            f"Peringkat {i} (Skor Kecocokan: {round(row.Similarity_Score * 100, 2)}%)"
        )
        print(f"ID Iklan  : {row.ID_Iklan}")
        print(f"Judul     : {row.Judul}")
        print(f"Harga     : Rp {row.Harga:,.0f}")
        print(f"Lokasi    : {row.Kecamatan}, {row.Kota_Kabupaten}")

        # Fitur Explainability
        print("Detail:")
        print(f" - Transportasi: {str(row.Detail_POI_Transportasi)[:100]}...")
        print(f" - Kesehatan   : {str(row.Detail_POI_Kesehatan_Kebugaran)[:100]}...")
