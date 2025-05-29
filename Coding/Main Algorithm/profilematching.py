import pandas as pd
from pathlib import Path
import ast

# Load Top-N CBRS results (harus mencakup kolom 'facilities')
df = pd.read_csv("CBRS/cbrs_results_4.csv")

# Ideal profile based on user input
ideal_profile = {
    "type": "Rumah",
    "land_area": 200,
    "building_area": 50,
    "bedrooms": 2,
    "bathrooms": 2,
    "floors": 2,
    "SCHOOL": 0,
    "HOSPITAL": 1,
    "TRANSPORT": 1,
    "MARKET": 0,
    "MALL": 1,
    "facilities": ["AC", "Carport", "Refrigerator"]  # ✅ Tambahkan fasilitas ideal di sini
}

# Bobot kriteria
weights = {
    "type": 3,
    "land_area": 5,
    "building_area": 5,
    "bedrooms": 4,
    "bathrooms": 4,
    "floors": 2,
    "SCHOOL": 2,
    "HOSPITAL": 3,
    "TRANSPORT": 3,
    "MARKET": 2,
    "MALL": 3,
    "facilities": 4  # ✅ Bobot untuk fasilitas
}

# Konversi gap ke skor
def gap_to_score(gap):
    if gap == 0:
        return 5
    elif abs(gap) == 1:
        return 4.5
    elif abs(gap) == 2:
        return 4
    elif abs(gap) == 3:
        return 3.5
    elif abs(gap) == 4:
        return 3
    elif abs(gap) >= 5:
        return 2.5
    return 1

# Normalisasi string list facilities
def parse_facilities(value):
    if isinstance(value, list):
        return value
    if pd.isna(value) or value == '':
        return []
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, str):
            return [parsed]
    except:
        return [str(value)]
    return []

# Hitung skor total berdasarkan profil ideal
def calculate_total_score(row):
    total_score = 0
    total_weight = 0

    for key in ideal_profile:
        if key not in row:
            continue

        if key == "type":
            score = 5 if str(row[key]).lower() == ideal_profile[key].lower() else 1

        elif key == "facilities":
            user_facilities = set(ideal_profile["facilities"])
            prop_facilities = set(parse_facilities(row["facilities"]))
            matched = user_facilities.intersection(prop_facilities)
            match_ratio = len(matched) / len(user_facilities) if user_facilities else 0
            score = 1 + match_ratio * 4  # skala: 1 - 5

        else:
            try:
                gap = float(row[key]) - ideal_profile[key]
                score = gap_to_score(gap)
            except:
                score = 1

        total_score += score * weights[key]
        total_weight += weights[key]

    return total_score / total_weight if total_weight else 0

# Hitung skor GAP untuk seluruh properti
df["gap_score"] = df.apply(calculate_total_score, axis=1)

# Urutkan berdasarkan skor GAP tertinggi
df_sorted = df.sort_values(by="gap_score", ascending=False)

# Simpan hasil lengkap
filepath = Path('profile_matching/hasil_akhir_4.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
df_sorted.to_csv(filepath, index=False)

# Tampilkan hasil teratas
print("\n Recommended Properties:")
print(df_sorted[["title", "type", "bedrooms", "bathrooms", "similarity_score", "gap_score"]].head(5))