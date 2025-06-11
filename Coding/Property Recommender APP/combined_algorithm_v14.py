import pandas as pd
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.optimize import minimize
from scipy.sparse import csr_matrix, hstack
import numpy as np
import ast
from pathlib import Path
from ProfileMatching_v2 import determine_persona
from PropertyProfileMatching import apply_profile_matching

# === Load dataset ===
df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Main Algorithm\KBRS\kbrs_dataset_2.csv')

def run_algorithm(user_input):
    N = 10
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

    def normalize_user_facilities(fac):
        if isinstance(fac, list):
            return ' '.join(fac)
        elif isinstance(fac, str):
            return fac
        else:
            return ''

    # print("\n📦 User Input Passed to Profile Matching:")
    # for key, value in user_input.items():
    #     print(f"{key}: {value}")

    best_user_persona, matching_persona_score = determine_persona(user_input)
    user_input["Persona"] = best_user_persona

    # === Filter by city and persona ===
    filtered_by_city_df = df[df['address_city'].str.lower() == user_input['city'].lower()].copy()
    filtered_df = filtered_by_city_df[filtered_by_city_df['best_persona_match'] == best_user_persona].copy()

    # === Structured Features Processing ===
    features = ['type', 'land_area', 'building_area', 'bedrooms', 'bathrooms', 'floors',
                'SCHOOL', 'HOSPITAL', 'TRANSPORT', 'MARKET', 'MALL']
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
    filtered_df['facilities'] = filtered_df['facilities'].fillna("[]")

    # Convert array-like strings to text
    filtered_df['facilities_clean'] = filtered_df['facilities'].apply(normalize_text_column)


    # Combine binary entity columns as text (e.g. "SCHOOL HOSPITAL")
    entity_cols = ['SCHOOL', 'UNIVERSITY', 'HOSPITAL', 'TRANSPORT', 'MARKET', 'MALL', 'WORSHIP']
    filtered_df['entity_clean'] = filtered_df[entity_cols].apply(
        lambda row: ' '.join([col for col in entity_cols if row[col] == 1]), axis=1
    )

    # TF-IDF vectorizers
    vectorizer_fac = TfidfVectorizer(max_features=300)
    vectorizer_ent = TfidfVectorizer(max_features=300)

    tfidf_fac = vectorizer_fac.fit_transform(filtered_df['facilities_clean'])
    tfidf_ent = vectorizer_ent.fit_transform(filtered_df['entity_clean'])

    # Apply weights
    weight_fac, weight_ent = 0.5, 0.5
    tfidf_matrix = hstack([
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
    user_fac_text = normalize_user_facilities(user_input.get("facilities", ''))
    user_entity_text = ' '.join([col for col in entity_cols if user_input.get(col, 0) == 1])

    # TF-IDF transform for user
    user_fac_vec = vectorizer_fac.transform([user_fac_text])
    user_ent_vec = vectorizer_ent.transform([user_entity_text])
    user_tfidf = hstack([
        user_fac_vec.multiply(weight_fac),
        user_ent_vec.multiply(weight_ent)
    ])

    # Final user vector
    user_vector = hstack([user_structured_vector, user_tfidf])

    # === Compute Cosine Similarity ===
    similarity_scores = cosine_similarity(user_vector, property_matrix)[0]

    # === Top-N Results ===
    top_indices = np.argsort(similarity_scores)[::-1][:N]
    df_sorted_by_cosine = filtered_df.iloc[top_indices].copy()
    df_sorted_by_cosine['similarity_score'] = similarity_scores[top_indices]
    df_sorted_by_cosine["Persona"] = best_user_persona

    filepath_cbrs = Path('combined_algorithm/hasil_cbrs.csv')
    filepath_cbrs.parent.mkdir(parents=True, exist_ok=True)
    df_sorted_by_cosine.to_csv(filepath_cbrs, index=False)

    # Bobot kriteria (bisa disesuaikan)
    weights = {
        "type": 5,
        "land_area": 4,
        "building_area": 4,
        "bedrooms": 3,
        "bathrooms": 3,
        "floors": 2,
        "SCHOOL": 2,
        "HOSPITAL": 3,
        "TRANSPORT": 3,
        "MARKET": 2,
        "MALL": 3
    }

    # Skala konversi gap (selisih -> nilai skor)
    def gap_to_score(gap):
        if gap == 0:
            return 5
        elif gap == 1 or gap == -1:
            return 4.5
        elif gap == 2 or gap == -2:
            return 4
        elif gap == 3 or gap == -3:
            return 3.5
        elif gap == 4 or gap == -4:
            return 3
        elif gap >= 5 or gap <= -5:
            return 2.5
        else:
            return 1  # fallback

    df_sorted_by_final_score = apply_profile_matching(df_sorted_by_cosine)

    # Save the final DataFrame to CSV
    filepath = Path('combined_algorithm/hasil2.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df_sorted_by_final_score.to_csv(filepath, index=False)

    full_results = df_sorted_by_final_score[:N].to_dict(orient="records")
    cbrs_results = df_sorted_by_cosine[:N].to_dict(orient="records")

    return full_results, cbrs_results, best_user_persona, matching_persona_score