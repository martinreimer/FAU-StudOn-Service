# Configuration file for the application

# ==========================================
# Google OAuth Configuration
# ==========================================
# GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required for enabling Google OAuth.
# These values can be obtained by creating a project on the Google Developer Console
# and setting up OAuth credentials.
GOOGLE_CLIENT_ID = ""  # Replace with your Google OAuth Client ID
GOOGLE_CLIENT_SECRET = ""  # Replace with your Google OAuth Client Secret

# Set USE_GOOGLE_AUTH to True to enable Google OAuth functionality.
# If False, the application will skip the Google login process and use basic routes.
USE_GOOGLE_AUTH = False  # Set to True to enable Google OAuth

# ==========================================
# MongoDB Configuration
# ==========================================
# MONGODB_URI specifies the host address for the MongoDB instance.
# MONGODB_PORT specifies the port number MongoDB is listening on.
# MONGODB_DB specifies the database name used by the application.
# The remaining variables define the collection names for various data types.

MONGODB_URI = "127.0.0.1"  # MongoDB server address (default: localhost)
MONGODB_PORT = 27017  # Default port for MongoDB
MONGODB_DB = "university_courses"  # Name of the database

# Collection names for storing application data
MONGODB_COLLECTION_FOLDERS = "folders"  # Stores folder structure information
MONGODB_COLLECTION_USERS = "users"  # Stores user information
MONGODB_COLLECTION_SUBSCRIPTIONS = "subscriptions"  # Tracks user subscriptions to folders
MONGODB_COLLECTION_LOGS = "logs"  # Stores logs for user actions (e.g., subscribe/unsubscribe)
MONGODB_COLLECTION_FOLDER_CHANGES = "folder_changes"  # Tracks changes made to folders
