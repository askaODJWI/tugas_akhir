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
import random

# === Load dataset ===
df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Main Algorithm\KBRS\kbrs_dataset_2.csv')

def generate_reasoning(user_input: dict, property_row: dict) -> str:
    reasons = []

    # --- Bedrooms & Bathrooms ---
    if "bedrooms" in user_input:
        user_bed = user_input["bedrooms"]
        prop_bed = int(property_row.get("bedrooms", 0))
        if prop_bed >= user_bed:
            templates = [
                f"You were looking for at least {user_bed} bedroom(s), and this one has {prop_bed}.",
                f"This property matches your bedroom need of {user_bed} — it offers {prop_bed}.",
                f"With {prop_bed} bedroom(s), it fulfills your minimum request of {user_bed}."
            ]
        else:
            templates = [
                f"You wanted {user_bed} bedroom(s), but this one only has {prop_bed}.",
                f"This home falls short on bedrooms — you asked for {user_bed}, it has {prop_bed}."
            ]
        reasons.append(random.choice(templates))

    if "bathrooms" in user_input:
        user_bath = user_input["bathrooms"]
        prop_bath = int(property_row.get("bathrooms", 0))
        if prop_bath >= user_bath:
            templates = [
                f"It offers {prop_bath} bathroom(s), meeting your need for at least {user_bath}.",
                f"Your bathroom preference of {user_bath} is covered here with {prop_bath} available.",
                f"With {prop_bath} bathrooms, it's aligned with your request for {user_bath}."
            ]
            reasons.append(random.choice(templates))

    # --- Nearby Amenities ---
    nearby_amenities = []
    for amenity in ["SCHOOL", "HOSPITAL", "TRANSPORT", "MARKET", "MALL"]:
        if user_input.get(amenity, 0) == 1 and property_row.get(amenity, 0) == 1:
            nearby_amenities.append(amenity.title())

    if nearby_amenities:
        joined = ", ".join(nearby_amenities[:-1]) + f", and {nearby_amenities[-1]}" if len(nearby_amenities) > 1 else nearby_amenities[0]
        templates = [
            f"It's conveniently located near {joined}, just as you preferred.",
            f"This property is close to your desired amenities: {joined}.",
            f"Nearby access to {joined} aligns with your preferences."
        ]
        reasons.append(random.choice(templates))

    # --- Facilities ---
    matched_facilities = []
    if "facilities" in user_input:
        for facility in user_input["facilities"]:
            if facility.upper() in str(property_row.get("facilities_clean", "")).upper():
                matched_facilities.append(facility)

    if matched_facilities:
        joined = ", ".join(matched_facilities[:-1]) + f", and {matched_facilities[-1]}" if len(matched_facilities) > 1 else matched_facilities[0]
        templates = [
            f"The property includes the facilities you wanted: {joined}.",
            f"It comes with key features you prefer, such as {joined}.",
            f"You’ll find facilities like {joined}, matching your preferences."
        ]
        reasons.append(random.choice(templates))

    return " ".join(reasons) if reasons else "This property aligns well with your preferences."

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

    df_sorted_by_final_score = apply_profile_matching(df_sorted_by_cosine)
    df_sorted_by_final_score["reasoning"] = df_sorted_by_final_score.apply(
        lambda row: generate_reasoning(user_input, row), axis=1
    )

    # Save the final DataFrame to CSV
    filepath = Path('combined_algorithm/hasil2.csv')
    filepath.parent.mkdir(parents=True, exist_ok=True)
    df_sorted_by_final_score.to_csv(filepath, index=False)

    full_results = df_sorted_by_final_score[:N].to_dict(orient="records")
    cbrs_results = df_sorted_by_cosine[:N].to_dict(orient="records")

    return full_results, cbrs_results, best_user_persona, matching_persona_score