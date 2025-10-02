from flask import Flask, render_template, jsonify, request
import os

# for MySQL
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)

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
    username = request.form.get('username')
    password = request.form.get('password')
    
    #check if user already exists in the database

    #if they do not exists store information in db
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO accounts ()')


    #redirect the user to the home page

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

@app.route('/api/products')
def get_products():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    products_list = []
    for product in products:
        products_list.append({
            'productID': product['productID'],
            'productName': product['productName'],
            'numInStock': product['numInStock'],
            'price': float(product['price']),
            'rating': float(product['rating'])
        })

    return jsonify({'products': products_list})
    

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    with open('schema.sql', 'r') as f:
        sql_commands = f.read().split(';')
        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
    conn.commit()
    cursor.close()
    conn.close()


# REMOVE THIS WHEN USING MYSQL
if __name__ == '__main__':
    app.run(debug=True)