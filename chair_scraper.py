#import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from config import STUDON_COOKIE, START_PAGE

#Init Selenium
options = Options()
driver = webdriver.Chrome(options=options)

# Load Start Website
url = "https://www.studon.fau.de"  
driver.get(url)
#delete cookies
driver.delete_all_cookies()
time.sleep(2)
driver.add_cookie(STUDON_COOKIE)
driver.refresh()
time.sleep(2)


# Wait for the page to load completely (modify the timeout as needed)
driver.implicitly_wait(4)

# Find the container div with class="ilContainerItemsContainer"
container = driver.find_element(By.CLASS_NAME, "ilContainerItemsContainer")


# Find the link with the text "Technische Fakultät"
link_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Technische Fakultät")))
link_element.click()

time.sleep(2)





# Find the container div with class="ilContainerItemsContainer"
container = driver.find_element(By.CLASS_NAME, "ilContainerItemsContainer")

# Find all rows with class="ilCLI ilObjListRow row" inside the container div
rows = container.find_elements(By.CLASS_NAME, "ilCLI.ilObjListRow.row")

# Initialize a dictionary to store department information
departments = {}

# Loop through the rows and extract the department information
for row in rows:
    # Find the department name link
    department_link = row.find_element(By.TAG_NAME, "a")
    department_name = department_link.text
    department_url = department_link.get_attribute("href")
    
    # Find the department description
    department_description = row.find_element(By.CLASS_NAME, "ilListItemSection.il_Description").text
    
    # Store the department information in the dictionary
    departments[department_name] = {
        "name": department_name,
        "link": department_url,
        "description": department_description
    }

# Print the department information
for department in departments.values():
    print("Department Name:", department["name"])
    print("Department Link:", department["link"])
    print("Department Description:", department["description"])
    print()



# Check if any department has "Informatik" in its name
current_department = None

for department in departments.values():
    if "Informatik" in department["description"]:
        current_department = department
        break

if current_department is None:
    print("No department found with 'Informatik' in its name. Stopping the code.")
    exit

department_url = current_department["link"]
print("URL of the 'Informatik' department:", department_url)








#region Chair
# Open the URL of the 'Informatik' department
driver.get(department_url)
# Wait for the page to load completely (modify the timeout as needed)
driver.implicitly_wait(4)

# Find the container div with class="ilContainerItemsContainer"
container = driver.find_element(By.CLASS_NAME, "ilContainerItemsContainer")

# Find all rows with class="ilCLI ilObjListRow row" inside the container div
rows = container.find_elements(By.CLASS_NAME, "ilCLI.ilObjListRow.row")

# Initialize a dictionary to store chair information
chairs = {}

# Loop through the rows and extract the chair information
for row in rows:
    # Find the chair title element
    chair_title = row.find_element(By.CLASS_NAME, "il_ContainerItemTitle")
    chair_link = chair_title.find_element(By.TAG_NAME, "a").get_attribute("href")
    chair_name = chair_title.text

    # Find the chair description element
    chair_description = row.find_element(By.CLASS_NAME, "ilListItemSection.il_Description").text

    # Store the chair information in the dictionary
    chairs[chair_name] = {
        "name": chair_name,
        "description": chair_description,
        "link": chair_link
    }

# Print the chair information
for chair in chairs.values():
    print("Chair Name:", chair["name"])
    print("Chair Description:", chair["description"])
    print("Chair Link:", chair["link"])
    print("-" * 50)


# Check if any department has "Informatik" in its name
current_chair = None

# Loop through the chairs and check the chair description for "Mustererkennung"
for chair in chairs.values():
    if "Mustererkennung" in chair["description"]:
        current_chair = chair
        


if current_chair is None:
    print("No department found with 'Informatik' in its name. Stopping the code.")
    exit
chair_url = current_chair["link"]

#endregion

#region Semesters
'''
# Open the URL of the 'Informatik' department
driver.get(chair_url)
# Wait for the page to load completely (modify the timeout as needed)
driver.implicitly_wait(4)


rows = container.find_elements(By.CLASS_NAME, "ilCLI.ilObjListRow.row")

# Define a dictionary to store the folders and courses
items_dict = {}

# Loop through the list items
for item in rows:
    # Check if the item is a folder based on the icon's title
    is_folder = False
    icon = item.find_element_by_class_name("ilListItemIcon")
    if icon.get_attribute("title") == "Kategorie":
        is_folder = True
    
    # Extract the name, link, description, and is_folder information
    item_content = item.find_element_by_class_name("il_ContainerListItem")
    item_name = item_content.find_element_by_tag_name("a").text
    item_link = item_content.find_element_by_tag_name("a").get_attribute("href")
    item_description = item_content.find_element_by_class_name("ilListItemSection.il_Description").text
    
    # Create a dictionary for the item and store it in the items_dict
    item_dict = {
        "name": item_name,
        "link": item_link,
        "description": item_description,
        "is_folder": is_folder
    }
    
    # Add the item to the items_dict with a unique key
    items_dict[item_link] = item_dict

# Print the extracted information for each item
for key, item in items_dict.items():
    print("Name:", item["name"])
    print("Link:", item["link"])
    print("Description:", item["description"])
    print("Is Folder:", item["is_folder"])
    print("--------------------")

time.sleep(10)
'''
#endregion

# Quit the driver
driver.quit()