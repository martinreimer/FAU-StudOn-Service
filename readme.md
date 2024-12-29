
## Overview

This is a project designed to simplify and enhance the course registration process for students at Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU). The platform addresses common issues with **StudOn**, the university’s course management system, by providing a web scraper and a user-friendly interface that helps students:

- Quickly search for courses and find direct links to StudOn registration.
- Get notifications when new courses are available or when registration opens.
- Discover courses through recommendations based on their search queries.

This project originated during the **"Programming with LLMs"** course at the Pattern Recognition Lab, FAU, with a focus on leveraging AI for planning, implementation, and database design.

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

## Setup and Installation

### Prerequisites
1. **MongoDB**:
   - Download and install MongoDB from [here](https://www.mongodb.com/docs/manual/installation/).
    - Version used by me: `8.0.4 (current)` on Windows x64.
   - (also optional) Install MongoDB Shell ([mongosh](https://www.mongodb.com/docs/mongodb-shell/)).

2. **Geckodriver**:
   - Ensure `geckodriver` is installed and works with your browser.

3. **Python Packages**:
   - Install dependencies:
     ```bash
     pip install pandas selenium Werkzeug==2.2.2 Flask==2.3.1 pymongo webdriver-manager flask-oauthlib
     ```

### Running Locally
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/FAU-StudOn-Bot.git
   cd FAU-StudOn-Bot
2. Start MongoDB Server through UI f.e.
3. Run the Web Scrapper
    - define parameters in config.py
    - run main.py
4. Run the Flask Web Server
    - web_app.py

## Example Commands
### MongoDB Commands
Switch Database:
use university_courses

Find Specific Folder:
db.folders.find({ "path": "root//5. Technische Fakultät//5.1 CBI//" })


Delete All Data:
db.folders.deleteMany({})


## Use Cases
- Easier Course Search:
- Quickly locate and join courses on StudOn.
- Notifications: Stay informed about new or joinable courses.
- Course Recommendations: Discover new courses based on search text.


## Future Plans:
- Integration with other FAU faculties beyond the Technical Faculty.
- Limitations and Future Work
- Testing against edge cases.
- Notification service implementation.
- Code refactoring and testing.
- Faster execution through parallel processing.
- Full deployment for public use.


License
This project is licensed under the MIT License. See the LICENSE file for details.





