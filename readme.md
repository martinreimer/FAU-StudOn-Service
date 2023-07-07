
Data Structure:
{
    "_id": ObjectId("folder1"),
    "name": "Computer Science",
    "path": "root/Science/Computer Science",
    "courses": [
        {
            "name": "Data Structures and Algorithms",
            "description": "This course covers data structures...",
            "url": "http://example.com/course/data-structures-and-algorithms",
            "is_joinable": true
        },
        {
            "name": "Artificial Intelligence",
            "description": "This course covers AI concepts...",
            "url": "http://example.com/course/artificial-intelligence",
            "is_joinable": false
        }
    ],
    "child_folders": [
        ObjectId("folder2"),
        ObjectId("folder3")
    ]
}

# Set Up

1. sudo systemctl start mongod
2. mongosh

use university_courses
find: db.folders.find({ "path": "root//5. Technische Fakultät//5.1 CBI//" })
deleteall: db.folders.deleteMany({})


# Idee

## Course Notifier Service
- Nutzer melden sich an über Google
- zu erst einmal nur TechFak
- ein mal tägliches scraping und anschließender Mail-Versand
- Benachrichtigung
    - wenn neuer Kurs/PDF/Ordner hinzugefügt oder wenn Kurseintritt möglich
    - über Einstellungen konfigurierbar   


## Local-hosted Scraper
- paste in links to folder you want to scrap items and subfolders

## Use-Cases
- get notified for new courses and joinable courses
- search easily for courses
