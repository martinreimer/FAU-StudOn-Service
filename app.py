from flask import Flask, render_template
from pymongo import MongoClient
import config

app = Flask(__name__)

# Connect to the MongoDB
client = MongoClient(config.MONGODB_URI, config.MONGODB_PORT)

# Select the database
db = client[config.MONGODB_DB]

# Select the collection within the database
folders_collection = db[config.MONGODB_COLLECTION]

@app.route('/')
def index():
    # Fetch folder system data from MongoDB
    folders = folders_collection.find({})
    print(list(folders)) # check if data is being fetched

    # Render index.html with folders data
    return render_template('index.html', folders=folders)

if __name__ == "__main__":
    app.run(debug=True)
