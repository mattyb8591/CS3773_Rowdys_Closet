from flask import Flask, render_template, jsonify, request
import os
from routes.signup import signup_bp
from routes.login import login_bp
from routes.home import home_bp
from routes.cart import cart_bp
from routes.item import item_bp
from routes.profile import profile_bp


# for MySQL
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

app.register_blueprint(signup_bp, url_prefix="/signup")
app.register_blueprint(login_bp, url_prefix="/login")
app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(item_bp, url_prefix="/item")
app.register_blueprint(profile_bp, url_prefix="/profile")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="20.120.180.6",          # MySQL server
            user="rowdy",                 # MySQL username
            password="rowdyscloset",      # MySQL password
            database="rowdys_closet_db"   # Database name
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None



# renders the login page when visiting the URL
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signin():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/item')
def item():
    return render_template('item.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

# gets database data and sends it to the front end using  JSON

if __name__ == "__main__":
    app.run(debug=True)