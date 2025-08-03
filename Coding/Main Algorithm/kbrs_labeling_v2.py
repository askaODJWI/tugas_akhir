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
        "land_area": (22, 72),
        "building_area": (22, 50),
        "bedrooms": [1, 2],
        "bathrooms": [1, 2],
        "MALL": 1,
        "MARKET": 1,
        "TRANSPORT": 1
    }
}

# === Weights for each persona (importance of each feature) ===
weights_personas = {
    "Individu Lajang": {
        "type": 0.1818,
        "land_area": 0.1818,
        "building_area": 0.1818,
        "bedrooms": 0.0909,
        "bathrooms": 0.0909,
        "MALL": 0.0909,
        "MARKET": 0.0909,
        "TRANSPORT": 0.0909
    },
    "Pasangan Bekerja tanpa Anak": {
        "type": 0.1364,
        "land_area": 0.2273,
        "building_area": 0.2273,
        "bedrooms": 0.0909,
        "bathrooms": 0.0909,
        "MALL": 0.1364,
        "TRANSPORT": 0.0909
    },
    "Pasangan Bekerja dengan Anak": {
        "type": 0.0909,
        "land_area": 0.1818,
        "building_area": 0.1818,
        "bedrooms": 0.0909,
        "bathrooms": 0.0909,
        "SCHOOL": 0.0909,
        "HOSPITAL": 0.0909,
        "TRANSPORT": 0.0909,
        "MARKET": 0.0909
    }
}

# === MAUT utility function ===
def normalize(value, min_val, max_val):
    if pd.isna(value):
        return 0
    return max(0, min(1, (value - min_val) / (max_val - min_val)))

def maut_score(property_row, persona_criteria, weights):
    score = 0
    total_weight = sum(weights.values())

    for key, val in persona_criteria.items():
        weight = weights.get(key, 0)

        if key in ['land_area', 'building_area']:
            if not pd.isna(property_row[key]):
                u = normalize(property_row[key], val[0], val[1])
                score += u * weight

        elif key in ['bedrooms', 'bathrooms']:
            try:
                u = 1 if int(property_row[key]) in val else 0
                score += u * weight
            except:
                pass

        elif key == 'type':
            if isinstance(val, list):
                u = 1 if str(property_row[key]).lower() in [v.lower() for v in val] else 0
            else:
                u = 1 if str(property_row[key]).lower() == val.lower() else 0
            score += u * weight

        else:  # for proximity features like SCHOOL, HOSPITAL, etc.
            u = 1 if property_row.get(key, 0) == 1 else 0
            score += u * weight

    return score / total_weight if total_weight > 0 else 0

# === Score each property using MAUT ===
persona_scores = []

for _, row in df.iterrows():
    scores = {
        persona: maut_score(row, criteria, weights_personas[persona])
        for persona, criteria in ideal_personas.items()
    }
    best_match = max(scores, key=scores.get)

    property_data = row.to_dict()
    property_data["best_persona_match"] = best_match
    property_data["match_score"] = scores[best_match]

    persona_scores.append(property_data)


# === Save results ===
persona_score_df = pd.DataFrame(persona_scores)
filepath = Path('KBRS/kbrs_dataset_2_v2.csv')
filepath.parent.mkdir(parents=True, exist_ok=True)
persona_score_df.to_csv(filepath, index=False)

# === Preview ===
print("=== Preview of KBRS Dataset with Cleaned Numeric Columns ===")
print(persona_score_df.head())
