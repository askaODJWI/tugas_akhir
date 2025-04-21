import pandas as pd
import re
from dateparser import parse
from tqdm import tqdm

df = pd.read_csv("olx_housing_dataset_surabaya.csv")

# Your existing functions here
def scrape_description(ads_description, kata_kunci_list, entity_type=None):
    headings = [
        "Timur", "Tenggara", "Selatan", "Barat Daya", "Barat", "Barat Laut", 
        "Utara", "Timur Laut"
    ]
    
    # Ensure ads_description is a list
    if not isinstance(ads_description, list):
        return None
    
    for kata_kunci in kata_kunci_list:
        if entity_type == 'electricity':
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*([\d.,]+)\s*(watt|va|kva|token|w|wt|kwh)?'
        elif entity_type in ['garage', 'carport']:
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*(\d+)?\s*(mobil|mbl|cars?)?'
        elif entity_type == 'heading':
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*(.*?)(Timur|Tenggara|Selatan|Barat Daya|Barat Laut|Barat|Utara|Timur Laut|Kiblat|Khiblat)'
        elif entity_type == 'ownership':
            # Pattern to match "SHM" or "Sertifikat Hak Milik", "HGB" or "Hak Guna Bangunan"
            pattern = r'\b(SHM|Sertifikat Hak Milik|HGB|Hak Guna Bangunan)\b'
        else:
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*([\w\s\.,]+)'

        # Loop through each sentence in the description
        for sentence in ads_description:
            if isinstance(sentence, str) and kata_kunci.lower() in sentence.lower():
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    if entity_type == 'electricity':
                        value_str = match.group(1).replace('.', '').replace(',', '')
                        return int(value_str)
                    elif entity_type in ['garage', 'carport']:
                        value_str = match.group(1)
                        if value_str:
                            return int(value_str)
                        else:
                            return 1
                    elif entity_type == 'heading':
                        heading = match.group(2).capitalize()
                        if heading.lower() in ['kiblat', 'khiblat']:
                            return 'Barat'
                        return heading
                    elif entity_type == 'ownership':
                        # Return the appropriate abbreviation
                        ownership = match.group(1).lower()
                        if "shm" in ownership or "sertifikat hak milik" in ownership:
                            return "SHM"
                        elif "hgb" in ownership or "hak guna bangunan" in ownership:
                            return "HGB"
                    else:
                        value_str = match.group(1).strip()
                        val_split = value_str.split(" ")
                        return val_split[0]
    return None

def count_rooms(ads_description, keyword_list):
    for keyword in keyword_list:
        pattern = rf'(\d+)?\s*{re.escape(keyword)}'
        for sentence in ads_description:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                number = match.group(1)
                if number:
                    return int(number)
                return 1
    return 0

def parse_date(ads_postingdate):
    date_obj = parse(ads_postingdate, languages=['id', 'en'])
    
    if date_obj:
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year
        formatted_date = f"{day} {date_obj.strftime('%B')} {year}"
        return formatted_date, month, year
    else:
        return None, None, None
    
def extract_floors(ads_description, keyword_list):
    for keyword in keyword_list:
        # Pattern to match floors, including fractional (e.g., "1,5 Lantai" or "Lantai: 1,5")
        pattern = rf'(\d+[,.]?\d*)\s*{re.escape(keyword)}|{re.escape(keyword)}\s*[\:\-\s]*(\d+[,.]?\d*)'  # Match "2,5 Lantai" or "Lantai: 2,5"
        
        for sentence in ads_description:
            match = re.search(pattern, sentence, re.IGNORECASE)
            
            if match:
                # Check which group has the number
                number = match.group(1) if match.group(1) else match.group(2)
                
                # Replace commas with periods for proper float conversion
                if number:
                    number = number.replace(',', '.')
                    return float(number)  # Return as a float for fractional floors

    return 1  # Default to 1 if no floors are mentioned (single floor)

df['floors'] = df['floors'].astype(float)

# Iterate over the "description" column and perform any operations you want
# Iterate over the rows to process the 'description' column
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
    description = eval(row['description'])  # Convert the string back to a list (since it's stored as a string in the CSV)
    property_type = row['type']  # Assuming the 'type' column stores property types like "Apartemen"

    # Extract electricity capacity
    df.at[index, 'electricity_capacity'] = scrape_description(description, ['Listrik', 'Daya Listrik'], entity_type='electricity')

    # Extract garage capacity
    df.at[index, 'garage_capacity'] = scrape_description(description, ['Garasi'], entity_type='garage')

    # Extract carport capacity
    df.at[index, 'carport_capacity'] = scrape_description(description, ['Carport'], entity_type='carport')

    # Extract house orientation/heading
    df.at[index, 'house_orientation'] = scrape_description(description, ['Arah', 'Orientasi'], entity_type='heading')
    
    # Exctract ownership type
    df.at[index, 'certificate'] = scrape_description(description, ['Hak Milik', 'Sertifikat', 'Hak', 'SHM', 'HGB'], entity_type='ownership')

    # Extract additional rooms
    other_rooms = count_rooms(description, ['Ruang', 'Kamar', 'Dapur', 'Gudang'])
    if other_rooms > 0:
        df.at[index, 'additional_rooms'] = 1  # At least one 'other' room found
    else:
        df.at[index, 'additional_rooms'] = 0  # No additional 'other' rooms found

    # Parse the posting date
    formatted_date, posting_month, posting_year = parse_date(row['posting_date'])
    df.at[index, 'posting_date'] = formatted_date
    df.at[index, 'posting_date_month'] = posting_month
    df.at[index, 'posting_date_year'] = posting_year
    
    # Check if the property is an apartment
    if property_type == 'Apartemen':
        df.at[index, 'floors'] = 1  # Apartments can only have one floor
    else:
        # If not an apartment, extract floors using the 'extract_floors' function
        df.at[index, 'floors'] = extract_floors(description, ['Lantai'])

# Save the updated DataFrame back to a new CSV file
output_file = "updated_olx_housing_dataset_surabaya.csv"
df.to_csv(output_file, index=False)

print(f"Updated CSV saved to {output_file}")