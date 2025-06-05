# --- GAP to Weighted Score ---
def gap_to_weighted_score(gap):
    gap = abs(gap)
    return max(1, 5 - gap)  # gap: 0→5, 1→4, 2→3, 3→2, 4+→1

# --- User Input Example ---
user_input = {
    'building_area': 250,
    'bedrooms': 3,
    'bathrooms': 2,
    'floors': 2,
    'type': 'rumah',
    'hospital': 1,
    'school': 1,
    'market': 1,
    'transport': 1,
    'facility_ac': 1,
    'facility_carport': 1,
    'facility_garasi': 1,
    'facility_garden': 1,
    'facility_stove': 1,
    'facility_oven': 1,
    'facility_refrigerator': 1,
    'facility_microwave': 1,
    'facility_pam': 1,
    'facility_water_heater': 1,
    'facility_gordyn': 1
}

# --- Scoring Functions ---

# --- Karakteristik Hunian (Bobot: 40%) ---
def score_building_area(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value <= 72 else 4 if value <= 99 else 3 if value <= 149 else 2 if value <= 200 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 1 if value <= 72 else 2 if value <= 99 else 3 if value <= 149 else 4 if value <= 200 else 5
    elif persona == 'Berkeluarga dengan Anak':
        return 1 if value <= 72 else 2 if value <= 99 else 3 if value <= 149 else 4 if value <= 200 else 5

def score_bedrooms(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value <= 1 else 3 if value == 2 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value <= 2 else 3 if value == 3 else 2
    elif persona == 'Berkeluarga dengan Anak':
        return 1 if value <= 1 else 3 if value == 2 else 5

def score_bathrooms(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 3 if value == 2 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 3 if value == 2 else 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 1 if value <= 1 else 3 if value == 2 else 5

def score_floors(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 3 if value == 2 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 3 if value == 2 else 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 1 if value == 1 else 3 if value == 2 else 5

def score_type(value, persona):
    val = value.lower()
    return 5 if (persona == 'Individu Lajang' and val == 'apartemen') or \
                (persona != 'Individu Lajang' and val == 'rumah') else 1

# --- Fasilitas Lokasi Sekitar (Bobot: 30%) ---

def score_hospital(value, persona):
    if persona == 'Individu Lajang':
        return 3 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_school(value, persona):
    if persona == 'Individu Lajang':
        return 3 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 3 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_market(value, persona):
    if persona == 'Individu Lajang':
        return 3 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 3 if value == 1 else 1
    
def score_mall(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 3 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 3 if value == 1 else 1
    
def score_transport(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 3 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 3 if value == 1 else 1
    
# --- Fasilitas Hunian (Bobot: 30%) ---

def score_ac(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_carport(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_garasi(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_garden(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_stove(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_oven(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_refrigerator(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_microwave(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_pam(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_water_heater(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga dengan Anak':
        return 5 if value == 1 else 1
    
def score_gordyn(value, persona):
    if persona == 'Individu Lajang':
        return 5 if value == 0 else 1
    elif persona == 'Berkeluarga tanpa Anak':
        return 5 if value == 1 else 1
    elif persona == 'Berkeluarga dengan Anak':
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
    'Berkeluarga tanpa Anak': {
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
    'Berkeluarga dengan Anak': {
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
    'Berkeluarga tanpa Anak': {
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
    'Berkeluarga dengan Anak': {
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

# === CF/SF Weights ===
cf_weight = 0.6
sf_weight = 0.4

category_weights = {
    'Karakteristik Hunian': 0.4,
    'Fasilitas Hunian': 0.3,
    'Fasilitas Lokasi': 0.3
}

# === Evaluation ===
personas = list(ideal_scores.keys())
results = {}

for persona in personas:
    scores = {}
    gaps = {}
    weighted = {}
    category_cf = {}
    category_sf = {}

    # --- Compute Raw and Weighted Scores ---
    for key in ideal_scores[persona].keys():
        input_key = key
        if key.startswith('facility_'):
            input_key = key
        elif key in ['ac', 'carport', 'garasi', 'garden', 'stove', 'oven', 'refrigerator',
                     'microwave', 'pam', 'water_heater', 'gordyn']:
            input_key = f'facility_{key}'

        value = user_input.get(input_key, 0)
        score_func = globals().get(f"score_{key}", lambda v, p: 1)
        score = score_func(value, persona)
        scores[key] = score

        gap = score - ideal_scores[persona][key]
        wg = gap_to_weighted_score(gap)
        gaps[key] = gap
        weighted[key] = wg

        category, factor = criteria_structure[persona][key]
        if factor == 'CF':
            category_cf.setdefault(category, []).append(wg)
        else:
            category_sf.setdefault(category, []).append(wg)

    # --- Compute NCF/NSF & Weighted Category Scores ---
    category_scores = {}
    weighted_category_scores = {}
    for category in set(category_cf.keys()).union(category_sf.keys()):
        ncf_list = category_cf.get(category, [])
        nsf_list = category_sf.get(category, [])
        ncf = sum(ncf_list) / len(ncf_list) if ncf_list else 0
        nsf = sum(nsf_list) / len(nsf_list) if nsf_list else 0
        final_cat_score = cf_weight * ncf + sf_weight * nsf
        category_scores[category] = {
            'NCF': ncf,
            'NSF': nsf,
            'Score': final_cat_score
        }
        if category in category_weights:
            weighted_category_scores[category] = final_cat_score * category_weights[category]

    # --- Aggregate Final Score ---
    final_score = sum(weighted_category_scores.values())

    results[persona] = {
        'raw_scores': scores,
        'gaps': gaps,
        'weighted': weighted,
        'category_scores': category_scores,
        'weighted_category_scores': weighted_category_scores,
        'final_score': final_score
    }

# --- Output Results ---
print("\n=== Ranking Result ===")
ranking = sorted(results.items(), key=lambda x: x[1]['final_score'], reverse=True)
for i, (persona, data) in enumerate(ranking, start=1):
    print(f"\n#{i}: {persona}")
    print(f"Final Score: {data['final_score']:.2f}")
    for cat, val in data['category_scores'].items():
        print(f"  {cat}: NCF={val['NCF']:.2f}, NSF={val['NSF']:.2f}, Score={val['Score']:.2f}")
