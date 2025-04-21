from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from dateparser import parse
from tqdm import tqdm
import time
import csv
import re

# Set up Edge WebDriver
options = Options()
options.add_argument("--inprivate")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-logging")
# options.add_argument("--headless")

driver = webdriver.Edge(options=options)

def extract_id_from_url(url):
    pattern = r'-iid-(\d+)$'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_nested_value(data_dict, keys, default=None):
    for key in keys:
        if isinstance(data_dict, list):
            try:
                data_dict = data_dict[key]
            except (IndexError, TypeError):
                return default
        else:
            data_dict = data_dict.get(key, default)
            if data_dict is default:
                return default
    return data_dict or default

def get_data(app_data, ads_ID, data_type, key_name=None, location_type=None):
    # Handle "location" extraction
    if data_type == "location" and location_type:
        address_components = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "metadata", "locations", 0, "tree", 0, "addressComponents"], [])
        for component in address_components:
            if component.get("type") == location_type:
                return component.get("name", None)
        return None

    # Handle "images" extraction
    elif data_type == "images":
        images = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "images"], [])
        return [image.get("url") for image in images if 'url' in image]

    # Handle "parameters" extraction
    elif data_type == "parameters" and key_name:
        parameters = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "parameters"], [])
        for param in parameters:
            if param.get("key_name").lower() == key_name.lower():
                if param.get("type") == "single":
                    value = param.get("value_name", None)
                    if key_name.lower() == "sertifikasi":
                        if value and "shm" in value.lower():
                            return "SHM"
                        return None
                    return value
                elif param.get("type") == "multi":
                    values = [value.get("value_name") for value in param.get("values", [])]
                    return values[0] if len(values) == 1 else values
        return None
    
    # If none of the cases match, return None
    return None

def get_seller_name(app_data, ads_ID):
    seller_id = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "user_id"])
    return get_nested_value(app_data, ["states", "users", "elements", seller_id, "name"])

def extract_app_data(script_tags):
    retries = 3
    for script in script_tags:
        try:
            script_content = script.get_attribute('innerHTML')
            if 'window.__APP' in script_content:
                driver.execute_script(script_content)
                return driver.execute_script("return window.__APP;")
        except StaleElementReferenceException:
            if retries > 0:
                retries -= 1
                time.sleep(1)
                continue
            else:
                print("Stale element, retries exhausted")
                return None
    return None

def split_sentences(description):
    # Split by new lines
    sentences = description.splitlines()
    
    # Remove leading/trailing whitespace from each line
    sentences = [line.strip() for line in sentences if line.strip()]
    
    return sentences

def scrape_description(ads_description, kata_kunci_list, entity_type=None):
    # List of valid headings in Bahasa
    headings = [
        "Timur", "Tenggara", "Selatan", "Barat Daya", "Barat", "Barat Laut", 
        "Utara", "Timur Laut"
    ]
    
    if not isinstance(ads_description, list):  # Ensure ads_description is a list
        return None
    
    for kata_kunci in kata_kunci_list:
        # Pattern for each type of entity
        if entity_type == 'electricity':
            # Pattern for electricity, allows watt, kVA, etc., with flexible formatting
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*([\d.,]+)\s*(watt|va|kva|token|w|wt|kwh)?'
        elif entity_type in ['garage', 'carport']:
            # Pattern for carport/garage, flexible with numbers and optional car words
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*(\d+)?\s*(mobil|mbl|cars?)?'
        elif entity_type == 'heading':
            # Pattern for heading, looks for specific directions or "kiblat/khiblat"
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*(.*?)(Timur|Tenggara|Selatan|Barat Daya|Barat Laut|Barat|Utara|Timur Laut|Kiblat|Khiblat)'
        else:
            # Generic pattern for any other entity
            pattern = rf'{re.escape(kata_kunci)}\s*[\:\.\-\s]*([\w\s\.,]+)'

        # Loop through each sentence in the description
        for sentence in ads_description:
            if isinstance(sentence, str) and kata_kunci.lower() in sentence.lower():  # Case-insensitive search
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    if entity_type == 'electricity':
                        # Clean and return the number for electricity, handling commas/periods
                        value_str = match.group(1).replace('.', '').replace(',', '')
                        return int(value_str)  # Return as integer
                    elif entity_type in ['garage', 'carport']:
                        # Extract the car capacity, default to 1 if no number is specified
                        value_str = match.group(1)
                        if value_str:
                            return int(value_str)  # Return the number of cars
                        else:
                            return 1  # Default to 1 if carport/garage is mentioned but no number is found
                    elif entity_type == 'heading':
                        # Extract the heading or special case for "kiblat/khiblat"
                        heading = match.group(2).capitalize()  # Get the direction found
                        if heading.lower() in ['kiblat', 'khiblat']:
                            return 'Barat'  # "Kiblat" or "Khiblat" means "Barat"
                        return heading  # Return the found heading
                    else:
                        # For general cases, return the matched value
                        value_str = match.group(1).strip()
                        val_split = value_str.split(" ")
                        return val_split[0]  # Return the first word/number found
    return None

