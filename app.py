from flask import Flask, render_template, request, redirect, jsonify, url_for, session, flash
from pymongo import MongoClient
from AIfunction import generateTags
from flask_bcrypt import Bcrypt
import certifi
from dotenv import load_dotenv
import os


app = Flask(__name__)
bcrypt = Bcrypt(app)

load_dotenv()

# MongoDB connection string
# Ensure that you replace <username>, <password>, and <dbname> with your actual values
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database('Charities')
charity_collection = db['Charity']
users_collection = db['Users']
app.secret_key = "super secret key"


# Functions for the website
def get_accountId_from_email(email):
    user_data = users_collection.find_one({'email': email})
    return user_data.get('accountId') if user_data else None


#Routes
@app.route('/', methods=['POST', 'GET'])
def index():
    session.pop('sessionEmail', None)
    return render_template('website.html')
    # charities_data = list(charity_collection.find())  # Fetch all documents from the collection
    # for charity in charities_data:
    #     charity['_id'] = str(charity['_id'])   # Convert ObjectId to string for JSON serialization
    
    # # Return data as JSON
    # return jsonify(charities_data)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/searchOnClick', methods=['POST', 'GET'])
def searchOnClick():
    if request.method == 'POST':
        prompt = request.form['searchPrompt']
        charityList = getTagsList(prompt)
        return render_template('list.html', charityList = charityList)
    else:
        return render_template('search.html')

#login page
@app.route('/logbutton', methods=['POST', 'GET'])
def logbutton():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({"email": email})

        if user and user['password'] == password:
            session['sessionEmail'] = email
            return redirect(url_for('search')) # Redirect to the search page after successful login
        else:
            flash('Please check your login details and try again.')

    return render_template('log.html')

@app.route('/signbutton')
def signbutton():
    return render_template('sign.html')

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        hashpassword = bcrypt.generate_password_hash(password)

        user = {
            "name": name,
            "email": email,
            "password": hashpassword,
            "amount": 0
        }
        try:
            users_collection.insert_one(user)
            return redirect(url_for('search'))
        except:
            return "An error has occurred. Please try again."


@app.route('/amountDisplay', methods=['POST', 'GET'])
def amountDisplay():
    email = session['sessionEmail'] 
    user_data = users_collection.find_one({'email': email})
    _amount = user_data.get('amount')
    charityName = user_data.get('charity_name')
    _charity = charity_collection.find_one({'_id': charityName})

    return render_template('amountDisplay.html', donation_amount = _amount , charity_name = _charity)

def getTagsList(prompt):
    tags = generateTags(prompt)
    if tags[0] == "N/A":
        result = charity_collection.find({}).limit(10)
        return result
    if len(tags) > 1:
        print(f"{tags[0]}{tags[1]}")
        result = list(charity_collection.find({"Tag": tags[0]})) + list(charity_collection.find({"Tag": tags[1]}))
        return result
    else:
        return charity_collection.find({"Tag": tags.pop()})

if __name__ == '__main__':
    app.run(debug=True)
