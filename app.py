from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from wrkzeug.security import generate_password_hash

app = Flask(__name__)

client = MongoClient("mongodb+srv://jadlu150:V4ReGTptWi8mfWHw@charities.lmdjd.mongodb.net/")
db = client.charities_users
users_collection = db.users

@app.route('/')
def index():
    return render_template('sign.html')

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    hashed_password = generate_password_hash(password, method='sha256')

    user = {
        "name": name,
        "email": email,
        "password": hashed_password
    }

    try:
        users_collection.insert_one(user)
        return "Registered successfully!"
    except:
        return "An error has occurred. Please try again."

if __name__ == '__main__':
    app.run(debug=True)
