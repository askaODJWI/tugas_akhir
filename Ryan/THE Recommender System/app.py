import streamlit as st
import pandas as pd
import numpy as np
import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# KONFIGURASI & CACHE DATA
st.set_page_config(page_title="Sistem Rekomendasi Properti", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "..", "dataset_properti_corpus_final.csv")
POI_FILE = os.path.join(BASE_DIR, "..", "POI Extraction", "scaled_poi_density.npy")
EMBEDDING_FILE = os.path.join(
    BASE_DIR, "..", "Semantic Model", "semantic_embeddings.npy"
)
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Memori Sesi untuk Exclusion List
if "exclusion_list" not in st.session_state:
    st.session_state.exclusion_list = []


@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    poi_matrix = np.load(POI_FILE)
    embeddings = np.load(EMBEDDING_FILE)
    return df, poi_matrix, embeddings


model = load_model()
df_properti, poi_matrix, embeddings = load_data()


# FUNGSI PROFILE MATCHING & EXPLAINABILITY
def determine_persona(kamar_tidur, kamar_mandi, lantai, prioritas):
    score_single = 0
    score_family = 0

    # Kamar Tidur
    if kamar_tidur == 1:
        score_single += 2
    elif kamar_tidur > 1:
        score_family += 2

    # Kamar Mandi
    if kamar_mandi == 1:
        score_single += 1
    elif kamar_mandi > 1:
        score_family += 1

    # Lantai
    if lantai == 1:
        score_single += 1
    elif lantai >= 2:
        score_family += 1

    # Prioritas
    if prioritas == "Akses Pendidikan":
        score_family += 2
    elif prioritas == "Akses Transportasi Umum":
        score_single += 2
    elif prioritas == "Akses Klinik & Rumah Sakit":
        score_family += 1
    elif prioritas == "Akses Pusat Belanja & Kuliner":
        score_single += 1

    if score_family > score_single:
        return "Working Couple with Children"
    else:
        return "Single Professional"


def scale_value(val):
    if val <= 0.2:
        return 1
    elif val <= 0.4:
        return 2
    elif val <= 0.6:
        return 3
    elif val <= 0.8:
        return 4
    else:
        return 5


def gap_to_weight(gap):
    abs_gap = abs(gap)
    if abs_gap == 0:
        return 5
    elif abs_gap == 1:
        return 4
    elif abs_gap == 2:
        return 3
    elif abs_gap == 3:
        return 2
    else:
        return 1


def cek_fasilitas(fasilitas_str, keyword):
    if pd.isna(fasilitas_str):
        return 1
    return 5 if keyword.lower() in str(fasilitas_str).lower() else 1


def scale_luas_to_15(luas, target_type):
    if pd.isna(luas) or luas == 0:
        return 3
    if target_type == "compact":
        if luas <= 72:
            return 5
        elif luas <= 120:
            return 4
        elif luas <= 200:
            return 3
        elif luas <= 300:
            return 2
        else:
            return 1
    elif target_type == "luas":
        if luas >= 150:
            return 5
        elif luas >= 100:
            return 4
        elif luas >= 70:
            return 3
        elif luas >= 50:
            return 2
        else:
            return 1
    return 3


def get_matched_keywords(user_query, corpus_text):
    stopwords = {
        "yang",
        "di",
        "ke",
        "dari",
        "dan",
        "atau",
        "dengan",
        "untuk",
        "pada",
        "adalah",
        "ini",
        "itu",
        "sebuah",
        "saya",
        "mencari",
        "ingin",
        "ada",
        "dekat",
        "memiliki",
        "punya",
        "serta",
        "rumah",
        "apartemen",
        "hunian",
        "kamar",
        "lantai",
        "umum",
        "besar",
        "bagus",
        "tempat",
        "mobil",
        "pusat",
    }
    words = re.findall(r"\b[a-zA-Z0-9]{3,}\b", str(user_query).lower())

    ngrams = []
    for i in range(len(words) - 2):
        ngrams.append(f"{words[i]} {words[i+1]} {words[i+2]}")
    for i in range(len(words) - 1):
        ngrams.append(f"{words[i]} {words[i+1]}")
    for w in words:
        ngrams.append(w)

    matched = []
    corpus_lower = str(corpus_text).lower()

    for phrase in ngrams:
        phrase_words = phrase.split()
        if all(w in stopwords for w in phrase_words):
            continue

        if phrase in corpus_lower:
            is_subpart = False
            for m in matched:
                if phrase in m:
                    is_subpart = True
                    break
            if not is_subpart:
                matched.append(phrase)

    return matched


