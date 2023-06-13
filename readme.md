
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
