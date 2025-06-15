import pandas as pd
from pathlib import Path
import os

# GAP to Weighted Score
def gap_to_weighted_score(gap):
    return max(1, 5 - abs(gap))

# CF/SF Weights and Category Weights
cf_weight = 0.6
sf_weight = 0.4
category_weights = {
    'Karakteristik Hunian': 0.4,
    'Fasilitas Hunian': 0.3,
    'Fasilitas Lokasi': 0.3
}

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

fasilitas_hunian = [
    'AC', 'Carport', 'Garasi', 'Garden', 'Stove', 'Oven', 'Refrigerator',
    'Microwave', 'PAM', 'Water Heater', 'Gordyn'
]
fasilitas_lokasi = ['SCHOOL', 'HOSPITAL', 'MARKET', 'TRANSPORT', "MALL"]

def process_facilities(row):
    fac = str(row.get('facilities_clean', '')).upper().split()
    ent = str(row.get('entity_clean', '')).upper().split()

    facilities = {
        'facility_' + f.lower().replace(" ", "_"): int(f in fac)
        for f in fasilitas_hunian
    }
    entities = {e.lower(): int(e in ent) for e in fasilitas_lokasi}

    return pd.Series({**facilities, **entities})

def save_dataframe_with_counter(df, base_name: str, folder: str):
    os.makedirs(folder, exist_ok=True)
    existing = [f for f in os.listdir(folder) if f.startswith(base_name) and f.endswith(".csv")]
    numbers = [int(f.replace(base_name + "_", "").replace(".csv", "")) for f in existing if f.replace(base_name + "_", "").replace(".csv", "").isdigit()]
    next_index = max(numbers) + 1 if numbers else 1
    filename = f"{base_name}_{next_index:03d}.csv"
    filepath = os.path.join(folder, filename)
    df.to_csv(filepath, index=False)
    print(f"✅ Saved: {filepath}")

# === Core API Function ===
def apply_profile_matching(df: pd.DataFrame) -> pd.DataFrame:
    """
    Accepts a DataFrame with pre-filtered properties and computes 'final_score' for each row
    using persona-specific profile matching logic. Returns a sorted DataFrame.
    """
    def build_user_input(row):
        return {
            'land_area': row.get('land_area', 0),
            'building_area': row.get('building_area', 0),
            'bedrooms': row.get('bedrooms', 0),
            'bathrooms': row.get('bathrooms', 0),
            'floors': row.get('floors', 0),
            'type': row.get('type', 'rumah'),
            'hospital': row.get('HOSPITAL', 0),
            'school': row.get('SCHOOL', 0),
            'market': row.get('MARKET', 0),
            'mall': row.get('MALL', 0),
            'transport': row.get('TRANSPORT', 0),
            'facility_ac': int('AC' in str(row.get('facilities_clean', '')).upper()),
            'facility_carport': int('CARPORT' in str(row.get('facilities_clean', '')).upper()),
            'facility_garasi': int('GARASI' in str(row.get('facilities_clean', '')).upper()),
            'facility_garden': int('GARDEN' in str(row.get('facilities_clean', '')).upper()),
            'facility_stove': int('STOVE' in str(row.get('facilities_clean', '')).upper()),
            'facility_oven': int('OVEN' in str(row.get('facilities_clean', '')).upper()),
            'facility_refrigerator': int('REFRIGERATOR' in str(row.get('facilities_clean', '')).upper()),
            'facility_microwave': int('MICROWAVE' in str(row.get('facilities_clean', '')).upper()),
            'facility_pam': int('PAM' in str(row.get('facilities_clean', '')).upper()),
            'facility_water_heater': int('WATER HEATER' in str(row.get('facilities_clean', '')).upper()),
            'facility_gordyn': int('GORDYN' in str(row.get('facilities_clean', '')).upper())
        }
    
    # 1. Apply build_user_input to each row to generate a list of dictionaries.
    user_inputs_list = df.apply(build_user_input, axis=1).tolist()

    # 2. Convert the list of dictionaries into a DataFrame for inspection.
    user_input_df = pd.DataFrame(user_inputs_list)

    # 3. Save the DataFrame containing the output of build_user_input to a CSV.
    save_dataframe_with_counter(
        user_input_df,
        base_name="PropertyProfileMatching_UserInput",
        folder="results/property_profile_matching"
    )

    def calculate_final_score(user_input, persona):
        category_cf, category_sf = {}, {}

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
            ncf = sum(category_cf.get(cat, [])) / len(category_cf.get(cat, [])) if category_cf.get(cat) else 0
            nsf = sum(category_sf.get(cat, [])) / len(category_sf.get(cat, [])) if category_sf.get(cat) else 0
            final_score = cf_weight * ncf + sf_weight * nsf
            final_weighted[cat] = final_score * category_weights.get(cat, 0)

        return sum(final_weighted.values())

    df['final_score'] = df.apply(
        lambda row: calculate_final_score(build_user_input(row), row['Persona']), axis=1
    )

    df_sorted = df.sort_values(by='final_score', ascending=False)

    # Save result
    # save_dataframe_with_counter(df_sorted, base_name="PropertyProfileMatching_results", folder="results/property_profile_matching")

    return df_sorted