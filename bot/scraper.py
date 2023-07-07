#import
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time

def extract_row_info(driver, row):
    '''
    Extracts the information from a row element
    :param row: the row element
    :return: a dictionary containing the extracted information
    '''
    # Find the container div with class="il_ContainerItemTitle form-inline"
    container_element = row.find_element(By.CLASS_NAME, "il_ContainerItemTitle.form-inline")
    # Find the item name within the <h3> element
    h3_element = container_element.find_element(By.TAG_NAME, "h3")
    item_name = h3_element.text

    # Find the item link
    try:
        item_link = h3_element.find_element(By.TAG_NAME, "a").get_attribute("href")
    except:
        item_link = None

    # Check if item is normal && Check if item is a file to download, if so, skip
    if (item_name == None or item_name == "") or (item_link is not None and item_link.endswith("download.html")):
        return {
        "item_name": item_name,
        "item_link": None,
        "joinable": False,
        "is_folder": False
    }

    # Check if item is a folder by checking the icon
    joinable, is_folder, is_course = False, False, False
    try:
        img_alt = row.find_element(By.CLASS_NAME, "ilContainerListItemIcon").find_element(By.TAG_NAME, "img").get_attribute("alt")
        is_folder = "Kategorie" == img_alt
        if not is_folder:
            is_course = "Kurs" == img_alt
    except:
        print("Error in icon")

    # check if item is a course to skip rest
    if is_course:
        # Find the button and perform a click
        btn_group = row.find_element(By.CLASS_NAME, "btn-group")
        button = btn_group.find_element(By.TAG_NAME, "button")
        button.click()

        # Wait for the dropdown menu to load
        try:
            dropdown_menu = WebDriverWait(btn_group, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "dropdown-menu")))
            #dropdown_menu = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "dropdown-menu")))
        except TimeoutException:
            # Handle timeout exception if the element doesn't appear within the specified time
            print("Dropdown menu did not appear within the timeout period")

        # Check if there is an <a> element with the text "Beitreten"
        a_elements = dropdown_menu.find_elements(By.TAG_NAME, "a")

        for a_element in a_elements:
            if "Beitreten" == a_element.text or "Kursmitgliedschaft beenden" == a_element.text:
                joinable = True
            elif "Zu Favoriten hinzufügen" == a_element.text:
                is_folder = True

        # Perform another click on the button to close the collapsible
        button.click()

    # Store the item information in the dictionary
    item_info = {
        "item_name": item_name,
        "item_link": item_link,
        "joinable": joinable,
        "is_folder": is_folder
    }
    return item_info


def extract_tile_info(driver, tile_row):
    '''
    Extracts the information from a tile element
    :param tile_row: the tile element
    :return: a dictionary containing the extracted information
    '''
    card_element = tile_row.find_element(By.CLASS_NAME, "il-card.thumbnail")
    
    # Extract item name
    caption_element = card_element.find_element(By.CLASS_NAME, "caption.card-title")
    a_element = caption_element.find_element(By.TAG_NAME, "a")
    item_name = a_element.text
    item_link = a_element.get_attribute("href")
    
    # Check if item is normal && Check if item is a file to download, if so, skip
    if (item_name == None or item_name == "") or (item_link is not None and item_link.endswith("download.html")):
        return {
        "item_name": item_name,
        "item_link": None,
        "joinable": False,
        "is_folder": False
    }

    
    # Check if item is a folder by checking the icon
    joinable, is_folder, is_course = False, False, False
    try:
        icon_element = card_element.find_element(By.CLASS_NAME, "il-card-repository-head")
        img_alt = icon_element.find_element(By.TAG_NAME, "img").get_attribute("alt")
        is_folder = "Kategorie" == img_alt
        if not is_folder:
            is_course = "Kurs" == img_alt
    except:
        print("Error in icon")

    # check if item is not folder to skip rest
    if is_course:

        # Find the dropdown button
        dropdown_button = card_element.find_element(By.CLASS_NAME, "btn.btn-default.dropdown-toggle")
        dropdown_button.click()

        # Sleep for a second to allow the dropdown menu to load
        time.sleep(0.3)

        # Check if there are any actions related to joining
        # Wait for the dropdown menu to load
        try:
            dropdown_menu = WebDriverWait(card_element, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "dropdown-menu")))
            #dropdown_menu = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "dropdown-menu")))
        except TimeoutException:
            # Handle timeout exception if the element doesn't appear within the specified time
            print("Dropdown menu did not appear within the timeout period")


        btn_elements = dropdown_menu.find_elements(By.TAG_NAME, "button")
        for btn_element in btn_elements:
            if "Beitreten" == btn_element.text or "Kursmitgliedschaft beenden" == btn_element.text:
                joinable = True
            elif "Zu Favoriten hinzufügen" == btn_element.text:
                is_folder = True
        
        # Perform another click on the button to close the dropdown menu
        dropdown_button.click()

    # Store the item information in the dictionary
    item_info = {
        "item_name": item_name,
        "item_link": item_link,
        "joinable": joinable,
        "is_folder": is_folder
    }

    return item_info


def page_scrap(driver, url, print_info=False):
    '''
    Scrapes the page for items information
    :param driver: the selenium driver
    :param url: the url of the page to scrape
    :param print_info: whether to print the extracted information
    :return: a dictionary containing the extracted information
    '''
    # Load Start Website
    driver.get(url)

    # Wait for the page to load completely (modify the timeout as needed)
    #driver.implicitly_wait(1)

    # Initialize a dictionary to store items information
    items = {}
    # Find all container divs with class="ilContainerItemsContainer"
    containers = driver.find_elements(By.CLASS_NAME, "ilContainerItemsContainer")

    # Loop through the containers
    for container in containers:
        if print_info:
            print("-"*60 + "\n Container")
        
        # Find all rows with class="ilCLI ilObjListRow row" inside the container div
        rows = container.find_elements(By.CLASS_NAME, "ilCLI.ilObjListRow.row")
        
        # Check if Method 1: Rows is used
        if rows:  
            for row in rows:
                try:
                    item_info = extract_row_info(driver, row)
                    if item_info is not None:
                        items[item_info['item_name']] = item_info
                except:
                    if print_info:
                        print("Error in row")
                    continue
            
        # Check if Method 2: Tiles is used
        tiles = container.find_elements(By.CLASS_NAME, "ilContainerTileRows")
        if tiles:  
            tile_rows = container.find_elements(By.CLASS_NAME, "col-xs-12.col-sm-6.col-md-4.col-lg-3")
            for tile_row in tile_rows:
                try:
                    item_info = extract_tile_info(driver, tile_row)
                    if item_info is not None:
                        items[item_info['item_name']] = item_info
                except:
                    if print_info:
                        print("Error in tile")
                    continue    
    if print_info:
        # Print the extracted item information
        for item_name, item_info in items.items():
            print("item Name:", item_name)
            print("Joinable:", str(item_info["joinable"]))
            print("Folder:", str(item_info["is_folder"]))
            print("----")
    return items    