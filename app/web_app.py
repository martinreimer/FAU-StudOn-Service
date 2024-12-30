from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from flask_oauthlib.client import OAuth
import datetime
import config
import json

# Initialize the Flask application
app = Flask(__name__)

# Set the secret key for secure sessions (use a strong secret key in production)
app.secret_key = 'random_secret'

# Conditional OAuth setup based on configuration
if config.USE_GOOGLE_AUTH:
    # Initialize OAuth object
    oauth = OAuth(app)
    
    # Configure Google OAuth application
    google = oauth.remote_app(
        'google',
        consumer_key=config.GOOGLE_CLIENT_ID,
        consumer_secret=config.GOOGLE_CLIENT_SECRET,
        request_token_params={
            'scope': 'email',  # Request email access from users
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )

    # Login route: Redirects users to Google for authentication
    @app.route('/login')
    def login():
        return google.authorize(callback=url_for('authorized', _external=True))

    # Authorized route: Handles callback after successful login
    @app.route('/login/authorized')
    def authorized():
        response = google.authorized_response()
        if response is None or response.get('access_token') is None:
            # Handle case where authentication failed
            return 'Access denied: reason={} error={}'.format(
                request.args['error_reason'],
                request.args['error_description']
            )
        
        # Save access token in session
        session['google_token'] = (response['access_token'], '')
        
        # Fetch user information from Google API
        user_info = google.get('userinfo').data
        session['user_id'] = user_info['id']

        # Check if user exists in the database
        user = users_collection.find_one({'email': user_info['email']})
        if not user:
            # Create a new user if they don't exist
            user = {
                'google_id': user_info['id'],
                'email': user_info['email'],
                'registration_timestamp': datetime.datetime.utcnow()
            }
            users_collection.insert_one(user)
        
        # Save user info in session
        session['user_info'] = user_info
        return redirect(url_for('index'))

    # Retrieve OAuth token for authenticated requests
    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')

else:
    # Placeholder routes when Google OAuth is disabled
    @app.route('/login')
    def login():
        return redirect(url_for('index'))

    @app.route('/login/authorized')
    def authorized():
        return redirect(url_for('index'))

# Connect to MongoDB using credentials from config
client = MongoClient(config.MONGODB_URI, config.MONGODB_PORT)
db = client[config.MONGODB_DB]
folders_collection = db[config.MONGODB_COLLECTION_FOLDERS]
users_collection = db[config.MONGODB_COLLECTION_USERS]
subscriptions_collection = db[config.MONGODB_COLLECTION_SUBSCRIPTIONS]
logs_collection = db[config.MONGODB_COLLECTION_LOGS]

# Recursive helper function to build hierarchical data structures
def build_structure(parts, data=None, extra_data=None):
    if not parts:
        # Merge extra data with provided data if applicable
        if extra_data is not None:
            data = {**extra_data, **data}
        return data
    
    current = parts.pop(0)
    
    if not current:
        # Skip empty strings in the structure
        return build_structure(parts, data, extra_data)
    
    return {current: build_structure(parts, data, extra_data)}

# Home page route
@app.route('/')
def index():
    # Retrieve user ID from session
    user_id = session.get('user_id')
    
    # Fetch user's subscriptions from the database
    user_subscriptions = subscriptions_collection.find_one({"user_id": user_id})
    subscribed_paths = set(user_subscriptions["subscriptions"]) if user_subscriptions else set()

    # Fetch folder data from MongoDB
    folder_documents = list(folders_collection.find({}))
    
    # Build a hierarchical structure from folder data
    folder_structure = {}
    skip_root_folder = True
    for doc in folder_documents:
        # Helper function to merge dictionaries recursively
        def merge(d1, d2):
            for k, v in d2.items():
                if isinstance(v, dict):
                    d1[k] = merge(d1.get(k, {}), v)
                else:
                    d1[k] = v
            return d1
        
        doc_id = str(doc['_id'])
        is_subscribed = doc_id in subscribed_paths

        # Split folder paths into parts
        parts = doc['path'][0].split('//')[1:] if isinstance(doc['path'], list) else doc['path'].split('//')[1:]
        if skip_root_folder and len(parts) == 1 and parts[0] == '':
            continue

        # Additional metadata for each folder
        extra_data = {"id": doc_id, "is_subscribed": is_subscribed}
        
        # Filter non-folder items
        courses = {item: doc['items'][item] for item in doc['items'] if not doc['items'][item]['is_folder']}

        # Build folder structure
        folder_structure = merge(folder_structure, build_structure(parts, {"Courses": courses}, extra_data))

    # Save the folder structure to a JSON file (optional debugging step)
    with open("folder_structure.json", "w") as outfile:
        json.dump(folder_structure, outfile)

    # Render the index page with the folder structure
    return render_template('index.html', folders=folder_structure)

# Subscribe to a folder
@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    folder_id = data.get('folder_id')
    user_id = session.get('user_id')

    # Add the folder ID to the user's subscriptions
    subscriptions_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"subscriptions": folder_id}},
        upsert=True
    )

    # Log the subscription action
    logs_collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "action": "subscribed",
        "path": folder_id
    })

    return jsonify({'status': 'success'})

# Unsubscribe from a folder
@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    data = request.json
    folder_id = data.get('folder_id')
    user_id = session.get('user_id')

    # Remove the folder ID from the user's subscriptions
    subscriptions_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"subscriptions": folder_id}}
    )

    # Log the unsubscription action
    logs_collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "action": "unsubscribed",
        "path": folder_id
    })

    return jsonify({'status': 'success'})

# Logout route: Clears the session
@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('user_info', None)
    return redirect(url_for('index'))

# About page route
@app.route('/about')
def about():
    return render_template('about.html')

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