def filter_poi_by_radius(poi_str, max_dist_m=600):
    if pd.isna(poi_str) or not str(poi_str).strip():
        return []

    pois = [p.strip() for p in str(poi_str).split(",")]
    filtered = []

    for p in pois:
        match_m = re.search(r"\((\d+)m\)", p)
        match_km = re.search(r"\(([\d\.]+)km\)", p)

        dist = float("inf")
        if match_m:
            dist = int(match_m.group(1))
        elif match_km:
            dist = float(match_km.group(1)) * 1000

        if dist <= max_dist_m:
            filtered.append(p)

    return filtered


# UI PENGGUNA (SIDEBAR)
st.title("🏡 Sistem Rekomendasi Properti")
st.markdown("Pendekatan Semantic-Geospatial dengan Negative Feedback Handling")

st.sidebar.header("Kriteria Wajib")
kota_pilihan = st.sidebar.selectbox(
    "Pilih Kota:",
    [
        "Semua Kota",
        "Surabaya Kota",
        "Jakarta Selatan",
        "Jakarta Pusat",
        "Jakarta Barat",
        "Jakarta Timur",
        "Jakarta Utara",
        "Depok Kota",
        "Tangerang Kab.",
        "Tangerang Kota",
        "Tangerang Selatan Kota",
        "Bekasi Kab.",
        "Bekasi Kota",
        "Bogor Kab.",
        "Bogor Kota",
    ],
)
budget_maks = st.sidebar.number_input(
    "Budget Maksimal (Rp):", min_value=1000000, value=100000000, step=100000000
)
tipe_properti = st.sidebar.selectbox(
    "Tipe Properti:", ["Semua Tipe", "rumah", "apartemen"]
)

st.sidebar.header("Kriteria Preferensi")
kamar_tidur = st.sidebar.slider("Minimal Kamar Tidur:", 1, 11, 3)
kamar_mandi = st.sidebar.slider("Minimal Kamar Mandi:", 1, 11, 3)
lantai = st.sidebar.number_input("Minimal Jumlah Lantai:", min_value=1, value=2, step=1)

prioritas = st.sidebar.selectbox(
    "Fasilitas Lingkungan Paling Penting:",
    [
        "Akses Transportasi Umum",
        "Akses Pendidikan",
        "Akses Klinik & Rumah Sakit",
        "Akses Pusat Belanja & Kuliner",
    ],
)

# Inference Engine & Info Persona
persona = determine_persona(kamar_tidur, kamar_mandi, lantai, prioritas)
st.sidebar.success(f"**Persona Terdeteksi:**\n{persona}")

# Panel Memori Eksklusi
st.sidebar.header("Memori Eksklusi")
if len(st.session_state.exclusion_list) > 0:
    st.sidebar.warning("Atribut & Kata Kunci berikut sedang dihindari:")
    for excl in st.session_state.exclusion_list:
        st.sidebar.markdown(f"- 🚫 {excl}")
    if st.sidebar.button("Bersihkan Memori Eksklusi"):
        st.session_state.exclusion_list = []
        st.rerun()
else:
    st.sidebar.info("Belum ada atribut yang dieksklusi.")

# MAIN RECOMMENDATION ENGINE
st.subheader("🔍 Temukan Hunian Idaman Anda")

col_pos, col_neg = st.columns(2)

with col_pos:
    user_query = st.text_area(
        "Apa yang ANDA CARI?",
        placeholder="Contoh: rumah asri dan tenang, memiliki parkiran mobil dan halaman terbuka, serta dekat dengan pusat bisnis.",
        height=100,
    )

with col_neg:
    negative_query = st.text_area(
        "Apa yang ANDA HINDARI?",
        placeholder="Contoh: sutet, banjir, tusuk sate, gang sempit (Masukkan keyword(s), pisahkan dengan koma.)",
        height=100,
    )

