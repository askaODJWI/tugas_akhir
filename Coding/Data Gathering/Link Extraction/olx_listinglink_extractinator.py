from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from tqdm import tqdm
import time
import csv

# Initialize WebDriver instance
driver = webdriver.Edge()

# Initialize an empty list to store the extracted links
listing_links = []

# Function to extract listing links from a district URL
def extract_listing_links(url, district_info):
    try:
        driver.get(url)
        time.sleep(5)  # Allow some time for the page to load
        
        # Attempt to find any listings on the page
        try:
            driver.find_element(By.XPATH, '//li[@data-aut-id="itemBox" and contains(@class, "_1DNjI")]')
        except NoSuchElementException:
            print(f"No listings found in {district_info}. Skipping...")
            return False  # No listings, skip this URL

        # Load all the results by clicking "Load More" until the button no longer exists
        while True:
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@data-aut-id="btnLoadMore"]'))
                )
                load_more_button.click()
                print("Clicked 'Load More'")
                time.sleep(2)
            except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                print("No more 'Load More' button or an error occurred. Assuming all listings are loaded.")
                break

        # Find all the <li> elements that contain the listings
        listings = driver.find_elements(By.XPATH, '//li[@data-aut-id="itemBox" and contains(@class, "_1DNjI")]')
        total_listings = len(listings)
        print(f"Found {total_listings} listings in {district_info}.")

        for listing in tqdm(listings, desc=f"Extracting Links for {district_info}", unit="listing"):
            try:
                # Find the <a> tag inside each <li> element and extract the href attribute
                link_element = listing.find_element(By.TAG_NAME, 'a')
                listing_url = link_element.get_attribute('href')
                
                # Store the link along with the district information
                listing_links.append({
                    'Nation': district_info['Nation'],
                    'Province': district_info['Province'],
                    'City': district_info['City'],
                    'District': district_info['District'],
                    'Listing URL': listing_url
                })

            except Exception as e:
                print(f"Error extracting listing link: {e}")
                continue
        return True  # Listings were found and processed
    except Exception as e:
        print(f"Error extracting links from {district_info['District URL']}: {e}")
        return False

# Main function to read location data and extract links
def main():
    # Open and read the location_data.csv file
    with open('level3links.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        location_data = [row for row in reader]

    # Iterate through each row in the location data (each district URL)
    for district_info in location_data:
        url = district_info['District URL']
        print(f"Processing {district_info['District']} ({url})")
        
        # Extract listing links for the current district
        extracted = extract_listing_links(url, district_info)
        if not extracted:
            print(f"Skipping {district_info['District']} due to no listings.")
    
    # Write the extracted listing links to the extracted_listing_links.csv file
    with open('listingslinksurabaya.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Nation', 'Province', 'City', 'District', 'Listing URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in listing_links:
            writer.writerow(data)

    print("All listings have been extracted and saved to extracted_listing_links.csv.")

# Run the script
if __name__ == "__main__":
    main()
    driver.quit()
