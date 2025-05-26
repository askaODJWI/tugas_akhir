import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, hstack
import numpy as np
from pathlib import Path

# === Load dataset ===
df = pd.read_csv("KBRS/kbrs_dataset.csv")

# Define ideal personas
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
        "type": ["Apartemen", "Rumah"],  # Multiple allowed
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

# === USER INPUT ===
user_input = {
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
    "city": "Bekasi Kota"
}

# Match scoring function (same logic)
def match_score(input_data, persona_criteria):
    matches = 0
    total = 0

    for key, val in persona_criteria.items():
        if key in ['land_area', 'building_area']:
            if not pd.isna(input_data.get(key)):
                if val[0] <= input_data[key] <= val[1]:
                    matches += 1
            total += 1
        elif key in ['bedrooms', 'bathrooms']:
            try:
                if int(input_data.get(key, -1)) in val:
                    matches += 1
            except:
                pass
            total += 1
        elif key == 'type':
            input_type = input_data.get('type', '').lower()
            if isinstance(val, list):
                if input_type in [v.lower() for v in val]:
                    matches += 1
            else:
                if input_type == val.lower():
                    matches += 1
            total += 1
        else:
            if input_data.get(key) == val:
                matches += 1
            total += 1

    return matches / total if total > 0 else 0

# Calculate scores for each persona
user_scores = {persona: match_score(user_input, criteria) for persona, criteria in ideal_personas.items()}
best_user_persona = max(user_scores, key=user_scores.get)

# Add the best persona to user_input
user_input_personalized = user_input.copy()
user_input_personalized["Persona"] = best_user_persona

# === Filter dataset by city ===
filtered_by_city_df = df[df['address_city'].str.lower() == user_input['city'].lower()].copy()

# === Filter dataset by persona ===
filtered_df = filtered_by_city_df[filtered_by_city_df['best_persona_match'] == best_user_persona].copy()

# === Select relevant structured features ===
features = ['type', 'land_area', 'building_area', 'bedrooms', 'bathrooms', 'floors',
            'SCHOOL', 'HOSPITAL', 'TRANSPORT', 'MARKET', 'MALL']

# === Prepare dataset features ===
filtered_df_structured = filtered_df[features].copy()

# Handle categorical encoding (for 'type')
categorical_cols = ['type']
numeric_cols = [col for col in features if col not in categorical_cols]

# One-hot encode 'type'
encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
encoded_types = encoder.fit_transform(filtered_df_structured[categorical_cols])
encoded_type_cols = encoder.get_feature_names_out(categorical_cols)

# Scale numeric features
scaler = MinMaxScaler()
scaled_numeric = scaler.fit_transform(filtered_df[numeric_cols])
scaled_numeric_df = pd.DataFrame(scaled_numeric, columns=numeric_cols)

# Combine encoded + scaled features
property_matrix = hstack([csr_matrix(encoded_types), csr_matrix(scaled_numeric)])

# === Prepare user input vector ===
user_df = pd.DataFrame([user_input])
user_structured = user_df[features].copy()

# Encode 'type'
user_encoded_type = encoder.transform(user_structured[categorical_cols])
# Scale numeric
user_scaled_numeric = scaler.transform(user_structured[numeric_cols])

# Combine user features
user_vector = hstack([csr_matrix(user_encoded_type), csr_matrix(user_scaled_numeric)])

# === Compute Cosine Similarity ===
similarity_scores = cosine_similarity(user_vector, property_matrix)[0]

# === Top N Results ===
top_n = 10
top_indices = np.argsort(similarity_scores)[::-1][:top_n]
recommended = filtered_df.iloc[top_indices].copy()
recommended['similarity_score'] = similarity_scores[top_indices]

# === Output ===
print(recommended[['title', 'type', 'bedrooms', 'bathrooms', 'similarity_score']])

# === Save to CSV ===
filepath = Path('CBRS/cbrs_results_2.csv')  
filepath.parent.mkdir(parents=True, exist_ok=True)  
recommended.to_csv(filepath, index=False)
print("\n✅ Top-N recommendations saved to 'cbrs_results.csv'")
