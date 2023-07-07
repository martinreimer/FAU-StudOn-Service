#import
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time
from config import FAU_USERNAME, FAU_PASSWORD

def login(driver):
    # Load Start Website
    url = "https://www.studon.fau.de/studon/login.php?client_id=StudOn&cmd=force_login&lang=de"  
    driver.get(url)

    # Wait for the page to load completely (modify the timeout as needed)
    driver.implicitly_wait(4)

    element = driver.find_element(By.LINK_TEXT, "Anmelden")
    element.click()
    time.sleep(1)


    # Find the username input field and enter the username
    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys(FAU_USERNAME)

    # Find the password input field and enter the password
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(FAU_PASSWORD)

    # Submit the form
    submit_button = driver.find_element(By.ID, "submit_button")
    submit_button.click()
    time.sleep(0.5)