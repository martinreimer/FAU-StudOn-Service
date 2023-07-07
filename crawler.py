#import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scraper import page_scrap
from login import login
from pymongo import MongoClient
import config 
import re
from datetime import datetime
import hashlib
import argparse


#region: CONSTANTS
# Connect to the MongoDB
CLIENT = MongoClient(config.MONGODB_URI, config.MONGODB_PORT)

# Select the database
DB = CLIENT[config.MONGODB_DB]

# Select the collection within the database
FOLDERS_COLLECTION = DB[config.MONGODB_COLLECTION_FOLDERS]
FOLDER_CHANGES_COLLECTION = DB[config.MONGODB_COLLECTION_FOLDER_CHANGES]

#endregion
# region: Helper functions
def get_current_semester_year():
    '''
    Get the year of the current semester
    :return: the year of the current semester
    '''
    now = datetime.now()
    
    # if the current month is between January and April, the year of the current semester is the previous year
    if now.month <= 4:
        return now.year - 1
    # if the current month is between October and December, the year of the current semester is the current year
    else:
        return now.year

def is_relevant_folder(folder_name):
    '''
    Check if the folder is relevant 
    - no older semesters than the current one
    - no archive folders
    - no literature folders
    :param folder_name: the name of the folder
    :return: True if the folder is relevant, False otherwise
    - 
    '''
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

def calculate_hash(content):
    '''
    Calculate the hash of the content using SHA-256
    :param content: the content to hash
    :return: the hash value'''
    return hashlib.sha256(content).hexdigest()

def get_hash_of_page(driver):
    '''
    Get the hash of the current page
    - calculate hash of the page: mainscrolldiv contains all item information
    - return the hash value
    '''
    main_page_part = driver.find_element(By.CLASS_NAME, "ilTabsContentOuter")
    page_hash_value = calculate_hash(main_page_part.text.encode('utf-8'))
    return page_hash_value

def check_folder_changes(old_items_dict, new_items_dict):
    '''
    Check for changes in the folder
    - added items
    - removed items: currently not interesting
    - changed items: track if course was not joinable but now got joinable
    :param old_items_dict: dictionary containing the old items
    :param new_items_dict: dictionary containing the new items
    :return: a tuple containing the added and changed items'''
    # Identify added items
    added_items = [item for item in new_items_dict if item not in old_items_dict]
    
    # Identify removed items
    #removed_items = [item for item in old_items_dict if item not in new_items_dict]
    
    # Identify changed items
    changed_items = []
    for item in new_items_dict:
        if item in old_items_dict:
            old_item = old_items_dict[item]
            new_item = new_items_dict[item]
            if old_item != new_item:
                if old_item['joinable'] is False and new_item['joinable'] is True:
                    print(f"Item {item} is now joinable!")
                changed_items.append(item)
    
    return added_items, changed_items

def log_folder_changes(folder_id, added_items, changed_items):
    '''
    Log the changes of a folder
    :param folder_id: the ObjectId of the folder
    :param added_items: the added items
    :param changed_items: the changed items
    :return: None
    '''
    changes_collection = DB['changes']  # Use the appropriate name for the changes collection
    changes_document = {
        "folder_id": folder_id,
        "changes": {
            "added_items": added_items,
            "changed_items": changed_items
        },
        "timestamp": datetime.now()
    }
    changes_collection.insert_one(changes_document)

def insert_folder(folder):
    '''
    Insert a folder into the database
    :param folder: the folder to insert
    :return: the ObjectId of the inserted folder
    '''
    # Insert the current folder into MongoDB 
    result = FOLDERS_COLLECTION.insert_one(folder)
    inserted_id = result
    return inserted_id

# endregion
# region: Crawler functions

