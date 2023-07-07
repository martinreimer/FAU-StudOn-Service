from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pymongo import MongoClient
from flask_oauthlib.client import OAuth
import datetime
import config
import json


app = Flask(__name__)

app.secret_key = 'random_secret'  # Use a real secret key in production

# OAuth Setup
oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=config.GOOGLE_CLIENT_ID,
    consumer_secret=config.GOOGLE_CLIENT_SECRET,
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['google_token'] = (response['access_token'], '')

    user_info = google.get('userinfo').data

    session['user_id'] = user_info['id']
    # Check if user already exists
    user = users_collection.find_one({'email': user_info['email']})
    
    # If user does not exist, create new user
    if not user:
        user = {
            'google_id': user_info['id'],  # Use Google ID as user ID
            'email': user_info['email'],
            'registration_timestamp': datetime.datetime.utcnow()
        }
        users_collection.insert_one(user)
    else:
        # user exists, you can update information or do something else
        pass
    session['user_info'] = user_info

    return redirect(url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')




# Connect to MongoDB
client = MongoClient(config.MONGODB_URI, config.MONGODB_PORT)
db = client[config.MONGODB_DB]
folders_collection =  db["" + config.MONGODB_COLLECTION_FOLDERS] 
users_collection = db[config.MONGODB_COLLECTION_USERS]
subscriptions_collection = db[config.MONGODB_COLLECTION_SUBSCRIPTIONS]
logs_collection = db[config.MONGODB_COLLECTION_LOGS]

def build_structure(parts, data, extra_data=None):
    if not parts:
        # Merge courses with additional data if provided
        if extra_data is not None:
            data = {**extra_data, **data}
        return data
    
    current = parts.pop(0)
    
    # If the current part is an empty string, merge data directly
    if not current:
        return build_structure(parts, data, extra_data)
    
    return {current: build_structure(parts, data, extra_data)}

@app.route('/')
def index():
    
    # Fetch user's subscriptions from the database
    user_id = session.get('user_id')
    user_subscriptions = subscriptions_collection.find_one({"user_id": user_id})
    if user_subscriptions:
        subscribed_paths = set(user_subscriptions["subscriptions"])
    else:
        subscribed_paths = set()

    # Fetch all folder documents from MongoDB
    folder_documents = list(folders_collection.find({}))
    
    # Building hierarchical data structure
    skip_root_folder = True
    folder_structure = {}
    for doc in folder_documents:
        # Merge nested dictionaries
        def merge(d1, d2):
            for k, v in d2.items():
                if isinstance(v, dict):
                    d1[k] = merge(d1.get(k, {}), v)
                else:
                    d1[k] = v
            return d1
        
        # Check if the path is in the user's subscriptions
        #print(subscribed_paths)
        doc_id = str(doc['_id'])
        is_subscribed = doc_id in subscribed_paths
        #print(f"doc['_id']: doc_id, is_subscribed: {is_subscribed}")
        # Parts of the path
        parts = doc['path'].split('//')[1:]  # Use '//' as a separator
        # Skip the root folder
        if skip_root_folder:
            if len(parts) == 1 and parts[0] == '':  # this is a super-folder
                continue
        # Extra data to be added
        extra_data = {"id": doc_id, "is_subscribed": is_subscribed}
        
        if doc_id =="64a7ee35492144b26091666f":
            print("doc_id: ", doc_id)
            print("doc: ", doc)
            print("parts: ", parts)
        # Build structure
        folder_structure = merge(folder_structure, build_structure(parts, {"items": doc['items']}, extra_data))

    with open("folder_structure.json", "w") as outfile:
        json.dump(folder_structure, outfile)


    # Render the hierarchical structure using template
    return render_template('index.html', folders=folder_structure)



@app.route('/subscribe', methods=['POST'])
def subscribe():
    # Get data from request
    data = request.json
    print("subscribed: ", data)
    folder_id = data.get('folder_id')
    user_id = session.get('user_id')

    
    # Update user subscriptions in the database
    subscriptions_collection.update_one(
        {"user_id": user_id},
        {"$addToSet": {"subscriptions": folder_id}},
        upsert=True
    )

    # Log the action
    logs_collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "action": "subscribed",
        "path": folder_id
    })
    
    # Return a response
    return jsonify({'status': 'success'})

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    # Get data from request
    data = request.json
    print("unsubscribed: ", data)
    folder_id = data.get('folder_id')
    user_id = session.get('user_id')

    # Update user subscriptions in the database
    subscriptions_collection.update_one(
        {"user_id": user_id},
        {"$pull": {"subscriptions": folder_id}}
    )

    # Log the action
    logs_collection.insert_one({
        "user_id": user_id,
        "timestamp": datetime.datetime.utcnow(),
        "action": "unsubscribed",
        "path": folder_id
    })
    
    # Return a response
    return jsonify({'status': 'success'})

@app.route('/logout')
def logout():
    # Clear the session
    session.pop('google_token', None)
    session.pop('user_info', None)
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)