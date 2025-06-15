import os
import pandas as pd

# --- GAP to Weighted Score ---
def gap_to_weighted_score(gap):
    gap = abs(gap)
    return max(1, 5 - gap)  # gap: 0→5, 1→4, 2→3, 3→2, 4+→1

# --- Scoring Functions ---

# --- Karakteristik Hunian (Bobot: 40%) ---
def score_building_area(value, persona):
    if persona == 'Individu Lajang':
        if value <= 72: return 5
        if value <= 99: return 4
        if value <= 149: return 3
        if value <= 200: return 2
        return 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        if value <= 50: return 1
        if value <= 72: return 2
        if value <= 120: return 3
        if value >= 150: return 4
        return 5
    elif persona == 'Pasangan Bekerja dengan Anak':
        if value <= 70: return 1
        if value <= 100: return 2
        if value <= 149: return 3
        if value <= 150: return 4
        return 5
    return 1

def score_bedrooms(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value <= 1 else 3 if value == 2 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value <= 2 else 3 if value == 3 else 2
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 1 if value <= 1 else 3 if value == 2 else 5

def score_bathrooms(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 3 if value == 2 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 3 if value == 2 else 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 1 if value <= 1 else 3 if value == 2 else 5

def score_floors(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 3 if value == 2 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 3 if value == 2 else 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 1 if value == 1 else 3 if value == 2 else 5

def score_type(value, persona):
    val = value.lower()
    return 5 if (persona == 'Individu Lajang' and val == 'apartemen') or \
                (persona != 'Individu Lajang' and val == 'rumah') else 1

# --- Fasilitas Lokasi Sekitar (Bobot: 30%) ---

def score_hospital(value, persona):
    if persona == 'Individu Lajang':
        return 3 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_school(value, persona):
    if persona == 'Individu Lajang':
        return 3 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 3 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_market(value, persona):
    if persona == 'Individu Lajang':
        return 3 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 3 if value == 1 else 1
    
def score_mall(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 3 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 3 if value == 1 else 1
    
def score_transport(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 3 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 3 if value == 1 else 1
    
# --- Fasilitas Hunian (Bobot: 30%) ---

def score_ac(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_carport(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_garasi(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_garden(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_stove(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_oven(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_refrigerator(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_microwave(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_pam(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_water_heater(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 1 else 1
    
def score_gordyn(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 5 if value == 0 else 1
    
# --- Data Transformation ---

# --- Ideal Scores ---
ideal_scores = {
    'Individu Lajang': {
        'building_area': 5,
        'bedrooms': 5,
        'bathrooms': 3,
        'floors': 3,
        'type': 5,
        'hospital': 4,
        'school': 4,
        'market': 4,
        'mall': 4,
        'transport': 4,
        'ac': 3,
        'carport': 2,
        'garasi': 2,
        'garden': 2,
        'stove': 3,
        'oven': 2,
        'refrigerator': 3,
        'microwave': 2,
        'pam': 3,
        'water_heater': 2,
        'gordyn': 2
    },
    'Pasangan Bekerja tanpa Anak': {
        'building_area': 5,
        'bedrooms': 5,
        'bathrooms': 3,
        'floors': 3,
        'type': 5,
        'hospital': 4,
        'school': 4,
        'market': 4,
        'mall': 4,
        'transport': 4,
        'ac': 3,
        'carport': 3,
        'garasi': 3,
        'garden': 2,
        'stove': 3,
        'oven': 3,
        'refrigerator': 3,
        'microwave': 2,
        'pam': 3,
        'water_heater': 2,
        'gordyn': 2
    },
    'Pasangan Bekerja dengan Anak': {
        'building_area': 5,
        'bedrooms': 5,
        'bathrooms': 3,
        'floors': 3,
        'type': 5,
        'hospital': 4,
        'school': 4,
        'market': 4,
        'mall': 4,
        'transport': 4,
        'ac': 3,
        'carport': 3,
        'garasi': 3,
        'garden': 3,
        'stove': 3,
        'oven': 3,
        'refrigerator': 3,
        'microwave': 3,
        'pam': 3,
        'water_heater': 3,
        'gordyn': 3
    }
}

# --- Criteria → Category & CF/SF per Persona ---
criteria_structure = {
    'Individu Lajang': {
        'building_area': ('Karakteristik Hunian', 'SF'),
        'bedrooms': ('Karakteristik Hunian', 'CF'),
        'bathrooms': ('Karakteristik Hunian', 'SF'),
        'floors': ('Karakteristik Hunian', 'SF'),
        'type': ('Fasilitas Hunian', 'CF'),
        'hospital': ('Fasilitas Lokasi', 'SF'),
        'school': ('Fasilitas Lokasi', 'SF'),
        'market': ('Fasilitas Lokasi', 'SF'),
        'mall': ('Fasilitas Lokasi', 'CF'),
        'transport': ('Fasilitas Lokasi', 'CF'),
        'ac': ('Fasilitas Hunian', 'CF'),
        'carport': ('Fasilitas Hunian', 'SF'),
        'garasi': ('Fasilitas Hunian', 'SF'),
        'garden': ('Fasilitas Hunian', 'SF'),
        'stove': ('Fasilitas Hunian', 'CF'),
        'oven': ('Fasilitas Hunian', 'SF'),
        'refrigerator': ('Fasilitas Hunian', 'CF'),
        'microwave': ('Fasilitas Hunian', 'SF'),
        'pam': ('Fasilitas Hunian', 'CF'),
        'water_heater': ('Fasilitas Hunian', 'SF'),
        'gordyn': ('Fasilitas Hunian', 'SF')
    },
    'Pasangan Bekerja tanpa Anak': {
        'building_area': ('Karakteristik Hunian', 'CF'),
        'bedrooms': ('Karakteristik Hunian', 'CF'),
        'bathrooms': ('Karakteristik Hunian', 'SF'),
        'floors': ('Karakteristik Hunian', 'SF'),
        'type': ('Fasilitas Hunian', 'SF'),
        'hospital': ('Fasilitas Lokasi', 'CF'),
        'school': ('Fasilitas Lokasi', 'SF'),
        'market': ('Fasilitas Lokasi', 'CF'),
        'mall': ('Fasilitas Lokasi', 'SF'),
        'transport': ('Fasilitas Lokasi', 'SF'),
        'ac': ('Fasilitas Hunian', 'CF'),
        'carport': ('Fasilitas Hunian', 'CF'),
        'garasi': ('Fasilitas Hunian', 'CF'),
        'garden': ('Fasilitas Hunian', 'SF'),
        'stove': ('Fasilitas Hunian', 'CF'),
        'oven': ('Fasilitas Hunian', 'CF'),
        'refrigerator': ('Fasilitas Hunian', 'CF'),
        'microwave': ('Fasilitas Hunian', 'SF'),
        'pam': ('Fasilitas Hunian', 'CF'),
        'water_heater': ('Fasilitas Hunian', 'SF'),
        'gordyn': ('Fasilitas Hunian', 'SF')
    },
    'Pasangan Bekerja dengan Anak': {
        'building_area': ('Karakteristik Hunian', 'CF'),
        'bedrooms': ('Karakteristik Hunian', 'CF'),
        'bathrooms': ('Karakteristik Hunian', 'CF'),
        'floors': ('Karakteristik Hunian', 'SF'),
        'type': ('Fasilitas Hunian', 'SF'),
        'hospital': ('Fasilitas Lokasi', 'CF'),
        'school': ('Fasilitas Lokasi', 'CF'),
        'market': ('Fasilitas Lokasi', 'SF'),
        'mall': ('Fasilitas Lokasi', 'SF'),
        'transport': ('Fasilitas Lokasi', 'SF'),
        'ac': ('Fasilitas Hunian', 'CF'),
        'carport': ('Fasilitas Hunian', 'CF'),
        'garasi': ('Fasilitas Hunian', 'CF'),
        'garden': ('Fasilitas Hunian', 'CF'),
        'stove': ('Fasilitas Hunian', 'CF'),
        'oven': ('Fasilitas Hunian', 'CF'),
        'refrigerator': ('Fasilitas Hunian', 'CF'),
        'microwave': ('Fasilitas Hunian', 'CF'),
        'pam': ('Fasilitas Hunian', 'CF'),
        'water_heater': ('Fasilitas Hunian', 'CF'),
        'gordyn': ('Fasilitas Hunian', 'CF')
    }
}

def save_dataframe_with_counter(df, base_name: str, folder: str):
    os.makedirs(folder, exist_ok=True)
    existing = [f for f in os.listdir(folder) if f.startswith(base_name) and f.endswith(".csv")]
    numbers = [int(f.replace(base_name + "_", "").replace(".csv", "")) for f in existing if f.replace(base_name + "_", "").replace(".csv", "").isdigit()]
    next_index = max(numbers) + 1 if numbers else 1
    filename = f"{base_name}_{next_index:03d}.csv"
    filepath = os.path.join(folder, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Saved: {filepath}")

def build_user_input(raw_input: dict) -> dict:
    facilities_list = [f.upper() for f in raw_input.get("facilities", [])]

    def has(fac_name): return int(fac_name.upper() in facilities_list)

    return {
        "type": raw_input.get("type", "rumah"),
        "land_area": raw_input.get("land_area", 0),
        "building_area": raw_input.get("building_area", 0),
        "bedrooms": raw_input.get("bedrooms", 0),
        "bathrooms": raw_input.get("bathrooms", 0),
        "floors": raw_input.get("floors", 0),
        "hospital": raw_input.get("HOSPITAL", 0),
        "school": raw_input.get("SCHOOL", 0),
        "market": raw_input.get("MARKET", 0),
        "mall": raw_input.get("MALL", 0),
        "transport": raw_input.get("TRANSPORT", 0),
        "facility_ac": has("AC"),
        "facility_carport": has("CARPORT"),
        "facility_garasi": has("GARASI"),
        "facility_garden": has("GARDEN"),
        "facility_stove": has("STOVE"),
        "facility_oven": has("OVEN"),
        "facility_refrigerator": has("REFRIGERATOR"),
        "facility_microwave": has("MICROWAVE"),
        "facility_pam": has("PAM"),
        "facility_water_heater": has("WATER HEATER"),
        "facility_gordyn": has("GORDYN")
    }

def determine_persona(user_input: dict) -> tuple[str, float]:
    # The initial user_input is the raw input, which gets processed here.
    processed_user_input = build_user_input(user_input)

    # --- MODIFICATION START ---
    # 1. Convert the processed user input dictionary into a single-row DataFrame.
    user_input_df = pd.DataFrame([processed_user_input])

    # 2. Save the DataFrame to a CSV for inspection.
    save_dataframe_with_counter(
        user_input_df,
        base_name="ProfileMatching_UserInput",
        folder="results/profile_matching"
    )

    user_input = build_user_input(user_input)
    # --- CF/SF Weights ---
    cf_weight = 0.6
    sf_weight = 0.4
    category_weights = {
        'Karakteristik Hunian': 0.4,
        'Fasilitas Hunian': 0.3,
        'Fasilitas Lokasi': 0.3
    }

    results = {}
    for persona in ideal_scores.keys():
        category_cf = {}
        category_sf = {}

        for key in ideal_scores[persona]:
            input_key = f'facility_{key}' if key in ['ac', 'carport', 'garasi', 'garden', 'stove', 'oven',
                                                     'refrigerator', 'microwave', 'pam', 'water_heater', 'gordyn'] else key
            if key == 'building_area':
                value = user_input.get('building_area', 0) if persona == 'Individu Lajang' else user_input.get('land_area', 0)
            else:
                value = user_input.get(input_key, 0)
            score_func = globals().get(f"score_{key}", lambda v, p: 1)
            actual = score_func(value, persona)
            ideal = ideal_scores[persona][key]
            wg = gap_to_weighted_score(actual - ideal)

            category, factor = criteria_structure[persona][key]
            (category_cf if factor == 'CF' else category_sf).setdefault(category, []).append(wg)

        final_weighted = {}
        for cat in set(category_cf) | set(category_sf):
            ncf = sum(category_cf.get(cat, [])) / len(category_cf.get(cat)) if category_cf.get(cat) else 0
            nsf = sum(category_sf.get(cat, [])) / len(category_sf.get(cat)) if category_sf.get(cat) else 0
            final_score = cf_weight * ncf + sf_weight * nsf
            final_weighted[cat] = final_score * category_weights.get(cat, 0)

        total_score = sum(final_weighted.values())
        results[persona] = total_score

    # Save to CSV
    results_df = pd.DataFrame(list(results.items()), columns=["persona", "score"])
    save_dataframe_with_counter(results_df, base_name="ProfileMatching_results", folder="results/profile_matching")

    best_persona = max(results, key=results.get)
    best_score = results[best_persona]
    return best_persona, best_score