def initial_crawl(driver, url, folder_path="root//", is_demo_mode=False):
    '''
    Crawls the StudOn website and returns a dictionary containing all items
    - scrap the current page
    - insert the current folder into MongoDB
    - recursively crawl the sub-folders
    - add the ObjectId of each sub-folder to the current folder as a reference

    :param driver: the Selenium driver
    :param url: the URL to crawl
    :param folder_path: the path of the current scrapped folder
    :param is_demo_mode: whether to enable demo mode (no db operations)
    :return: a dictionary containing all items
    '''
    print(f"Processing {folder_path}")
    # Check if url starts with https://www.studon.fau.de/
    if url is None or not url.startswith(config.BASE_URL):
        return None

    # Get the hash of the current page
    hash = get_hash_of_page(driver=driver)

    # Get items from the current page
    all_items = page_scrap(driver, url)

    # Get all items that are sub-folders
    sub_folders = {k: v for k, v in all_items.items() if v['is_folder']}

    # Object to store folder data
    folder = { 
        "path": folder_path, "url": url, "hash": hash, "items": all_items, "child_folders": []
    }
    if not is_demo_mode:
        inserted_id = insert_folder(folder)
        if inserted_id == None:
            print("Error inserting folder")


    # Process its sub-folders via recursion
    for _, item_info in sub_folders.items():
        # folder_path = root: Ignore for now faculty folders other than "technical faculty"
        if folder_path == "root//" and item_info['item_name'] != "5. Technische Fakultät":
            continue

        # Check if this is a relevant folder (current or next semester)
        if is_relevant_folder(item_info['item_name']):
            # We need to go deeper into this folder
            # folder path of subfolder
            sub_folders_path = folder_path + item_info['item_name'] + "//"
            # Recursively crawl the sub-folder  
            sub_folder_id = initial_crawl(driver=driver, url=item_info['item_link'], folder_path=sub_folders_path, is_demo_mode=is_demo_mode)
            # Add the ObjectId of the sub-folder to the current folder
            folder['child_folders'].append(sub_folder_id)
    # If this is a demo run, don't do db operations
    if not is_demo_mode and len(folder['child_folders']) > 0:
        # Update the child_folders field
        result = FOLDERS_COLLECTION.update_one(
            {"_id": inserted_id}, 
            {"$set": {"child_folders": folder["child_folders"]}}
        )
        # check if the update was successful
        if result.modified_count != 1:
            print("Error updating child_folders field")

    # Return the ObjectId of the current folder, such that it can be used as a reference in the parent folder
    return inserted_id




