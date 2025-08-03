import pandas as pd

df_all_cases = pd.read_csv('results_profile_matching1.csv')

# Format Input Parameter kembali
def format_input_param_full(row):
    return f'''{{
"type": "{row["type"]}",
"land_area": {row["land_area"]},
"building_area": {row["building_area"]},
"bedrooms": {row["bedrooms"]},
"bathrooms": {row["bathrooms"]},
"floors": {row["floors"]},
"hospital": {row["HOSPITAL"]},
"school": {row["SCHOOL"]},
"market": {row["MARKET"]},
"mall": {row["MALL"]},
"transport": {row["TRANSPORT"]},
"facilities": "{row["facilities"]}"
}}'''

df_all_cases['Input Parameter'] = df_all_cases.apply(format_input_param_full, axis=1)
df_all_cases['Expected Results'] = df_all_cases['profile_target']
df_all_cases['Real Results'] = df_all_cases['predicted_persona']

# Buat Test ID & Test Case sesuai format yang diminta
count_dict_full = {"PA":0, "PB":0, "PC":0}

def custom_test_id_full(row):
    if row['profile_target'] == "Individu Lajang":
        prefix = "PA"
    elif row['profile_target'] == "Pasangan Bekerja tanpa Anak":
        prefix = "PB"
    else:
        prefix = "PC"
    count_dict_full[prefix] += 1
    return f"{prefix}{count_dict_full[prefix]}"

def custom_test_case_full(row):
    if row['profile_target'] == "Individu Lajang":
        return f"Profil A {row['level']}"
    elif row['profile_target'] == "Pasangan Bekerja tanpa Anak":
        return f"Profil B {row['level']}"
    else:
        return f"Profil C {row['level']}"

df_all_cases['Test ID'] = df_all_cases.apply(lambda row: custom_test_id_full(row), axis=1)
df_all_cases['Test Case'] = df_all_cases.apply(custom_test_case_full, axis=1)

# Final tabel sesuai format
final_full_excel = df_all_cases[['Test ID', 'Test Case', 'Input Parameter', 'Expected Results', 'Real Results']]

# Simpan ke Excel
full_excel_path = "Full_Profile_Matching_Test_Report.xlsx"
final_full_excel.to_excel(full_excel_path, index=False)
full_excel_path