# Function to count the presence of rooms (return 1 if found, otherwise 0)
def count_rooms(ads_description, keyword_list):
    for keyword in keyword_list:
        pattern = rf'(\d+)?\s*{re.escape(keyword)}'  # Look for a number before the room name
        for sentence in ads_description:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                number = match.group(1)
                if number:
                    return int(number)  # Return the number found before the keyword
                return 1  # If no number is found, return 1 (room is mentioned without quantity)
    return 0  # Return 0 if no match is found

def extract_all_ads_info(ads_description):
    # Define the keywords for each variable
    if not isinstance(ads_description, list) or not all(isinstance(sentence, str) for sentence in ads_description):
        ads_description = []
    
    keywords = {
        'garage': ['Garasi', 'Garage'],
        'carport': ['Carport', 'Carpot'],
        'electricity': ['Listrik', 'electricity', 'pln', 'listtrik'],
        'heading': ['Hadap', 'Orientasi'],
        'ruang_tamu': ['Ruang Tamu'],
        'ruang_makan': ['Ruang Makan'],
        'maid_bedroom': ['Kamar Pembantu'],
        'maid_bathroom': ['Kamar Mandi Pembantu'],
        'floors': ['Lantai']
    }
    
     # Extract values using scrape_description for each keyword list
    extracted_info = {}
    
    # Extract carport and garage and set default value to 0 if not found
    extracted_info['garage'] = scrape_description(ads_description, keywords['garage'], entity_type='garage') or 0
    extracted_info['carport'] = scrape_description(ads_description, keywords['carport'], entity_type='carport') or 0

    
    # Extract electricity capacity and house orientation
    extracted_info['electricity'] = scrape_description(ads_description, keywords['electricity'], entity_type='electricity') or None
    extracted_info['heading'] = scrape_description(ads_description, keywords['heading'], entity_type='heading') or None
    
    # Check for rooms (1 if mentioned, 0 if not)
    extracted_info['ruang_tamu'] = count_rooms(ads_description, keywords['ruang_tamu']) or 0
    extracted_info['ruang_makan'] = count_rooms(ads_description, keywords['ruang_makan']) or 0
    
    # Check for maid bedroom and bathroom
    extracted_info['maid_bedroom'] = count_rooms(ads_description, keywords['maid_bedroom']) or 0
    extracted_info['maid_bathroom'] = count_rooms(ads_description, keywords['maid_bathroom']) or 0
    
    # Extract number of floors (Lantai)
    extracted_info['floors'] = extract_floors(ads_description, keywords['floors'])

    # Now, search for any "ruang" that isn't explicitly "Ruang Tamu" or "Ruang Makan"
    other_rooms = []
    for sentence in ads_description:
        if isinstance(sentence, str) and "ruang" in sentence.lower() and "ruang tamu" not in sentence.lower() and "ruang makan" not in sentence.lower():
            other_rooms.append(sentence)
    
    # Count the number of "other" rooms
    if len(other_rooms) > 0:
        extracted_info['additional_rooms'] = 1  # At least one additional room found
    else:
        extracted_info['additional_rooms'] = 0  # No additional rooms found
    
    return extracted_info