def incremental_crawl(driver, url, folder_path="root//", is_demo_mode=False):
    '''
    Crawl StudOn website similar to initial_crawl but compare folder items with the ones in the database
    - scrap the current page
    - compare the hash of the current page with the one in the database
    - if the hash is the same, folder stayed the same:
        - we can skip scraping this page & reuse items from the database
    - if the hash is different: 
        - we need to scrap the page again
        - compare the items with the ones in the database
        - if there are new items:
            we need to insert them into the database
        - if there are changed items:
            - we need to log them
            - we need to update the folder in the database
    - insert the current folder into MongoDB
    - recursively crawl the sub-folders 
    - add the ObjectId of each sub-folder to the current folder as a reference

    :param driver: the Selenium driver
    :param url: the URL to crawl
    :param folder_path: the path of the current scrapped folder
    :param is_demo_mode: whether to enable demo mode (no db operations)
    :return: a dictionary containing all items
    '''
    print(f"Processing {folder_path}")
    # Check if url starts with https://www.studon.fau.de/
    if url is None or not url.startswith(config.BASE_URL):
        return None

    # Get the hash of the current folder
    hash = get_hash_of_page(driver=driver)

    # Get the old folder from the database
    old_folder = FOLDERS_COLLECTION.find_one({"path": folder_path})

    # If the folder is the database and it doesnt contains items (courses), we can use compare the hash of the page with the one in the database
    # If the hash is the same, folder stayed the same, we can skip scraping this page & reuse items from the database
    if old_folder is not None and len(old_folder['items']) == 0 and old_folder.get('hash') == hash:
        new_items = old_folder['items']
    else:
        new_items = page_scrap(driver, url)

        # Check differences between old and new folder, if there is an old folder
        if old_folder is not None:
            old_items = old_folder['items']
            added_items, changed_items = check_folder_changes(old_items, new_items)
            if added_items or changed_items:
                print(f"Added items: {added_items}")
                print(f"Changed items: {changed_items}")
                log_folder_changes(old_folder['_id'], added_items, changed_items)
 
            # Define the new values to be updated
            new_values = { "$set": { "url": url, "items": new_items } }

            # Update the document in the collection
            # If this is a demo run, don't do db operations 
            if not is_demo_mode:
                FOLDERS_COLLECTION.update_one({"_id": old_folder['_id']}, new_values)
                # Check if the update was successful
                if result.modified_count != 1: 
                    print("Error updating folder")
        else:
            # If found entirely new folder -> insert  into MongoDB 
            # Check if this is a demo run
            if not is_demo_mode:
                folder = {
                    "url": url, "path": folder_path, "hash": hash, "items": new_items, "child_folders": []
                }
                inserted_id = insert_folder(folder)
                if inserted_id == None:
                    print("Error inserting folder")
            
    # Get all items that are sub-folders
    sub_folders = {k: v for k, v in new_items.items() if v['is_folder']}    


    # Process its sub-folders via recursion
    for _, item_info in sub_folders.items():
        # folder_path = root: Ignore for now faculty folders other than "technical faculty"
        if folder_path == "root//" and item_info['item_name'] != "5. Technische Fakultät":
            continue

        # Check if this is a relevant folder (current or next semester)
        if is_relevant_folder(item_info['item_name']):
            # We need to go deeper into this folder
            # folder path of subfolder
            sub_folders_path = folder_path + item_info['item_name'] + "//"
            # Recursively crawl the sub-folder  
            sub_folder_id = initial_crawl(driver=driver, url=item_info['item_link'], folder_path=sub_folders_path, is_demo_mode=is_demo_mode)
            # Add the ObjectId of the sub-folder to the current folder
            folder['child_folders'].append(sub_folder_id)
    # If this is a demo run, don't do db operations
    if not is_demo_mode and len(folder['child_folders']) > 0:
        # Update the child_folders field
        result = FOLDERS_COLLECTION.update_one(
            {"_id": inserted_id}, 
            {"$set": {"child_folders": folder["child_folders"]}}
        )
        # check if the update was successful
        if result.modified_count != 1:
            print("Error updating child_folders field")

    # Return the ObjectId of the current folder, such that it can be used as a reference in the parent folder
    return inserted_id

# endregion

def main(crawl_type : str, is_debug_mode : bool, is_headless : bool, is_demo_mode : bool):
    '''
    Main function
    :param crawl_type: the type of crawl to perform (initial or incremental)
    :param is_debug_mode: whether to enable debug mode
    :param is_headless: whether to enable headless mode (no browser window))
    :param is_demo_mode: whether to enable demo mode (no db operations)
    :return: None
    '''
    #Init default arguments

    options = Options()

    # Set headless mode
    if is_headless:
        # headless mode operations
        options.add_argument("--headless")

    # Init Selenium
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # Login to StudOn
    print("StudOn Login ...")
    login(driver=driver)
    print("Successfully logged in to StudOn")

    if crawl_type == 'initial':
        # initial_crawl function
        print("Initial Crawling...")
        _ = initial_crawl(driver=driver, url=config.START_PAGE_URL, is_demo_mode=is_demo_mode)
    elif crawl_type == 'incremental':
        # incremental_crawl function
        print("Incremental Crawling...")
        _ = incremental_crawl(driver=driver, url=config.START_PAGE_URL, is_demo_mode=is_demo_mode)



if __name__ == '__main__':
    """
    Main function
    initial run: python crawler.py initial --debug --headless --demo
    incremental run: python crawler.py initial --debug --headless --demo

    """
    parser = argparse.ArgumentParser(description='Web Crawling Script')
    
    parser.add_argument('crawl_type', choices=['initial', 'incremental'], help='Type of crawl to perform')
    parser.add_argument('--debug', dest='is_debug_mode', action='store_true', help='Enable debug mode')
    parser.add_argument('--headless', dest='is_headless', action='store_true', help='Enable headless mode')
    parser.add_argument('--demo', dest='is_demo_mode', action='store_true', help='Enable demo mode')

    args = parser.parse_args()

    main(args.crawl_type, args.is_debug_mode, args.is_headless, args.is_demo_mode)
