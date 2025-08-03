import pandas as pd
from ProfileMatching import determine_persona  # asumsi dari file ProfileMatching.py yang sudah ada

# Load data csv yang sudah kamu buat sebelumnya
df_inputs = pd.read_csv("random_300_test_inputs_profile_matching.csv")

# Kita akan menyimpan hasil dalam list
results = []

for idx, row in df_inputs.iterrows():
    # Parse facilities (dari string "AC,STOVE,PAM" menjadi list)
    facilities_list = row['facilities'].split(',') if pd.notna(row['facilities']) and row['facilities'] else []

    # Build user_input dict
    user_input = {
        "type": row["type"],
        "land_area": row["land_area"],
        "building_area": row["building_area"],
        "bedrooms": row["bedrooms"],
        "bathrooms": row["bathrooms"],
        "floors": row["floors"],
        "HOSPITAL": row["HOSPITAL"],
        "SCHOOL": row["SCHOOL"],
        "MARKET": row["MARKET"],
        "MALL": row["MALL"],
        "TRANSPORT": row["TRANSPORT"],
        "facilities": facilities_list
    }

    # Tentukan persona
    persona_label, persona_score = determine_persona(user_input)

    # Simpan ke hasil
    results.append({
        "profile_target": row["profile"],
        "level": row["level"],
        "type": row["type"],
        "land_area": row["land_area"],
        "building_area": row["building_area"],
        "bedrooms": row["bedrooms"],
        "bathrooms": row["bathrooms"],
        "floors": row["floors"],
        "HOSPITAL": row["HOSPITAL"],
        "SCHOOL": row["SCHOOL"],
        "MARKET": row["MARKET"],
        "MALL": row["MALL"],
        "TRANSPORT": row["TRANSPORT"],
        "facilities": row["facilities"],
        "predicted_persona": persona_label,
        "matching_score": round(persona_score, 4)
    })

# Buat DataFrame hasil
df_results = pd.DataFrame(results)

# Simpan ke CSV
output_path = "results_profile_matching1.csv"
df_results.to_csv(output_path, index=False)
print(f"✅ Hasil disimpan ke {output_path}")
