from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.edge.options import Options
import time
import csv

# Set up Edge WebDriver
options = Options()
options.add_argument("--inprivate")

driver = webdriver.Edge(options=options)

# Open the page or load the HTML file (you can replace it with a local file using "file://path_to_file")
driver.get('https://www.olx.co.id/dijual-rumah-apartemen_c5158')  # Replace with the actual URL

# Set up an explicit wait (up to 10 seconds)
wait = WebDriverWait(driver, 10)

# Create and open the CSV file in write mode
csv_file = open('level2links.csv', mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)

# Write the header for the CSV file
csv_writer.writerow(['Sub-location', 'URL'])

# Function to clean the 'data-aut-id' by removing 'location_'
def clean_data_aut_id(data_aut_id):
    return data_aut_id.replace('location_', '')

# Function to extract level 2 data (sub-location)
def extract_level_2_data(province_url):
    driver.get(province_url)
    time.sleep(2)  # Small delay to ensure the page loads
    try:
        ul_level_2 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-aut-id="ulLevel_2"]')))
        li_elements_level_2 = ul_level_2.find_elements(By.TAG_NAME, 'li')

        for li_2 in li_elements_level_2:
            link_2 = li_2.find_element(By.TAG_NAME, 'a')
            data_aut_id_level_2 = clean_data_aut_id(link_2.get_attribute('data-aut-id'))  # Clean the sub-location name
            href_level_2 = link_2.get_attribute('href')

            # Sub-location: (Level 2)
            sub_location = data_aut_id_level_2
            print(f"Sub-location: {sub_location}, URL: {href_level_2}")

            # Write the sub-location and URL to the CSV file
            csv_writer.writerow([sub_location, href_level_2])

    except NoSuchElementException:
        print("No Sub-locations found.")
    except TimeoutException:
        print("Timeout while waiting for Level 2 data.")
    finally:
        # Navigate back to the previous page
        driver.back()
        time.sleep(2)  # Small delay to ensure the page loads

# Function to extract data and save into CSV
def extract_data(retrieved_provinces):
    # Define the provinces you want to visit
    provinces_to_visit = ["Jawa Timur"]

    # Store province URLs for later extraction
    province_urls = {}

    # Level 0 - Find 'ul[data-aut-id="ulLevel_0"]' for Nation
    ul_level_0 = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul[data-aut-id="ulLevel_0"]')))
    li_elements_level_0 = ul_level_0.find_elements(By.TAG_NAME, 'li')

    for li in li_elements_level_0:
        link = li.find_element(By.TAG_NAME, 'a')
        data_aut_id_level_0 = clean_data_aut_id(link.get_attribute('data-aut-id'))  # Clean the nation name
        href_level_0 = link.get_attribute('href')
        
        # Nation: (Level 0)
        nation = data_aut_id_level_0
        print(f"Nation: {nation}, URL: {href_level_0}")
        
        # Level 1 - Find 'ul[data-aut-id="ulLevel_1"]' for Province inside level 0's li
        try:
            ul_level_1 = li.find_element(By.CSS_SELECTOR, 'ul[data-aut-id="ulLevel_1"]')
            li_elements_level_1 = ul_level_1.find_elements(By.TAG_NAME, 'li')

            for li_1 in li_elements_level_1:
                link_1 = li_1.find_element(By.TAG_NAME, 'a')
                data_aut_id_level_1 = clean_data_aut_id(link_1.get_attribute('data-aut-id'))  # Clean the province name
                href_level_1 = link_1.get_attribute('href')

                # Province: (Level 1)
                province = data_aut_id_level_1
                if province in provinces_to_visit and province not in retrieved_provinces:
                    retrieved_provinces.add(province)
                    print(f"Retrieved Province: {province}, URL: {href_level_1}")

                    # Store the province URL for level 2 data extraction later
                    province_urls[province] = href_level_1

        except NoSuchElementException:
            print(f"No Provinces found under Nation: {nation}")
        except TimeoutException:
            print(f"Timeout while loading provinces for Nation: {nation}")

    # Check if all desired provinces have been retrieved
    if all(province in retrieved_provinces for province in provinces_to_visit):
        print("All desired provinces have been retrieved.")

        # Now, navigate to each province URL and extract level 2 data
        for province, url in province_urls.items():
            print(f"Extracting data for {province} at {url}")
            extract_level_2_data(url)  # Extract sub-locations (Level 2)

        return True  # Indicate that all provinces and sub-locations have been retrieved
    return False  # Indicate that some provinces are still pending

# Start the extraction process
retrieved_provinces = set()

try:
    indonesia_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@data-aut-id="location_Indonesia"]'))
        )
    indonesia_option.click()
    time.sleep(2)  # Small delay to ensure that the page updates to "Indonesia"
    
    # Keep extracting data until all desired provinces are retrieved
    while not extract_data(retrieved_provinces):
        print("Retrying to extract data...")
        time.sleep(2)  # Small delay before retrying

finally:
    # Close the browser and the CSV file after the task is complete
    csv_file.close()
    driver.quit()