def extract_floors(ads_description, keyword_list):
    for keyword in keyword_list:
        pattern = rf'(\d+)\s*{re.escape(keyword)}|{re.escape(keyword)}\s*[\:\-\s]*\d+'  # Look for "2 Lantai" or "Lantai: 2"
        for sentence in ads_description:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                number = match.group(1)
                if number:
                    return int(number)  # Extract the number of floors
                # If the pattern is "Lantai: 2" or similar, find the number at the end
                alt_match = re.search(rf'{re.escape(keyword)}\s*[\:\-\s]*(\d+)', sentence, re.IGNORECASE)
                if alt_match:
                    return int(alt_match.group(1))
    return 1  # Default to 1 if no floors are mentioned (single floor)

def parse_date(ads_postingdate):
    
    # Parse the date using dateparser
    date_obj = parse(ads_postingdate, languages=['id', 'en'])
    
    if date_obj:
        # Extract day, month, and year
        day = date_obj.day
        month = date_obj.month  # Get month name in Indonesian
        year = date_obj.year
        
        # Format the date as '20 Agustus 2024'
        formatted_date = f"{day} {date_obj.strftime('%B')} {year}"
        
        return formatted_date, month, year
    else:
        return None, None, None

def scrape_data_from_url(url):
    try:
        driver = webdriver.Edge(options=options)
        driver.get(url)
        retries = 3
        while retries > 0:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                retries = 0
            except TimeoutException:
                retries -= 1
                driver.refresh()
                if retries == 0:
                    print(f"Failed to load {url}")
                return
        time.sleep(3)
        
        ads_ID = extract_id_from_url(url)
        if not ads_ID:
            print("Failed to extract Ad ID from URL.")
            return None

        # Extract app data
        script_tags = driver.find_elements(By.TAG_NAME, 'script')
        app_data = extract_app_data(script_tags)
        
        if not app_data:
            print("Failed to extract app data.")
            return None

        ads_title = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "title"])
        ads_price = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "price", "value", "raw"])

        ads_type = get_data(app_data, ads_ID, "parameters", key_name="Tipe")
        ads_la = get_data(app_data, ads_ID, "parameters", key_name="Luas Tanah")
        ads_ba = get_data(app_data, ads_ID, "parameters", key_name="Luas Bangunan")
        ads_bed = get_data(app_data, ads_ID, "parameters", key_name="Kamar Tidur")
        ads_bath = get_data(app_data, ads_ID, "parameters", key_name="Kamar Mandi")
        ads_floors = get_data(app_data, ads_ID, "parameters", key_name="Lantai")
        ads_cert = get_data(app_data, ads_ID, "parameters", key_name="Sertifikasi")
        ads_address = get_data(app_data, ads_ID, "parameters", key_name="Alamat Lokasi")
        ads_facilities = get_data(app_data, ads_ID, "parameters", key_name="Fasilitas")
        ads_images = get_data(app_data, ads_ID, "images")
        
        ads_addressroad = get_data(app_data, ads_ID, "location", location_type="NEIGHBOURHOOD")
        ads_addresscity = get_data(app_data, ads_ID, "location", location_type="CITY")
        ads_addressdistrict = get_data(app_data, ads_ID, "location", location_type="NEIGHBOURHOOD")
        ads_addresssubdistrict = get_data(app_data, ads_ID, "location", location_type="NEIGHBOURHOOD")

        ads_description = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "description"])
        ads_postingdate = get_nested_value(app_data, ["states", "items", "elements", ads_ID, "created_at"])
        
        ads_poster = get_seller_name(app_data, ads_ID)
        
        # You can split the description into an array of sentences if needed
        if ads_description:
            ads_description = split_sentences(ads_description)
        else:
            ads_description = []
        
        ads_info = extract_all_ads_info(ads_description)
        
        ads_postingdate, ads_postingdate_month, ads_postingdate_year = parse_date(ads_postingdate)
        
        if ads_floors is None or ads_floors == '0':
            ads_floors = ads_info.get('floors')
        
        # Collect the scraped data in a dictionary
        scraped_data = {
            'url': url,
            'ads_id': ads_ID,
            'title': ads_title,
            'price': ads_price,
            'type': ads_type,
            'land_area': ads_la,
            'building_area': ads_ba,
            'bedrooms': ads_bed,
            'bathrooms': ads_bath,
            'maid_bedrooms': ads_info.get('maid_bedroom'),
            'maid_bathrooms': ads_info.get('maid_bathroom'),
            'ruang_tamu': ads_info.get('ruang_tamu'),
            'ruang_makan': ads_info.get('ruang_makan'),
            'additional_rooms': ads_info.get('additional_rooms'),
            'floors': ads_floors,
            'certificate': ads_cert,
            'address': ads_address,
            'address_road': ads_addressroad,
            'address_city': ads_addresscity,
            'address_district': ads_addressdistrict,
            'address_subdistrict': ads_addresssubdistrict,
            'garage_capacity': ads_info.get('garage'),
            'carport_capacity': ads_info.get('carport'),
            'facilities': ads_facilities,
            'description': ads_description,
            'posting_date': ads_postingdate,
            'posting_date_month':ads_postingdate_month,
            'posting_date_year': ads_postingdate_year,
            'poster': ads_poster,
            'electricity_capacity': ads_info.get('electricity'),
            'house_orientation': ads_info.get('heading'),
            'image_url': ads_images
        }
        return scraped_data
    
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return None
    
