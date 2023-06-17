#import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from page_scraper import scrap_page, get_hash_of_page
from login import login
from pymongo import MongoClient
import config 

from datetime import datetime

def get_current_semester_year():
    now = datetime.now()
    
    # if the current month is between January and April, the year of the current semester is the previous year
    if now.month <= 4:
        return now.year - 1
    # if the current month is between October and December, the year of the current semester is the current year
    else:
        return now.year

import re

def is_desired_folder_name(folder_name):
    # If folder name contains Strings, it is not a desired folder
    if "archiv" in folder_name.lower() or "literatur" in folder_name.lower():
        return False
    

    # Get the current semester year
    current_year = get_current_semester_year()
    
    # Regular expression pattern to match the prefixes and year
    pattern = r'\b(?:WS|SS|SoSe|WiSe|Wintersemester|Winter Semester|Winter|Sommersemester|Sommer Semester|Summer Semester|Sommer|Summer)\s*(?:20)?(\d{2})\b'
    
    # Try to find the year in the folder name using regular expressions
    year_match = re.search(pattern, folder_name, re.IGNORECASE)
    if year_match:
        # Extract the last two digits of the year from the folder name
        folder_year_last_two_digits = int(year_match.group(1))
        
        # Convert to four digit year
        folder_year = folder_year_last_two_digits + 2000 if folder_year_last_two_digits < 50 else folder_year_last_two_digits + 1900
        
        # Check if the year in folder name is greater than or equal to the current semester year
        return folder_year >= current_year
    else:
        # If we can't find a year in the folder name, we can't determine if it's not current or next semester
        return True



# Connect to the MongoDB
client = MongoClient(config.MONGODB_URI, config.MONGODB_PORT)

# Select the database
db = client[config.MONGODB_DB]

# Select the collection within the database
folders_collection = db[config.MONGODB_COLLECTION_FOLDERS]


def crawl_website(driver, url, path="root//"):
    print(f"Processing {path}")
    # Check if url starts with https://www.studon.fau.de/
    if url is None or not url.startswith(config.BASE_URL):
        return None

    items = scrap_page(driver, url)

    hash = get_hash_of_page(driver=driver)
    # Object to store folder data
    folder = {
        "path": path,
        "hash": hash,
        "courses": [],
        "child_folders": []
    }
    
    # Process items from the current page
    for _, item_info in items.items():
        if item_info['is_folder']:
            # Ignore for now faculty folders not from technical faculty
            if path == "root//" and item_info['item_name'] != "5. Technische Fakultät":
                continue
            # Check if this is a relevant folder (current or next semester)
            if is_desired_folder_name(item_info['item_name']):
                # We need to go deeper into this folder
                sub_folder_id = crawl_website(driver, item_info['item_link'], path + item_info['item_name'] + "//")
                # Add the ObjectId of the sub-folder to the current folder
                folder['child_folders'].append(sub_folder_id)
        else:
            # This is a course, add it to the courses list in the folder object
            folder['courses'].append({
                "name": item_info['item_name'],
                "link": item_info['item_link'],
                "joinable": item_info['joinable']
            })
    
    # Insert the current folder into MongoDB and return its ObjectId
    result = folders_collection.insert_one(folder)
    return result.inserted_id


def main(is_headless=True):
    #Init Selenium
    options = Options()
    if is_headless:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Maximize the browser window
    driver.maximize_window()
    # Login to StudOn
    login(driver=driver)
    print("Successfully logged in to StudOn")
    print("Crawling website...")
    crawl_website(driver, config.START_PAGE_URL)
    # Now you have all items in the 'items' dictionary
    # You can store this dictionary in your database.
    # Make sure to handle database operations and exceptions here.
    # ...database code...

    # Don't forget to close the driver after you're done
    driver.quit()

if __name__ == "__main__":
    main()
