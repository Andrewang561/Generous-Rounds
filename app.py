from flask import Flask, render_template, request, redirect, jsonify, url_for
from pymongo import MongoClient
import certifi

app = Flask(__name__)

# MongoDB connection string
# Ensure that you replace <username>, <password>, and <dbname> with your actual values
MONGO_URI = 'mongodb+srv://jadlu150:V4ReGTptWi8mfWHw@charities.lmdjd.mongodb.net/?retryWrites=true&w=majority&appName=Charities'

# Connect to MongoDB
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.get_database('Charities')
charity_collection = db['Charity']
users_collection = db['user']

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

@app.route('/logbuttonlink')
def logbuttonlink():
    return render_template('log.html')

@app.route('/logbutton', methods=['POST'])
def logbutton():
    return redirect(url_for('logbuttonlink'))

@app.route('/signbuttonlink')
def signbuttonlink():
    return render_template('sign.html')

@app.route('/signbutton', methods=['POST'])
def signbutton():
    return redirect(url_for('signbuttonlink'))

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user = {
            "name": name,
            "email": email,
            "password": password
        }

        try:
            users_collection.insert_one(user)
            return redirect(url_for('search'))
        except:
            return "An error has occurred. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
