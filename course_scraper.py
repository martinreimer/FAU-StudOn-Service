#import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from config import STUDON_COOKIE, WEBSITE

#Init Selenium
options = Options()
driver = webdriver.Chrome(options=options)

# Load Start Website
url = WEBSITE  
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

# Find all rows with class="ilCLI ilObjListRow row" inside the container div
rows = container.find_elements(By.CLASS_NAME, "ilCLI.ilObjListRow.row")

# Initialize a dictionary to store course information
courses = {}
# Loop through the rows and extract the course information
for row in rows:
    # Find the container div with class="il_ContainerItemTitle form-inline"
    container_element = row.find_element(By.CLASS_NAME, "il_ContainerItemTitle.form-inline")
    
    # Find the course name within the <h3> element
    h3_element = container_element.find_element(By.TAG_NAME, "h3")
    course_name = h3_element.text
    
    # Find the course description
    description_element = row.find_element(By.CLASS_NAME, "il_Description")
    description = description_element.text
    
    # Find the course details and lecturers
    properties_element = row.find_element(By.CLASS_NAME, "il_ItemProperties")
    details_element = properties_element.find_element(By.TAG_NAME, "span")
    details = details_element.text
    
    lecturers_element = properties_element.find_elements(By.TAG_NAME, "span")[1]
    lecturers = lecturers_element.text
    

    # Find the button and perform a click
    btn_group = row.find_element(By.CLASS_NAME, "btn-group")
    button = btn_group.find_element(By.TAG_NAME, "button")
    button.click()

    # Sleep for 5 seconds to allow the dropdown menu to load
    time.sleep(1)

    # Check if there is an <a> element with the text "Beitreten"
    dropdown_menu = btn_group.find_element(By.CLASS_NAME, "dropdown-menu")
    a_elements = dropdown_menu.find_elements(By.TAG_NAME, "a")
    joinable = False

    for a_element in a_elements:
        if "Beitreten" in a_element.text:
            joinable = True
            break


    # Store the course information in the dictionary
    course_info = {
        "course_name": course_name,
        "description": description,
        "details": details,
        "lecturers": lecturers,
        "joinable": joinable
    }
    courses[course_name] = course_info
    


# Print the extracted course information
for course_name, course_info in courses.items():
    print("Course Name:", course_name)
    print("Description:", course_info["description"])
    print("Details:", course_info["details"])
    print("Lecturers:", course_info["lecturers"])
    print("Joinable:", str(course_info["joinable"]))
    print("----")

# Quit the driver
driver.quit()