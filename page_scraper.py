#import
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time


def extract_row_info(row):
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

    # Check if item is normal
    if item_name == None or item_name == "":
        return None
    
    # Find the item link
    try:
        a_element = h3_element.find_element(By.TAG_NAME, "a")
        item_link = a_element.get_attribute("href")
    except:
        item_link = None

    # Find the item description
    try:
        description_element = row.find_element(By.CLASS_NAME, "il_Description")
        description = description_element.text
    except:
        description = None

    # Find the item details
    try:
        properties_element = row.find_element(By.CLASS_NAME, "il_ItemProperties")
        details_element = properties_element.find_element(By.TAG_NAME, "span")
        details = details_element.text
        
    except:
        details = None

    # Check if item is a file to download, if so, skip
    if item_link is not None and item_link.endswith("download.html"):
        return None

        # Find the container div with class="il_ContainerItemTitle form-inline"
    container_element = row.find_element(By.CLASS_NAME, "il_ContainerItemTitle.form-inline")
    
    # Find the item name within the <h3> element
    h3_element = container_element.find_element(By.TAG_NAME, "h3")
    item_name = h3_element.text

    # Check if item is a folder by checking the icon
    joinable = False
    is_folder = False
    try:
        icon_element = row.find_element(By.CLASS_NAME, "ilContainerListItemIcon")
        icon_img_element = icon_element.find_element(By.TAG_NAME, "img")
        is_folder = "icon_cat.svg" in icon_img_element.get_attribute("src")
    except:
        print("Error in icon")

    # check if item is not folder to skip rest
    if False:#not is_folder:
        # Check if item is link, if so, skip
        if "icon_webr.svg" in icon_img_element.get_attribute("src"):
            return None

        # Find the button and perform a click
        btn_group = row.find_element(By.CLASS_NAME, "btn-group")
        button = btn_group.find_element(By.TAG_NAME, "button")

        button.click()

        # Sleep for 5 seconds to allow the dropdown menu to load
        time.sleep(0.3)

        # Check if there is an <a> element with the text "Beitreten"
        dropdown_menu = btn_group.find_element(By.CLASS_NAME, "dropdown-menu")
        a_elements = dropdown_menu.find_elements(By.TAG_NAME, "a")


        for a_element in a_elements:
            if "Beitreten" in a_element.text or "Kursmitgliedschaft beenden" in a_element.text:
                joinable = True
            elif "Zu Favoriten hinzufügen" in a_element.text:
                is_folder = True

        # Perform another click on the button to close the collapsible
        button.click()

    # Store the item information in the dictionary
    item_info = {
        "item_name": item_name,
        "description": description,
        "item_link": item_link,
        "joinable": joinable,
        "is_folder": is_folder
    }
    return item_info


def extract_tile_info(tile_row):
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
    
    # Check if item is normal
    if item_name == None or item_name == "":
        return None
    
    # Extract item description
    caption_elements = card_element.find_elements(By.CLASS_NAME, "caption")
    description = caption_elements[1].text if len(caption_elements) > 1 else None  # Assuming the description is always the second caption
    
    # Check if item is a file to download, if so, skip
    if item_link is not None and item_link.endswith("download.html"):
        return None
    
    # Check if item is a folder by checking the icon
    joinable = False
    is_folder = False

    icon_element = card_element.find_element(By.CLASS_NAME, "il-card-repository-head")
    icon_img_element = icon_element.find_element(By.TAG_NAME, "img")
    is_folder = "icon_cat.svg" in icon_img_element.get_attribute("src")

    # check if item is not folder to skip rest
    if False:#not is_folder:
        # Check if item is link, if so, skip
        if "icon_webr.svg" in icon_img_element.get_attribute("src"):
            return None
        # Find the dropdown button
        dropdown_button = card_element.find_element(By.CLASS_NAME, "btn.btn-default.dropdown-toggle")
        dropdown_button.click()

        # Sleep for a second to allow the dropdown menu to load
        time.sleep(0.3)

        # Check if there are any actions related to joining
        dropdown_menu = card_element.find_element(By.CLASS_NAME, "dropdown-menu")
        btn_elements = dropdown_menu.find_elements(By.TAG_NAME, "button")

        for btn_element in btn_elements:
            if "Beitreten" in btn_element.text or "Kursmitgliedschaft beenden" in btn_element.text:
                joinable = True
            elif "Zu Favoriten hinzufügen" in btn_element.text:
                is_folder = True
        
        # Perform another click on the button to close the dropdown menu
        dropdown_button.click()

    # Store the item information in the dictionary
    item_info = {
        "item_name": item_name,
        "description": description,
        "item_link": item_link,
        "joinable": joinable,
        "is_folder": is_folder
    }

    return item_info


def scrap_page(driver, url, print_info=False):
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
    driver.implicitly_wait(2)

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
                    item_info = extract_row_info(row)
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
                    item_info = extract_tile_info(tile_row)
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
            print("Description:", item_info["description"])
            print("Joinable:", str(item_info["joinable"]))
            print("Folder:", str(item_info["is_folder"]))
            print("----")
    return items    