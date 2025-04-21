import csv
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# Set up Edge WebDriver
options = Options()
options.add_argument("--inprivate")
driver = webdriver.Edge(options=options)

# Set up an explicit wait (up to 2 minutes for Level 3 data)
wait = WebDriverWait(driver, 120)

# Input CSV file (contains sub-location links)
input_csv_filename = "level2links.csv"

# Output CSV file (to save the extracted district info)
output_csv_filename = "level3links.csv"

# List of sub-locations to filter
desired_sub_locations = [
    "Surabaya Kota"
]

# Function to clean the 'data-aut-id' by removing 'location_'
def clean_data_aut_id(data_aut_id):
    return data_aut_id.replace('location_', '')

# Function to extract data for a specific URL (handles Nation, Province, City, District)
def extract_data(nation_url):
    driver.get(nation_url)
    time.sleep(2)  # Small delay to ensure the page loads
    with open(output_csv_filename, mode='a', newline='', encoding='utf-8') as output_csv_file:
        fieldnames = ['Nation', 'Province', 'City', 'District', 'District URL']
        writer = csv.DictWriter(output_csv_file, fieldnames=fieldnames)

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
                    print(f"  Province: {province}, URL: {href_level_1}")

                    # Level 2 - Find 'ul[data-aut-id="ulLevel_2"]' for City inside level 1's li
                    try:
                        ul_level_2 = li_1.find_element(By.CSS_SELECTOR, 'ul[data-aut-id="ulLevel_2"]')
                        li_elements_level_2 = ul_level_2.find_elements(By.TAG_NAME, 'li')

                        for li_2 in li_elements_level_2:
                            link_2 = li_2.find_element(By.TAG_NAME, 'a')
                            data_aut_id_level_2 = clean_data_aut_id(link_2.get_attribute('data-aut-id'))  # Clean the city name
                            href_level_2 = link_2.get_attribute('href')

                            # City: (Level 2)
                            city = data_aut_id_level_2
                            print(f"    City: {city}, URL: {href_level_2}")

                            # Level 3 - Find 'ul[data-aut-id="ulLevel_3"]' for District inside level 2's li
                            try:
                                ul_level_3 = li_2.find_element(By.CSS_SELECTOR, 'ul[data-aut-id="ulLevel_3"]')
                                li_elements_level_3 = ul_level_3.find_elements(By.TAG_NAME, 'li')

                                for li_3 in li_elements_level_3:
                                    link_3 = li_3.find_element(By.TAG_NAME, 'a')
                                    data_aut_id_level_3 = clean_data_aut_id(link_3.get_attribute('data-aut-id'))  # Clean the district name
                                    href_level_3 = link_3.get_attribute('href')

                                    # District: (Level 3)
                                    district = data_aut_id_level_3
                                    print(f"      District: {district}, URL: {href_level_3}")

                                    # Write the data to the CSV file
                                    writer.writerow({
                                        'Nation': nation,
                                        'Province': province,
                                        'City': city,
                                        'District': district,
                                        'District URL': href_level_3
                                    })

                            except NoSuchElementException:
                                print(f"No Districts found under City: {city}")
                            except TimeoutException:
                                print(f"Timeout while waiting for Districts under City: {city}")

                    except NoSuchElementException:
                        print(f"No Cities found under Province: {province}")

            except NoSuchElementException:
                print(f"No Provinces found under Nation: {nation}")

# Read the input CSV file and start extraction for each sub-location URL
def read_input_and_extract():
    with open(input_csv_filename, mode='r', newline='', encoding='utf-8') as input_csv_file:
        reader = csv.DictReader(input_csv_file)

        for row in reader:
            sub_location = row['Sub-location']
            sub_location_url = row['URL']

            # Check if the sub-location is in the desired list
            if sub_location in desired_sub_locations:
                print(f"Processing Sub-location: {sub_location}, URL: {sub_location_url}")
                
                # Extract data for this sub-location
                extract_data(sub_location_url)
            else:
                print(f"Skipping Sub-location: {sub_location}, not in desired list.")

# Start the extraction process
try:
    # Create the output CSV file and write the header
    with open(output_csv_filename, mode='w', newline='', encoding='utf-8') as output_csv_file:
        fieldnames = ['Nation', 'Province', 'City', 'District', 'District URL']
        writer = csv.DictWriter(output_csv_file, fieldnames=fieldnames)
        writer.writeheader()

    read_input_and_extract()  # Call the function to read input and start extraction
finally:
    # Close the browser after the task is complete
    driver.quit()