# Function to parallelize scraping using threading
def scrape_in_parallel(urls, max_threads=15):
    scraped_data = []
    
    with ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(scrape_data_from_url, url): url for url in urls}
        
        # Using tqdm to display progress
        for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping URLs"):
            url = futures[future]
            try:
                data = future.result()
                if data:
                    scraped_data.append(data)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    
    return scraped_data

def main():
    # Open the CSV file containing the list of URLs
    with open('batch4.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        listing_urls = [row[4] for row in reader]  # Assuming each row has only one column containing the URL
    
    # listing_urls = ['https://www.olx.co.id/item/rumah-premium-2-lantai-kemang-jakarta-iid-925431446',
    #                 'https://www.olx.co.id/item/rumah-3-lantai-design-minimalis-siap-huni-di-kemang-jakarta-selatan-iid-925420896',
    #                 'https://www.olx.co.id/item/dapatkan-rumah-755-juta-dengan-program-pesantren-keluarga-kprs-depok-iid-925513221',
    #                 'https://www.olx.co.id/item/termurah-rumah-mezzanine-di-citayam-lokasi-startegis-iid-924998644',
    #                 'https://www.olx.co.id/item/rumah-megangin-potongan-diskon-harga-15-dekat-stasiun-depok-lama-iid-925510719'
    #                 ]
    
    # Split the list into chunks and scrape in parallel
    num_threads = 15  # Number of threads (you can adjust this based on your system)
    scraped_data = scrape_in_parallel(listing_urls, max_threads=num_threads)
    
    # Write all scraped data into a CSV file
    with open('olx_housing_dataset_batch4_surabaya.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'url', 'ads_id', 'title', 'price', 'type', 'land_area', 'building_area',
            'bedrooms', 'bathrooms', 'maid_bedrooms', 'maid_bathrooms', 'ruang_tamu', 'ruang_makan', 'additional_rooms', 'floors', 'certificate', 'address', 'address_road', 
            'address_city', 'address_district', 'address_subdistrict', 'garage_capacity', 'carport_capacity', 'facilities', 
            'description', 'posting_date', 'posting_date_month', 'posting_date_year', 'poster', 'electricity_capacity', 'house_orientation', 'image_url'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in scraped_data:
            writer.writerow(data)
    
    print("CSV file created successfully with multiple listings.")
    driver.quit()

if __name__ == "__main__":
    main()
