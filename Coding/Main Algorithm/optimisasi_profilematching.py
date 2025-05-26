import pandas as pd
import numpy as np
from pathlib import Path
from scipy.optimize import minimize

# === Load Top-N CBRS results ===
df = pd.read_csv("CBRS/cbrs_results_3.csv")

# === Ideal profile (based on user input) ===
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
    "MALL": 1
}

# === Skala konversi gap (selisih -> skor) ===
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
    else:
        return 1

# === Daftar fitur yang digunakan untuk scoring ===
feature_keys = list(ideal_profile.keys())

# === Fungsi loss untuk optimasi bobot ===
def loss(weights):
    weights = dict(zip(feature_keys, weights))
    total_loss = 0

    for idx, row in df.iterrows():
        total_score = 0
        total_weight = 0
        for key in feature_keys:
            if key == "type":
                score = 5 if str(row[key]).lower() == ideal_profile[key].lower() else 1
            else:
                try:
                    gap = float(row[key]) - ideal_profile[key]
                    score = gap_to_score(gap)
                except:
                    score = 1
            total_score += score * weights[key]
            total_weight += weights[key]

        avg_score = total_score / total_weight if total_weight else 0
        loss_i = (5 - avg_score)**2
        total_loss += loss_i

    return total_loss

# === Inisialisasi dan optimasi ===
initial_weights = [3.0 for _ in feature_keys]  # default awal
bounds = [(1.0, 5.0)] * len(feature_keys)

result = minimize(loss, initial_weights, bounds=bounds, method='L-BFGS-B')
optimized_weights = dict(zip(feature_keys, result.x))

print("\n Optimized Weights:")
for k, v in optimized_weights.items():
    print(f"{k}: {v:.2f}")

# === Hitung gap_score dengan bobot hasil optimasi ===
def calculate_total_score(row):
    total_score = 0
    total_weight = 0
    for key in feature_keys:
        weight = optimized_weights.get(key, 1)
        if key == "type":
            score = 5 if str(row[key]).lower() == ideal_profile[key].lower() else 1
        else:
            try:
                gap = float(row[key]) - ideal_profile[key]
                score = gap_to_score(gap)
            except:
                score = 1
        total_score += score * weight
        total_weight += weight
    return total_score / total_weight if total_weight else 0

df["gap_score"] = df.apply(calculate_total_score, axis=1)

# === Urutkan dan simpan hasil akhir ===
df_sorted = df.sort_values(by="gap_score", ascending=False)

# Simpan hasil ke CSV
final_path = Path("profile_matching/hasil_akhir_optimized.csv")
final_path.parent.mkdir(parents=True, exist_ok=True)
df_sorted.to_csv(final_path, index=False)

# === Output ringkas ===
print("\n🎯 Top 5 Rekomendasi:")
print(df_sorted[["title", "type", "bedrooms", "bathrooms", "similarity_score", "gap_score"]].head(5))
