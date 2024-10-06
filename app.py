from flask import Flask, render_template, request, redirect, jsonify, url_for, session, flash
from pymongo import MongoClient
from AIfunction import generateTags
from flask_bcrypt import Bcrypt
import certifi
import math


app = Flask(__name__)
bcrypt = Bcrypt(app)


# MongoDB connection string
# Ensure that you replace <username>, <password>, and <dbname> with your actual values
MONGO_URI = 'mongodb+srv://jadlu150:V4ReGTptWi8mfWHw@charities.lmdjd.mongodb.net/?retryWrites=true&w=majority&appName=Charities'

# Connect to MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database('Charities')
charity_collection = db['Charity']
users_collection = db['Users']
db2 = client.get_database('fakeBank')
bank1_collection = db2['Bank1']

app.secret_key = "super secret key"
# Functions for the website
def get_accountId_from_email(email):
    user_data = users_collection.find_one({'email': email})
    return user_data.get('accountId') if user_data else None

#Routes
@app.route('/', methods=['POST', 'GET'])
def index():
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
        print(password)
        user = users_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['sessionEmail'] = email
            return render_template('search.html') # Redirect to the search page after successful login
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
            "amount": 0,
            "charity_name": {},
            "accountId": ""
        }
        try:
            users_collection.insert_one(user)
            session['sessionEmail'] = email
            return redirect(url_for('search'))
        except:
            return "An error has occurred. Please try again."

# function to help amountDisplay update amount
def check_new_transactions(accountID):
    new_transactions = bank1_collection.find({"accountId": accountID, "checked": 0})

    total_roundup = 0
    for transaction in new_transactions:
        amount = transaction['amount']

        rounded_amount = round(amount)
        roundup_value = rounded_amount - amount
        total_roundup += roundup_value
        bank1_collection.update_one({"_id": transaction['_id']}, {"$set": {"checked": 1}})
    
    return total_roundup


@app.route('/amountDisplay', methods=['POST', 'GET'])
def donationAmount():
    email = session['sessionEmail']
    user = users_collection.find_one({"email": email})

    if request.method == 'POST':
        new_amount = check_new_transactions(user['accountId']) + user['amount']

        users_collection.update_one({"email": email}, {"$set": {"amount": new_amount}})

    user = users_collection.find_one({"email": email})
    charity = charity_collection.find_one({"Name": user['charity_name']})
    _charityName = charity['Name']

    return render_template('amountDisplay.html', charity_name = _charityName, donation_amount = user['amount'])



def getTagsList(prompt):
    tags = generateTags(prompt)
    if tags[0] == "N/A":
        result = list(charity_collection.find({}).limit(10))
        return result
    if len(tags) > 1:
        print(f"{tags[0]}{tags[1]}")
        result = list(charity_collection.find({"Tag": tags[0]})) + list(charity_collection.find({"Tag": tags[1]}))
        return result
    else:
        return list(charity_collection.find({"Tag": tags.pop()}))

if __name__ == '__main__':
    app.run(debug=True)
