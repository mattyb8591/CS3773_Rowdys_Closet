from flask import Flask, render_template, url_for, redirect
import os
from signup import signup_bp
from login import login_bp
from home import home_bp
from cart import cart_bp
from item import item_bp
from profile import profile_bp

# for MySQL
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

app.register_blueprint(login_bp, url_prefix="/")
app.register_blueprint(signup_bp, url_prefix="/signup")
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
# gets database data and sends it to the front end using  JSON
@app.route("/")
def index():
    return "Testing"


if __name__ == '__main__':
    app.run(debug=True)


