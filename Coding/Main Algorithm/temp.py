import pandas as pd

# Load the dataset
df = pd.read_csv(r'C:\Users\madea\OneDrive\Documents\Kuliah\Semester 8\Tugas Akhir\Coding\Data Preprocessing\updated_jabodetabeksur_olx_housing_dataset_.csv')

# Filter for only 'Rumah' and 'Apartemen'
filtered_df = df[df['type'].isin(['Rumah', 'Apartemen'])]

# Select only relevant columns
selected_columns = ['type', 'land_area', 'building_area']

# Drop rows with missing values in land_area or building_area
filtered_df = filtered_df[selected_columns].dropna()

# Convert to numeric (if not already)
filtered_df['land_area'] = pd.to_numeric(filtered_df['land_area'], errors='coerce')
filtered_df['building_area'] = pd.to_numeric(filtered_df['building_area'], errors='coerce')

# Group by type and describe statistics
stats = filtered_df.groupby('type')[['land_area', 'building_area']].describe()

print(stats)