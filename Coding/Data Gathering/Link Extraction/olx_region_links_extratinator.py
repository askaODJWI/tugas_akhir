from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

import time
import csv

# Initialize WebDriver
driver = webdriver.Edge()

# Navigate to the base URL
driver.get("https://www.olx.co.id/dijual-rumah-apartemen_c5158")

# Ensure "Indonesia" is selected after expanding the dropdown
try:
    indonesia_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@data-aut-id="location_Indonesia"]'))
    )
    indonesia_option.click()
    time.sleep(2)  # Small delay to ensure that the page updates to "Indonesia"
except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
    print("Error selecting 'Indonesia':", e)
    driver.quit()

# Define the regions and their corresponding sub-locations of interest
regions_of_interest = {
    "Jawa Barat": ["Bekasi Kota", "Depok Kota", "Bogor Kota"],
    "Jakarta D.K.I": "all",  # Extract all locations
    "Banten": ["Tangerang Selatan Kota", "Tangerang Kota"]
}

# Dictionary to store the final links
final_links = {}

# Function to navigate back to the "Indonesia" location page
def go_back_to_indonesia():
    try:
        indonesia_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@data-aut-id="location_Indonesia"]'))
        )
        indonesia_link.click()
        time.sleep(2)  # Small delay to ensure the page updates
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print("Error navigating back to 'Indonesia':", e)
        driver.quit()

# Function to extract Kecamatan links for a specific Kota (city)
def extract_kecamatan_links(city_name, city_link):
    driver.get(city_link)
    time.sleep(2)  # Wait for the page to load

    kecamatan_links = {}
    try:
        kecamatan_elements = driver.find_elements(By.XPATH, '//a[@rel and contains(@data-aut-id, "location") and contains(text(), "Kecamatan")]')
        for kecamatan in kecamatan_elements:
            name = kecamatan.text
            link = kecamatan.get_attribute('href')
            kecamatan_links[name] = link
    except (NoSuchElementException, TimeoutException) as e:
        print(f"Error extracting kecamatan links for city {city_name}: {e}")

    return kecamatan_links

# Function to extract links for a region
def extract_region_links(region_name, sub_locations=None):
    try:
        # Find the region element and click it
        region_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//a[@rel and contains(@data-aut-id, "location") and contains(text(), "{region_name}")]'))
        )
        region_link = region_element.get_attribute('href')
        region_element.click()
        time.sleep(2)
        
        # Extract sub-location links if applicable
        if sub_locations:
            sub_location_links = {}
            for sub_location in sub_locations:
                while True:
                    try:
                        sub_location_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, f'//a[@rel and contains(@data-aut-id, "location") and contains(text(), "{sub_location}")]'))
                        )
                        sub_location_link = sub_location_element.get_attribute('href')
                        sub_location_links[sub_location] = extract_kecamatan_links(sub_location, sub_location_link)
                        break
                    except StaleElementReferenceException as e:
                        print(f"StaleElementReferenceException for sub-location {sub_location}: {e}")
                        time.sleep(1)
            final_links[region_name] = sub_location_links
        else:
            # Extract all locations under this region
            sub_location_elements = driver.find_elements(By.XPATH, '//a[@rel and contains(@data-aut-id, "location")]')
            final_links[region_name] = {elem.text: elem.get_attribute('href') for elem in sub_location_elements}
        
        # Navigate back to the "Indonesia" location page
        go_back_to_indonesia()
    
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"Error finding region {region_name}: {e}")

# Iterate through the regions and extract the links
for region, sub_locations in regions_of_interest.items():
    if sub_locations == "all":
        extract_region_links(region)
    else:
        extract_region_links(region, sub_locations)

# Print the final links for verification
for region, cities in final_links.items():
    print(f"\nRegion: {region}")
    for city, kecamatans in cities.items():
        print(f"  City: {city}")
        for kecamatan, link in kecamatans.items():
            print(f"    Kecamatan: {kecamatan} -> Link: {link}")

# Close the WebDriver
driver.quit()

# Save the links to a CSV file
with open('olx_links_rumah.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['region', 'city', 'kecamatan', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for region, cities in final_links.items():
        for city, kecamatans in cities.items():
            for kecamatan, link in kecamatans.items():
                writer.writerow({'region': region, 'city': city, 'kecamatan': kecamatan, 'link': link})
