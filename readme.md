## Overview

This is a project designed to simplify and enhance the course registration process for students at Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU). The platform addresses common issues with **StudOn**, the university’s course management system, by providing a web scraper and a user-friendly interface that helps students:

- Quickly search for courses and find direct links to StudOn registration.
- Get notifications when new courses are available or when registration opens.
- Discover courses through recommendations based on their search queries.

This project originated during the **"Programming with LLMs"** course at the Pattern Recognition Lab, FAU, with a focus on leveraging AI for planning, implementation, and database design.


## Table of Contents
  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Demo](#demo)
  - [Setup and Installation](#setup-and-installation)
  - [Example Commands](#example-commands)
  - [How Scraping Works](#how-scraping-works)
  - [Project Structure](#project-structure)
  - [Use Cases](#use-cases)
  - [Future Plans](#future-plans)
---



## Features

### Implemented Features
1. **Web Scraping**:
   - Scrapes StudOn for course listings, folders, and documents.
   - Tracks whether courses are open for registration.
   - Predefined folder scraping for faster operation.

2. **Web Application**:
   - Search and visualize courses and folders from StudOn.
   - Direct links to join courses when registration is open.
   - Expand/collapse all folders for easier navigation.

3. **Database Integration**:
   - Stores scraped data in a MongoDB database for efficient querying.

### Planned Features
- **Notifications**:
  - Email alerts for new courses, joinable courses, or updated documents.
  - Customizable notification preferences.
- **Course Recommendations**:
  - Suggest courses based on user search queries.
- **Performance Improvements**:
  - Optimize scraping speed and enable parallel processing.
- **Login and Authentication**:
  - Google OAuth for secure user access.
- **Deployment**:
  - Fully functional and accessible via a public server.

---

## Tech Stack

- **Programming Language**: Python
- **Large Language Models**: ChatGPT, GitHub Copilot
- **Web Scraping**: Selenium
- **Web Framework**: Flask
- **Database**: MongoDB
- **Authentication**: Google OAuth
- **Libraries**: 
  - `pandas`, `selenium`, `Werkzeug==2.2.2`, `Flask==2.3.1`, `pymongo`, `webdriver-manager`, `flask-oauthlib`

---

## Demo

### 1. Scraping Bot in Action

![Scraping Bot in Action](/media/scrapping.gif)

The above GIF demonstrates the scraping bot live in action:
- Navigating through the StudOn platform.
- Identifying folders and courses.
- Extracting relevant data and saving it to MongoDB.

### 2. Website Usage and Notifications

![Website Usage and Notifications](/media/webapp.gif)

This GIF showcases the functionality of the web application:
- Searching and navigating through folders and courses.
- Viewing course details and joinable statuses.
- Subscribing to a folder to receive notifications on changes.



## Setup and Installation

### Prerequisites
1. **MongoDB**:
   - Download and install MongoDB from [here](https://www.mongodb.com/docs/manual/installation/).
   - All required databases and collections will be automatically created during setup, but ensure the correct URI and port are configured in the `bot/config.py` file.
   - Example:
     ```python
     MONGODB_URI = "127.0.0.1"
     MONGODB_PORT = 27017
     ```

2. **Geckodriver and Chromedriver**:
   - Ensure `geckodriver` and `chromedriver` are installed and compatible with your browser.

3. **Python Packages**:
   - Install dependencies:
     ```bash
     pip install pandas selenium Werkzeug==2.2.2 Flask==2.3.1 pymongo webdriver-manager flask-oauthlib
     ```

### Configuration

#### `bot/config.py`
- **Scraping Configuration**:
  - `TO_BE_PROCESSED_FOLDERS`: Specifies which folders and their subfolders to scrape.
    - Example: `"root//5. Technische Fakultät//5.3 INF//"`
    - To scrape everything, set to `"root//"`.
  - `START_PAGE_URL`: Defines the starting page for scraping.
    - Example for specific folder scraping: `"https://www.studon.fau.de/studon/goto.php?target=cat_1110"`
    - For scraping everything, provide the main page link containing all superfolders.
- **MongoDB Configuration**:
  - Ensure `MONGODB_URI`, `MONGODB_PORT`, and other database settings are properly configured.

#### `app/config.py`
- **Google OAuth Configuration**:
  - Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` for enabling Google login.
  - Example:
    ```python
    GOOGLE_CLIENT_ID = "<your-client-id>"
    GOOGLE_CLIENT_SECRET = "<your-client-secret>"
    ```
  - To disable Google login, set `USE_GOOGLE_AUTH = False`.

  

### Running Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/FAU-StudOn-Bot.git
   cd FAU-StudOn-Bot
2. Start MongoDB Server through UI f.e.
3. Run the Web Scrapper
    - for initial run: python main.py initial
    - for incremental update: python main.py incremental
4. Run the Flask Web Server
    - python web_app.py

## Example Commands
### MongoDB Commands
Switch Database:
use university_courses

Find Specific Folder:
db.folders.find({ "path": "root//5. Technische Fakultät//5.1 CBI//" })


Delete All Data:
db.folders.deleteMany({})


## How Scraping Works

Web scraping in FAU-StudOn-Bot involves extracting data from the FAU StudOn platform and storing it in a structured format for further processing. Below is an explanation of the workflow with visual aids.

### Step 1: Extracting Course Information

![StudOn Course HTML Example](/media/studon_html_code.png)

- **Left**: Shows how courses and folders are displayed on the StudOn platform.
- **Right**: The corresponding HTML source code, where you can identify:
  - Whether an item is a course or folder.
  - If it’s a course, whether it is joinable.
  - Links to the course and its name.

### Step 2: Saving Data to MongoDB

![MongoDB JSON Example](/media/web_json_structure.png)

- Data from each page/folder is saved in MongoDB as JSON.
- For each page, the bot saves:
  - A unique ID.
  - Path to the folder/page.
  - URL of the folder/page.
  - A hash of the page content for tracking changes.
  - A list of items (courses or folders) with details:
    - Name
    - Link
    - Whether it is a folder or a course.
    - If it is a joinable course.

### Step 3: Structuring Data for Web Display

- The backend script aligns all JSON data from the database into a nested dictionary structure for the web application.
- Example JSON structure:
  ```json
  {
    "5. Technische Fakultät": {
      "5.3 INF": {
        "id": "67716f605e3bfb66771e5011",
        "is_subscribed": false,
        "Courses": {
          "Digitale Geistes- und Sozialwissenschaften / Digital Humanities": {
            "item_name": "Digitale Geistes- und Sozialwissenschaften / Digital Humanities",
            "item_link": "https://www.studon.fau.de/studon/ilias.php?ref_id=1651226&cmd=render&cmdClass=ilrepositorygui&cmdNode=146&baseClass=ilRepositoryGUI",
            "joinable": false,
            "is_folder": false
          }
        }
      }
    }
  }

## Project Structure
```md
folders/
  app/
    templates/
      index.html         # Frontend template
    config.py            # Configuration for web app
    folder_structure.json # Generated file displaying scraped data structure
    web_app.py           # Backend logic for web app

  bot/
    Dokumente/           # Temporary storage for documents
    dump/                # Temporary storage
    chromedriver/        # Required for scraping
    config.py            # Configuration for bot
    crawler.py           # Core scraping logic
    geckodriver/         # Required for scraping
    login.py             # Handles login interactions
    main.py              # Entry point for initial and incremental updates
    scraper.py           # Implements scraping workflows

readme.md                # This file
requirements.txt         # Dependencies
```

## Use Cases
- Easier Course Search:
- Quickly locate and join courses on StudOn.
- Notifications: Stay informed about new or joinable courses.
- Course Recommendations: Discover new courses based on search text.


## Future Plans:
- Integration with other FAU faculties beyond the Technical Faculty.
- Testing against edge cases.
- Notification service implementation.
- Code refactoring and testing.
- Faster execution through parallel processing.
- Full deployment for public use.




