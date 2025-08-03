import pandas as pd
import random

# ===================================================================================
# KONFIGURASI PROFIL BERDASARKAN TINGKAT KECOCOKAN
# ===================================================================================
# Berdasarkan analisis file ProfileMatching.py, nilai-nilai berikut ini
# dikelompokkan untuk menghasilkan skor yang mendekati persentase target.
# PERBAIKAN: Semua atribut yang diperlukan kini memiliki nilai untuk setiap tingkat kualitas.

PROFILES = {
    'Individu Lajang': {
        # Karakteristik Hunian
        'type':          {'best': 'apartemen', 'good': 'apartemen', 'avg': 'rumah',   'bad': 'rumah',   'worst': 'rumah'},
        'building_area': {'best': 70,  'good': 90,  'avg': 140, 'bad': 180, 'worst': 250},
        'bedrooms':      {'best': 1,   'good': 1,   'avg': 2,   'bad': 2,   'worst': 3},
        'bathrooms':     {'best': 1,   'good': 1,   'avg': 2,   'bad': 2,   'worst': 3},
        'floors':        {'best': 1,   'good': 1,   'avg': 2,   'bad': 2,   'worst': 3},
        # Fasilitas Lokasi
        'HOSPITAL':      {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'SCHOOL':        {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'MARKET':        {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'MALL':          {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'TRANSPORT':     {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        # Fasilitas Hunian (1=punya, 0=tidak punya)
        'facilities': {
            'best':  ["AC", "STOVE", "REFRIGERATOR", "PAM"],
            'good':  ["AC", "STOVE"],
            'avg':   ["AC", "CARPORT", "GARDEN"], # Campuran ideal dan tidak ideal
            'bad':   ["CARPORT", "GARASI", "GARDEN"],
            'worst': ["CARPORT", "GARASI", "GARDEN", "OVEN", "MICROWAVE", "WATER HEATER", "GORDYN"]
        }
    },
    'Pasangan Bekerja tanpa Anak': {
        # Karakteristik Hunian
        'type':          {'best': 'rumah', 'good': 'rumah', 'avg': 'apartemen', 'bad': 'apartemen', 'worst': 'apartemen'},
        'building_area': {'best': 150, 'good': 120, 'avg': 72, 'bad': 50,  'worst': 30},
        'bedrooms':      {'best': 2,   'good': 2,   'avg': 3,  'bad': 4,   'worst': 4},
        'bathrooms':     {'best': 1,   'good': 1,   'avg': 2,  'bad': 2,   'worst': 3},
        'floors':        {'best': 1,   'good': 1,   'avg': 2,  'bad': 2,   'worst': 3},
        # Fasilitas Lokasi
        'HOSPITAL':      {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'SCHOOL':        {'best': 1, 'good': 1, 'avg': 0, 'bad': 0, 'worst': 0},
        'MARKET':        {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'MALL':          {'best': 1, 'good': 1, 'avg': 0, 'bad': 0, 'worst': 0},
        'TRANSPORT':     {'best': 1, 'good': 1, 'avg': 0, 'bad': 0, 'worst': 0},
        # Fasilitas Hunian
        'facilities': {
            'best':  ["AC", "STOVE", "REFRIGERATOR", "PAM", "CARPORT", "GARASI", "OVEN"],
            'good':  ["AC", "CARPORT", "STOVE", "REFRIGERATOR"],
            'avg':   ["AC", "CARPORT", "GARDEN", "MICROWAVE"], # Campuran
            'bad':   ["GARDEN", "MICROWAVE"],
            'worst': ["GARDEN", "MICROWAVE", "WATER HEATER", "GORDYN"]
        }
    },
    'Pasangan Bekerja dengan Anak': {
        # Karakteristik Hunian
        'type':          {'best': 'rumah', 'good': 'rumah', 'avg': 'apartemen', 'bad': 'apartemen', 'worst': 'apartemen'},
        'building_area': {'best': 150, 'good': 149, 'avg': 100, 'bad': 70,  'worst': 50},
        'bedrooms':      {'best': 3,   'good': 4,   'avg': 2,   'bad': 1,   'worst': 1},
        'bathrooms':     {'best': 3,   'good': 2,   'avg': 2,   'bad': 1,   'worst': 1},
        'floors':        {'best': 3,   'good': 2,   'avg': 2,   'bad': 1,   'worst': 1},
        # Fasilitas Lokasi
        'HOSPITAL':      {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'SCHOOL':        {'best': 1, 'good': 1, 'avg': 1, 'bad': 0, 'worst': 0},
        'MARKET':        {'best': 1, 'good': 0, 'avg': 1, 'bad': 0, 'worst': 0},
        'MALL':          {'best': 1, 'good': 0, 'avg': 1, 'bad': 0, 'worst': 0},
        'TRANSPORT':     {'best': 1, 'good': 0, 'avg': 1, 'bad': 0, 'worst': 0},
        # Fasilitas Hunian
        'facilities': {
            'best':  ["AC", "STOVE", "REFRIGERATOR", "PAM", "CARPORT", "GARASI", "OVEN", "GARDEN", "MICROWAVE", "WATER HEATER"],
            'good':  ["AC", "CARPORT", "GARASI", "GARDEN", "STOVE"],
            'avg':   ["AC", "GARDEN", "STOVE"],
            'bad':   ["AC"],
            'worst': []
        }
    }
}


def generate_targeted_case(persona_name, percentage):
    """Membuat satu test case yang menargetkan persentase kecocokan tertentu."""
    profile = PROFILES[persona_name]
    case = {}

    # Tentukan tingkat kualitas berdasarkan persentase
    if percentage == 100: level_map = {'best': 1.0}
    elif percentage == 75: level_map = {'best': 0.7, 'good': 0.3}
    elif percentage == 50: level_map = {'good': 0.5, 'avg': 0.5}
    elif percentage == 25: level_map = {'avg': 0.4, 'bad': 0.6}
    elif percentage == 10: level_map = {'bad': 0.5, 'worst': 0.5}
    else: level_map = {'worst': 1.0} # 0%

    # Pilih nilai untuk setiap atribut
    for key, values in profile.items():
        chosen_level = random.choices(list(level_map.keys()), weights=list(level_map.values()), k=1)[0]
        level_value = values.get(chosen_level)
        case[key] = level_value
            
    # Koreksi kecil untuk memastikan kasus 0% dan 100% lebih murni
    if percentage == 100:
        for key, values in profile.items(): case[key] = values['best']
    if percentage == 0:
        for key, values in profile.items(): case[key] = values['worst']
    
    # Penambahan Logika land_area
    if case['type'] == 'rumah':
        case['land_area'] = int(case['building_area'] * 1.2)
    else: # 'apartemen'
        case['land_area'] = case['building_area']
        
    return case


def generate_random_case(persona_name):
    """Membuat satu test case dengan nilai acak sepenuhnya."""
    profile = PROFILES[persona_name]
    case = {}
    for key, values in profile.items():
        random_level = random.choice(list(values.keys()))
        level_value = values[random_level]
        case[key] = level_value
        
    # Penambahan Logika land_area
    if case['type'] == 'rumah':
        case['land_area'] = int(case['building_area'] * 1.2)
    else: # 'apartemen'
        case['land_area'] = case['building_area']

    return case


# --- Main Script ---

all_test_cases = []
personas = list(PROFILES.keys())
target_percentages = [100, 75, 50, 25, 10, 0]
num_per_persona = 100

for persona_name in personas:
    # 1. Buat test case yang ditargetkan
    for percentage in target_percentages:
        case_data = generate_targeted_case(persona_name, percentage)
        case_data['persona'] = persona_name
        case_data['test_case_type'] = f'Target {percentage}%'
        all_test_cases.append(case_data)
        
    # 2. Buat sisa test case secara acak untuk melengkapi 100
    num_random_to_generate = num_per_persona - len(target_percentages)
    for i in range(num_random_to_generate):
        case_data = generate_random_case(persona_name)
        case_data['persona'] = persona_name
        case_data['test_case_type'] = f'Random_{i+1}'
        all_test_cases.append(case_data)


# --- Konversi ke DataFrame dan Simpan ---

df = pd.DataFrame(all_test_cases)

# Memperbarui daftar kolom yang diperlukan
required_cols = ['persona', 'test_case_type', 'type', 'land_area', 'building_area', 'bedrooms', 'bathrooms', 'floors', 
                 'HOSPITAL', 'SCHOOL', 'MARKET', 'MALL', 'TRANSPORT', 'facilities']
for col in required_cols:
    if col not in df.columns:
        df[col] = 0 # Default value

# Konversi list fasilitas menjadi string
df['facilities'] = df['facilities'].apply(lambda x: ', '.join(x) if isinstance(x, list) else "")
df = df[required_cols] # Urutkan kolom

# Simpan ke CSV
csv_filename = 'persona_test_cases_advanced.csv'
df.to_csv(csv_filename, index=False)

print(f"✅ Berhasil membuat {len(all_test_cases)} test case dan menyimpannya ke '{csv_filename}'")
