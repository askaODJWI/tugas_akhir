from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json

options = Options()
options.add_argument("--inprivate")  # InPrivate mode (similar to Incognito)
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--no-sandbox")  # Avoid sandboxing issues
options.add_argument("--disable-logging")  # Suppress logging
# options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Chrome(options=options)

try:
    # Open the webpage
    driver.get("https://www.olx.co.id/item/full-furnished-apartemen-pondok-klub-villa-jakarta-selatanbestview-iid-846771718")

    # Wait for the page to load completely
    time.sleep(5)  # You can adjust the sleep time as needed

    # Find all <script> tags on the page
    script_tags = driver.find_elements(By.TAG_NAME, 'script')

    # Search for the script containing 'window.__APP'
    for script in script_tags:
        script_content = script.get_attribute('innerHTML')
        if 'window.__APP' in script_content:
           # Execute the script content in the browser's JavaScript context
            driver.execute_script(script_content)

            # Now you can access the window.__APP object directly using execute_script
            app_data = driver.execute_script("return window.__APP;")
            
            with open('script.json', 'w', encoding='utf-8') as json_file:
                json.dump(app_data, json_file, ensure_ascii=False, indent=4)

            print("Script containing 'window.__APP' has been saved to script.json")
            break
    else:
        print("No script containing 'window.__APP' found.")

finally:
    # Close the browser
    driver.quit()