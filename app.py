from flask import Flask, render_template, jsonify
import sqlite3
import os

'''
sqlite3 will be used to create a self contained database system for our website
will allow for python to interact with our "database"

flask will be used for python to communicate with javascript
'''

app = Flask(__name__)

# connects with database 
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# renders the HTML template when visiting the URL
@app.route('/')
def index():
    return render_template('index.html')

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

def init_db():
    conn = sqlite3.connect('database.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize database if it doesn't exist
    if not os.path.exists('database.db'):
        import init_db
        init_db()
    
    app.run(debug=True)