import pandas as pd
import numpy as np
from pathlib import Path

# Load dataset
df = pd.read_csv('INER/dataset_with_entities.csv')

# === Clean numeric columns ===
def clean_numeric_column(series):
    return (
        series.replace('>10', 10)
              .replace('3+', 3)
              .replace('2+', 2)
              .replace('4+', 4)
              .replace('-', np.nan)
              .astype(float)
    )

numeric_cols = ['land_area', 'building_area', 'bedrooms', 'bathrooms', 'floors']
for col in numeric_cols:
    if col in df.columns:
        df[col] = clean_numeric_column(df[col])

# === Ideal profiles for personas ===
ideal_personas = {
    "Pasangan Bekerja dengan Anak": {
        "type": "Rumah",
        "land_area": (200, 600),
        "building_area": (200, 600),
        "bedrooms": [3],
        "bathrooms": [2],
        "SCHOOL": 1,
        "HOSPITAL": 1,
        "TRANSPORT": 1,
        "MARKET": 1
    },
    "Pasangan Bekerja tanpa Anak": {
        "type": ["Apartemen", "Rumah"],
        "land_area": (22, 70),
        "building_area": (22, 70),
        "bedrooms": [2],
        "bathrooms": [2],
        "MALL": 1,
        "TRANSPORT": 1
    },
    "Individu Lajang": {
        "type": "Apartemen",
        "land_area": (22, 50),
        "building_area": (22, 50),
        "bedrooms": [1, 2],
        "bathrooms": [1, 2],
        "MALL": 1,
        "MARKET": 1,
        "TRANSPORT": 1
    }
}

# === Helper: calculate match score ===
def match_score(property_row, persona_criteria):
    matches = 0
    total = 0

    for key, val in persona_criteria.items():
        if key in ['land_area', 'building_area']:
            if not pd.isna(property_row[key]):
                if val[0] <= property_row[key] <= val[1]:
                    matches += 1
            total += 1
        elif key in ['bedrooms', 'bathrooms']:
            try:
                if int(property_row[key]) in val:
                    matches += 1
            except:
                pass
            total += 1
        elif key == 'type':
            if isinstance(val, list):
                if isinstance(property_row[key], str) and property_row[key].lower() in [v.lower() for v in val]:
                    matches += 1
            else:
                if isinstance(property_row[key], str) and property_row[key].lower() == val.lower():
                    matches += 1
            total += 1

    return matches / total if total > 0 else 0

# === Score each property ===
persona_scores = []

for _, row in df.iterrows():
    scores = {persona: match_score(row, criteria) for persona, criteria in ideal_personas.items()}
    best_match = max(scores, key=scores.get)

    # Copy all original row data
    property_data = row.to_dict()

    # Tambahkan kolom baru
    property_data["best_persona_match"] = best_match
    property_data["match_score"] = scores[best_match]

    persona_scores.append(property_data)

# === Save results ===
persona_score_df = pd.DataFrame(persona_scores)
filepath = Path('KBRS/kbrs_dataset_2.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
persona_score_df.to_csv(filepath, index=False)

# === Preview ===
print("=== Preview of KBRS Dataset with Cleaned Numeric Columns ===")
print(persona_score_df.head())
