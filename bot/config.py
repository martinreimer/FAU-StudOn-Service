# Configuration file for the bot

# ==========================================
# MongoDB Configuration
# ==========================================
# MongoDB settings for storing application data.
# Adjust these variables based on your MongoDB setup.

MONGODB_URI = "127.0.0.1"  # MongoDB server address (default: localhost)
MONGODB_PORT = 27017  # Default MongoDB port
MONGODB_DB = "university_courses"  # Name of the database

# Collection names used by the bot for organizing and tracking data
MONGODB_COLLECTION_FOLDERS = "folders"  # Stores folder structure information
MONGODB_COLLECTION_USERS = "users"  # Stores user details
MONGODB_COLLECTION_SUBSCRIPTIONS = "subscriptions"  # Tracks user subscriptions to folders
MONGODB_COLLECTION_LOGS = "logs"  # Logs user actions (e.g., subscription/unsubscription)
MONGODB_COLLECTION_FOLDER_CHANGES = "folder_changes"  # Tracks changes made to folders

# ==========================================
# FAU Login Configuration
# ==========================================
# FAU login credentials for accessing restricted areas of the FAU StudOn platform.
# Replace these placeholders with your FAU username and password.
# Ensure this file is securely stored, as it contains sensitive information.

FAU_USERNAME = ""  # Your FAU username
FAU_PASSWORD = ""  # Your FAU password

# ==========================================
# StudOn Scraping Configuration
# ==========================================
# URLs and folder settings for scraping content from the FAU StudOn platform.

# START_PAGE_URL specifies the starting page for scraping.
# - If you want to scrape everything, set this to the main page containing all superfolders.
# - If you want to scrape from a specific folder, provide the direct link to that folder.
START_PAGE_URL = "https://www.studon.fau.de/studon/goto.php?target=cat_1110" #inf folder link

# TO_BE_PROCESSED_FOLDERS defines which folder and its subfolders will be scraped.
# - Use "root//" to scrape everything starting from the root.
# - Otherwise, specify folder names with "root//" as the prefix.
TO_BE_PROCESSED_FOLDERS = "root//5. Technische Fakultät//5.3 INF//"  # Example folder structure

# BASE_URL specifies the base URL of the StudOn platform.
# This is used to construct complete URLs during scraping.
BASE_URL = "https://www.studon.fau.de/"
