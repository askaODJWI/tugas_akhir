import pandas as pd

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
    "MALL": 1
}

# Calculate scores for each persona
user_scores = {persona: match_score(user_input, criteria) for persona, criteria in ideal_personas.items()}
best_user_persona = max(user_scores, key=user_scores.get)


print(f"\n🔖 This user best fits the persona: **{best_user_persona}**")
print(f"🎯 Match score: {user_scores[best_user_persona] * 100:.1f}%\n")

print("📊 Detailed Match Scores:")
for persona, score in user_scores.items():
    print(f" - {persona}: {score * 100:.1f}%")