if st.button("Cari Rekomendasi") or user_query:
    if user_query.strip() == "":
        st.warning(
            "Mohon masukkan deskripsi hunian idaman Anda pada kolom pencarian sebelah kiri."
        )
    else:
        with st.spinner("Mempersiapkan rekomendasi terbaik untuk Anda..."):

            # Menangkap input Negative Feedback ke Memori Eksklusi
            if negative_query.strip() != "":
                neg_terms = [
                    term.strip() for term in negative_query.split(",") if term.strip()
                ]
                for term in neg_terms:
                    if term not in st.session_state.exclusion_list:
                        st.session_state.exclusion_list.append(term)

            # INITIAL FILTERING
            df_filtered = df_properti.copy()
            if kota_pilihan != "Semua Kota":
                df_filtered = df_filtered[
                    df_filtered["Kota_Kabupaten"].str.lower() == kota_pilihan.lower()
                ]
            if tipe_properti != "Semua Tipe":
                df_filtered = df_filtered[
                    df_filtered["Tipe_Properti"].str.lower() == tipe_properti.lower()
                ]
            df_filtered = df_filtered[df_filtered["Harga"] <= budget_maks]
            df_filtered = df_filtered[df_filtered["Kamar_Tidur"] >= kamar_tidur]
            df_filtered = df_filtered[df_filtered["Kamar_Mandi"] >= kamar_mandi]
            df_filtered = df_filtered[df_filtered["Lantai"] >= lantai]

            # NEGATIVE FEEDBACK FILTERING
            for excl_term in st.session_state.exclusion_list:
                df_filtered = df_filtered[
                    ~df_filtered["Korpus_Properti"].str.contains(
                        excl_term, case=False, na=False
                    )
                ]

            if len(df_filtered) == 0:
                st.error(
                    "Tidak ada properti yang memenuhi kriteria. Coba longgarkan budget atau bersihkan memori eksklusi Anda."
                )
            else:
                # SBERT SIMILARITY
                query_vector = model.encode([user_query], convert_to_numpy=True)
                filtered_indices = df_filtered.index.tolist()
                filtered_embeddings = embeddings[filtered_indices]

                sim_scores_raw = cosine_similarity(query_vector, filtered_embeddings)[0]
                sim_scores_scaled = [scale_value(score) for score in sim_scores_raw]
                df_filtered["SBERT_Score"] = sim_scores_scaled
                df_filtered["SBERT_Raw"] = sim_scores_raw

                filtered_poi = poi_matrix[filtered_indices]
                final_scores = []

                for i, (_, row) in enumerate(df_filtered.iterrows()):
                    poi_vals = [scale_value(val) for val in filtered_poi[i]]

                    if persona == "Single Professional":
                        cf_k1 = np.mean(
                            [
                                (
                                    5
                                    if str(row["Tipe_Properti"]).lower() == "apartemen"
                                    else 1
                                ),
                                (
                                    5
                                    if row["Kamar_Tidur"] == 1
                                    else gap_to_weight(row["Kamar_Tidur"] - 1)
                                ),
                                (
                                    5
                                    if row["Kamar_Mandi"] == 1
                                    else gap_to_weight(row["Kamar_Mandi"] - 1)
                                ),
                                (
                                    5
                                    if row["Lantai"] == 1
                                    else gap_to_weight(row["Lantai"] - 1)
                                ),
                            ]
                        )
                        sf_k1 = np.mean(
                            [
                                gap_to_weight(
                                    scale_luas_to_15(row["Luas_Tanah"], "compact") - 3
                                ),
                                gap_to_weight(
                                    scale_luas_to_15(row["Luas_Bangunan"], "compact")
                                    - 3
                                ),
                            ]
                        )
                        score_k1 = (cf_k1 * 0.6) + (sf_k1 * 0.4)

                        cf_k2 = np.mean(
                            [
                                gap_to_weight(row["SBERT_Score"] - 5),
                                gap_to_weight(poi_vals[2] - 5),
                                gap_to_weight(poi_vals[6] - 5),
                                gap_to_weight(poi_vals[3] - 5),
                            ]
                        )
                        sf_k2 = np.mean(
                            [
                                gap_to_weight(poi_vals[1] - 3),
                                gap_to_weight(poi_vals[5] - 3),
                                gap_to_weight(poi_vals[7] - 3),
                                gap_to_weight(poi_vals[8] - 3),
                            ]
                        )
                        score_k2 = (cf_k2 * 0.6) + (sf_k2 * 0.4)

                        cf_k3 = np.mean(
                            [
                                gap_to_weight(
                                    cek_fasilitas(
                                        row["Fasilitas"], "Pendingin ruangan (AC)"
                                    )
                                    - 5
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Internet") - 5
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Air") - 5
                                ),
                            ]
                        )
                        sf_k3 = np.mean(
                            [
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Keamanan") - 3
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Kolam renang") - 3
                                ),
                                gap_to_weight(
                                    cek_fasilitas(
                                        row["Fasilitas"], "Berperabot Lengkap"
                                    )
                                    - 3
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Kitchen Set") - 3
                                ),
                            ]
                        )
                        score_k3 = (cf_k3 * 0.6) + (sf_k3 * 0.4)

                    else:
                        cf_k1 = np.mean(
                            [
                                (
                                    5
                                    if str(row["Tipe_Properti"]).lower() == "rumah"
                                    else 1
                                ),
                                (
                                    5
                                    if row["Kamar_Tidur"] > 2
                                    else gap_to_weight(row["Kamar_Tidur"] - 3)
                                ),
                                (
                                    5
                                    if row["Kamar_Mandi"] > 1
                                    else gap_to_weight(row["Kamar_Mandi"] - 2)
                                ),
                                (
                                    5
                                    if row["Lantai"] >= 2
                                    else gap_to_weight(row["Lantai"] - 2)
                                ),
                            ]
                        )
                        km_tamu_val = (
                            5
                            if pd.notna(row.get("Kamar_Mandi_Tamu"))
                            and row["Kamar_Mandi_Tamu"] > 0
                            else 1
                        )
                        sf_k1 = np.mean(
                            [
                                gap_to_weight(
                                    scale_luas_to_15(row["Luas_Tanah"], "luas") - 3
                                ),
                                gap_to_weight(
                                    scale_luas_to_15(row["Luas_Bangunan"], "luas") - 3
                                ),
                                gap_to_weight(km_tamu_val - 3),
                            ]
                        )
                        score_k1 = (cf_k1 * 0.6) + (sf_k1 * 0.4)

                        cf_k2 = np.mean(
                            [
                                gap_to_weight(row["SBERT_Score"] - 5),
                                gap_to_weight(poi_vals[0] - 5),
                                gap_to_weight(poi_vals[3] - 5),
                            ]
                        )
                        sf_k2 = np.mean(
                            [
                                gap_to_weight(poi_vals[1] - 3),
                                gap_to_weight(poi_vals[5] - 3),
                                gap_to_weight(poi_vals[4] - 3),
                                gap_to_weight(poi_vals[7] - 3),
                                gap_to_weight(poi_vals[6] - 3),
                            ]
                        )
                        score_k2 = (cf_k2 * 0.6) + (sf_k2 * 0.4)

                        cf_k3 = np.mean(
                            [
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Parkiran mobil")
                                    - 5
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Keamanan") - 5
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "CCTV") - 5
                                ),
                                gap_to_weight(
                                    cek_fasilitas(
                                        row["Fasilitas"], "Pendingin ruangan (AC)"
                                    )
                                    - 5
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Internet") - 5
                                ),
                            ]
                        )
                        sf_k3 = np.mean(
                            [
                                gap_to_weight(
                                    cek_fasilitas(
                                        row["Fasilitas"], "Taman Bermain Anak"
                                    )
                                    - 3
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Air") - 3
                                ),
                                gap_to_weight(
                                    cek_fasilitas(row["Fasilitas"], "Halaman Terbuka")
                                    - 3
                                ),
                            ]
                        )
                        score_k3 = (cf_k3 * 0.6) + (sf_k3 * 0.4)

                    total_score = (score_k1 * 0.4) + (score_k2 * 0.3) + (score_k3 * 0.3)
                    final_scores.append(total_score)

                df_filtered["Total_Score"] = final_scores
                df_ranked = df_filtered.sort_values(
                    by="Total_Score", ascending=False
                ).head(10)

                # UI HASIL REKOMENDASI
                st.write(f"### Menampilkan Top {len(df_ranked)} Rekomendasi Teratas")

                for rank, (idx, row) in enumerate(df_ranked.iterrows(), start=1):
                    with st.container():
                        st.markdown(f"#### {rank}. {row['Judul']}")

                        km_tamu = (
                            f"{int(row['Kamar_Mandi_Tamu'])} Kamar Mandi Tamu"
                            if pd.notna(row["Kamar_Mandi_Tamu"])
                            else "Kamar Mandi Tamu: None"
                        )
                        fasilitas = (
                            row["Fasilitas"] if pd.notna(row["Fasilitas"]) else "None"
                        )
                        daya_listrik = (
                            f"{(row['Daya_Listrik_Watt'])} Watt"
                            if pd.notna(row["Daya_Listrik_Watt"])
                            else "None"
                        )
                        sertifikat = (
                            row["Sertifikat"] if pd.notna(row["Sertifikat"]) else "None"
                        )
                        arah_hadap = (
                            row["Arah_Hadap"] if pd.notna(row["Arah_Hadap"]) else "None"
                        )
                        url_sumber = (
                            row["URL_Sumber"] if pd.notna(row["URL_Sumber"]) else "#"
                        )

                        lantai_val = row["Lantai"]
                        if pd.notna(lantai_val):
                            lantai_str = (
                                f"{int(lantai_val)}"
                                if float(lantai_val).is_integer()
                                else f"{lantai_val}"
                            )
                        else:
                            lantai_str = "None"

                        st.markdown(
                            f"**Harga:** Rp {row['Harga']:,.0f} | **Lokasi:** {row['Kecamatan']}, {row['Kota_Kabupaten']}"
                        )
                        st.markdown(
                            f"**Spesifikasi:** {row['Tipe_Properti'].title()} | {lantai_str} Lantai | {row['Kamar_Tidur']} Kamar Tidur | {row['Kamar_Mandi']} Kamar Mandi | {km_tamu}"
                        )
                        st.caption(f"Fasilitas: {fasilitas}")
                        st.caption(
                            f"Daya Listrik: {daya_listrik} | Sertifikat: {sertifikat} | Arah Hadap: {arah_hadap}"
                        )

                        st.markdown(f"[🔗 **Link Iklan**]({url_sumber})")

                        # FITUR EXPLAINABILITY
                        with st.expander(
                            "💡 Mengapa properti ini direkomendasikan untuk Anda?"
                        ):
                            match_pct = round(row["SBERT_Raw"] * 100, 1)
                            matched_kws = get_matched_keywords(
                                user_query, row["Korpus_Properti"]
                            )

                            if matched_kws:
                                kw_str = ", ".join([f"**{k}**" for k in matched_kws])
                                st.markdown(
                                    f"**Kesesuaian Narasi ({match_pct}%):** Narasi iklan ini selaras dengan pencarian Anda. Kata kunci relevan: {kw_str}."
                                )
                            else:
                                st.markdown(
                                    f"**Kesesuaian Narasi ({match_pct}%):** Narasi iklan ini memiliki kedekatan konteks dengan deskripsi idaman Anda."
                                )

                            st.markdown(
                                f"**Karakteristik Fisik:** Properti memenuhi standar minimum ({lantai_str} Lantai, {row['Kamar_Tidur']} Kamar Tidur, {row['Kamar_Mandi']} Kamar Mandi), cocok dengan gaya hidup **{persona}**."
                            )

                            prioritas_map = {
                                "Akses Transportasi Umum": "Detail_POI_Transportasi",
                                "Akses Pendidikan": "Detail_POI_Pendidikan",
                                "Akses Klinik & Rumah Sakit": "Detail_POI_Kesehatan_Kebugaran",
                                "Akses Pusat Belanja & Kuliner": "Detail_POI_Perbelanjaan",
                            }
                            detail_col = prioritas_map.get(prioritas)

                            if detail_col and pd.notna(row.get(detail_col)):
                                pois_within_walkable = filter_poi_by_radius(
                                    row[detail_col], max_dist_m=600
                                )
                                if pois_within_walkable:
                                    poi_str = ", ".join(pois_within_walkable)
                                    st.markdown(
                                        f"**Karakteristik Geospasial:** Sangat mendukung prioritas **{prioritas}** Anda. Fasilitas dalam radius <= 600m: *{poi_str}*."
                                    )
                                else:
                                    closest_pois = str(row[detail_col]).split(",")[:1]
                                    poi_str = ", ".join(closest_pois).strip()
                                    st.markdown(
                                        f"**Karakteristik Geospasial:** Mendukung prioritas **{prioritas}** Anda. Fasilitas terdekat: *{poi_str}*."
                                    )
                            else:
                                st.markdown(
                                    f"**Karakteristik Geospasial:** Memenuhi standar kecocokan radius spasial sistem (1.25 km) untuk kelengkapan fasilitas publik di sekitar properti."
                                )

                        # ITEM-LEVEL NEGATIVE FEEDBACK
                        with st.expander("👎 Kurang Suka dengan Properti Ini?"):
                            opsi_eksklusi = []
                            if pd.notna(row["Fasilitas"]):
                                fasilitas_list = [
                                    f.strip() for f in str(row["Fasilitas"]).split(",")
                                ]
                                opsi_eksklusi.extend(fasilitas_list)

                            selected_excl = st.multiselect(
                                "Pilih atribut spesifik yang ingin dihindari pada pencarian berikutnya:",
                                opsi_eksklusi,
                                key=f"multi_{row['ID_Iklan']}",
                            )

                            if st.button("Cari Ulang", key=f"btn_{row['ID_Iklan']}"):
                                if selected_excl:
                                    st.session_state.exclusion_list.extend(
                                        selected_excl
                                    )
                                    st.session_state.exclusion_list = list(
                                        set(st.session_state.exclusion_list)
                                    )
                                    st.rerun()
                                else:
                                    st.warning(
                                        "Pilih minimal satu atribut untuk dieksklusi."
                                    )
                        st.divider()
