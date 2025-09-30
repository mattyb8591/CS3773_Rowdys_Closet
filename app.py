from flask import Flask, render_template, jsonify
import sqlite3
import os

'''
# for MySQL
import mysql.connector
from mysql.connector import Error
'''


app = Flask(__name__)

# connects with database 
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

'''
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="",       # MySQL server
            user="",   # MySQL username
            password="",  # MySQL password
            database=""   # Database name
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

'''

# renders the login page when visiting the URL
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/home')
def signin():
    return render_template('home.html')

@app.route('/profile')
def signin():
    return render_template('profile.html')

@app.route('/item')
def signin():
    return render_template('item.html')

@app.route('/cart')
def signin():
    return render_template('cart.html')

# gets database data and sends it to the front end using  JSON
@app.route('/api/products')
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    
    # Convert rows to list of dictionaries
    products_list = []
    for product in products:
        products_list.append({
            'productID': product['productID'],
            'productName': product['productName'],
            'numInStock': product['numInStock'],
            'price': float(product['price']),
            'rating': float(product['rating'])
        })
    
    # returns JSON response with the "products" data
    return jsonify({'products': products_list})

'''
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
    '''

def init_db():
    conn = sqlite3.connect('database.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

'''
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
'''

# REMOVE THIS WHEN USING MYSQL
if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists('database.db'):
        import init_db
        init_db()
    
    app.run(debug=True)