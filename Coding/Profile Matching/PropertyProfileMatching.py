import pandas as pd
from pathlib import Path

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

# Mapping raw persona label to scoring system
persona_map = {
    "Individu Lajang": "Individu Lajang",
    "Pasangan Bekerja tanpa Anak": "Pasangan Bekerja tanpa Anak",
    "Pasangan Bekerja dengan Anak": "Pasangan Bekerja dengan Anak"
}

# --- Scoring Functions ---

# --- Karakteristik Hunian (Bobot: 40%) ---
def score_building_area(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value <= 72 else 4 if value <= 99 else 3 if value <= 149 else 2 if value <= 200 else 1
    elif persona == 'Pasangan Bekerja tanpa Anak':
        return 1 if value <= 72 else 2 if value <= 99 else 3 if value <= 149 else 4 if value <= 200 else 5
    elif persona == 'Pasangan Bekerja dengan Anak':
        return 1 if value <= 72 else 2 if value <= 99 else 3 if value <= 149 else 4 if value <= 200 else 5

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
fasilitas_lokasi = ['SCHOOL', 'HOSPITAL', 'MARKET', 'TRANSPORT']

def process_facilities(row):
    fac = str(row.get('facilities_clean', '')).upper().split()
    ent = str(row.get('entity_clean', '')).upper().split()

    facilities = {
        'facility_' + f.lower().replace(" ", "_"): int(f in fac)
        for f in fasilitas_hunian
    }
    entities = {e.lower(): int(e in ent) for e in fasilitas_lokasi}

    return pd.Series({**facilities, **entities})


def build_user_input(row):
    return {
        'building_area': row.get('building_area', 0),
        'bedrooms': row.get('bedrooms', 0),
        'bathrooms': row.get('bathrooms', 0),
        'floors': row.get('floors', 0),
        'type': row.get('type', 'rumah'),
        'hospital': row.get('hospital', 0),
        'school': row.get('school', 0),
        'market': row.get('market', 0),
        'transport': row.get('transport', 0),
        'facility_ac': row.get('facility_ac', 0),
        'facility_carport': row.get('facility_carport', 0),
        'facility_garasi': row.get('facility_garasi', 0),
        'facility_garden': row.get('facility_garden', 0),
        'facility_stove': row.get('facility_stove', 0),
        'facility_oven': row.get('facility_oven', 0),
        'facility_refrigerator': row.get('facility_refrigerator', 0),
        'facility_microwave': row.get('facility_microwave', 0),
        'facility_pam': row.get('facility_pam', 0),
        'facility_water_heater': row.get('facility_water_heater', 0),
        'facility_gordyn': row.get('facility_gordyn', 0),
    }

def calculate_final_score(user_input, persona):
    scores, category_cf, category_sf = {}, {}, {}

    for key in ideal_scores[persona]:
        input_key = f'facility_{key}' if key in ['ac', 'carport', 'garasi', 'garden', 'stove', 'oven',
                                                 'refrigerator', 'microwave', 'pam', 'water_heater', 'gordyn'] else key
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

# === Load Data ===
df = pd.read_csv("hasil_cbrs.csv")
original_columns = df.columns.tolist()
df['persona'] = df['best_persona_match'].map(persona_map)
df = pd.concat([df, df.apply(process_facilities, axis=1)], axis=1)

# === Score Each Property ===
df['final_score'] = df.apply(
    lambda row: calculate_final_score(build_user_input(row), row['persona']), axis=1
)

# === Finalize, Sort, and Output Cleaned Results ===

# 1. Create the list of columns for the final output file.
#    This includes all original columns plus the new 'final_score'.
final_output_columns = original_columns + ['final_score']

# 2. Create the final DataFrame with only the desired columns, dropping the intermediates.
df_final_output = df[final_output_columns]

# 3. Sort this clean DataFrame by the final_score in descending order.
df_sorted = df_final_output.sort_values(by='final_score', ascending=False)

# 4. Define the output file path and save the final, cleaned result.
output_filepath = Path('hasil_cbrs_with_scores.csv')
output_filepath.parent.mkdir(parents=True, exist_ok=True)
df_sorted.to_csv(output_filepath, index=False)

print(f"\n✅ All properties with scores have been saved to '{output_filepath}'")
print("The output file contains only the original columns plus the 'final_score'.")