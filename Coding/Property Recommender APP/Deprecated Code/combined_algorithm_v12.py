import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.optimize import minimize
from scipy.sparse import csr_matrix, hstack
import numpy as np
import ast
from pathlib import Path

# === Load dataset ===
df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Main Algorithm\KBRS\kbrs_dataset_2.csv')

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

def run_algorithm(user_input):
    def normalize_text_column(val):
        if pd.isna(val):
            return ''
        if isinstance(val, list):
            return ' '.join(val)
        if isinstance(val, str):
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, list):
                    return ' '.join(parsed)
                elif isinstance(parsed, str):
                    return parsed
            except (ValueError, SyntaxError):
                return val  # fallback if not list-like
        return ''

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
    # filtered_df_structured = filtered_df[features].copy()

    # Handle categorical encoding (for 'type')
    categorical_cols = ['type']
    numeric_cols = [col for col in features if col not in categorical_cols]

    # One-hot encode
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_types = encoder.fit_transform(filtered_df[categorical_cols])
    # Scale numerics
    scaler = MinMaxScaler()
    scaled_numeric = scaler.fit_transform(filtered_df[numeric_cols])
    # Structured property matrix
    structured_matrix = hstack([csr_matrix(encoded_types), csr_matrix(scaled_numeric)])

    # === Text Features (TF-IDF) ===
    filtered_df['description'] = filtered_df['description'].fillna("[]")
    filtered_df['facilities'] = filtered_df['facilities'].fillna("[]")

    # Convert array-like strings to text
    filtered_df['facilities_clean'] = filtered_df['facilities'].apply(normalize_text_column)
    filtered_df['description_clean'] = filtered_df['description'].apply(normalize_text_column)


    # Combine binary entity columns as text (e.g. "SCHOOL HOSPITAL")
    entity_cols = ['SCHOOL', 'UNIVERSITY', 'HOSPITAL', 'TRANSPORT', 'MARKET', 'MALL', 'WORSHIP']
    filtered_df['entity_clean'] = filtered_df[entity_cols].apply(
        lambda row: ' '.join([col for col in entity_cols if row[col] == 1]), axis=1
    )

    # TF-IDF vectorizers
    vectorizer_desc = TfidfVectorizer(max_features=300)
    vectorizer_fac = TfidfVectorizer(max_features=300)
    vectorizer_ent = TfidfVectorizer(max_features=300)

    tfidf_desc = vectorizer_desc.fit_transform(filtered_df['description_clean'])
    tfidf_fac = vectorizer_fac.fit_transform(filtered_df['facilities_clean'])
    tfidf_ent = vectorizer_ent.fit_transform(filtered_df['entity_clean'])

    # Apply weights
    weight_desc, weight_fac, weight_ent = 0.3, 0.2, 0.5
    tfidf_matrix = hstack([
        tfidf_desc.multiply(weight_desc),
        tfidf_fac.multiply(weight_fac),
        tfidf_ent.multiply(weight_ent)
    ])

    # === Final Property Matrix (Structured + TF-IDF) ===
    property_matrix = hstack([structured_matrix, tfidf_matrix])

    # === Prepare User Input Vector ===
    user_df = pd.DataFrame([user_input])
    user_structured = user_df[features].copy()
    user_encoded_type = encoder.transform(user_structured[categorical_cols])
    user_scaled_numeric = scaler.transform(user_structured[numeric_cols])
    user_structured_vector = hstack([csr_matrix(user_encoded_type), csr_matrix(user_scaled_numeric)])

    # User text fields
    user_desc_text = ""
    user_fac_text = ""
    user_entity_text = ' '.join([col for col in entity_cols if user_input.get(col, 0) == 1])

    # TF-IDF transform for user
    user_desc_vec = vectorizer_desc.transform([user_desc_text])
    user_fac_vec = vectorizer_fac.transform([user_fac_text])
    user_ent_vec = vectorizer_ent.transform([user_entity_text])
    user_tfidf = hstack([
        user_desc_vec.multiply(weight_desc),
        user_fac_vec.multiply(weight_fac),
        user_ent_vec.multiply(weight_ent)
    ])

    # Final user vector
    user_vector = hstack([user_structured_vector, user_tfidf])

    # === Compute Cosine Similarity ===
    similarity_scores = cosine_similarity(user_vector, property_matrix)[0]

    # === Top N Results ===
    top_n = 10
    top_indices = np.argsort(similarity_scores)[::-1][:top_n]
    recommended = filtered_df.iloc[top_indices].copy()
    recommended['similarity_score'] = similarity_scores[top_indices]

    filepath_cbrs = Path('combined_algorithm/hasil_cbrs.csv')
    filepath_cbrs.parent.mkdir(parents=True, exist_ok=True)
    recommended.to_csv(filepath_cbrs, index=False)

    # Skala konversi gap (selisih -> nilai skor)
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
            return 1  # fallback
        
     # === Daftar fitur yang digunakan untuk scoring ===
    feature_keys = list(user_input.keys())

    # === Fungsi loss untuk optimasi bobot ===
    def loss(weights):
        weights = dict(zip(feature_keys, weights))
        total_loss = 0

        for idx, row in df.iterrows():
            total_score = 0
            total_weight = 0
            for key in feature_keys:
                if key == "type":
                    score = 5 if str(row[key]).lower() == user_input[key].lower() else 1
                else:
                    try:
                        gap = float(row[key]) - user_input[key]
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

    # Fungsi menghitung total score untuk setiap properti
    def calculate_total_score(row):
        total_score = 0
        total_weight = 0
        for key in feature_keys:
            weight = optimized_weights.get(key, 1)
            if key == "type":
                score = 5 if str(row[key]).lower() == user_input[key].lower() else 1
            else:
                try:
                    gap = float(row[key]) - user_input[key]
                    score = gap_to_score(gap)
                except:
                    score = 1
            total_score += score * weight
            total_weight += weight
        return total_score / total_weight if total_weight else 0

    # Hitung skor untuk semua properti
    recommended["gap_score"] = recommended.apply(calculate_total_score, axis=1)

    # Urutkan berdasarkan skor tertinggi
    df_sorted = recommended.sort_values(by="gap_score", ascending=False)

    # Tampilkan hasil teratas
    df_sorted[["title", "type", "bedrooms", "bathrooms", "similarity_score", "gap_score"]].head(5)

    # === Output ===
    print("\nRecommended Properties")
    print(df_sorted[["title", "type", "bedrooms", "bathrooms", "similarity_score", "gap_score"]])

    # Save the final DataFrame to CSV
    filepath = Path('combined_algorithm/hasil.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df_sorted.to_csv(filepath, index=False)

    return df_sorted[["title", "type", "bedrooms", "bathrooms", "similarity_score", "gap_score"]].head(10).to_dict(orient="records")