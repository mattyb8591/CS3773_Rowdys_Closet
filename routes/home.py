from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app, session, url_for
import os
import mysql.connector
from werkzeug.security import check_password_hash

home_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static")

def load_products():
    from app import get_db_connection
    db = get_db_connection()
    
    if db is None:
        return {}
    
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT product_id, name, price, stock, type, img_file_path, size, description
        FROM products 
        ORDER BY product_id
    """)
    
    all_products = cursor.fetchall()
    cursor.close()
    db.close()
    
    
    # Use dictionary with product name as key to automatically handle duplicates
    products_dict = {}
    
    for product in all_products:
        product_name = product['name']
        
        # If this product name is already in our dictionary, skip it
        if product_name in products_dict:
            continue
            
        products_dict[product_name] = {
            'product_id': product['product_id'],
            'name': product['name'],
            'price': product['price'],
            'type': product['type'],
            'img_file_path': product['img_file_path'],
            'description': product['description'],
            'stock': product['stock']
        }
    
    unique_products_list = list(products_dict.values())

    products_by_type = {
        'T-Shirts': [],
        'Hoodies': [], 
        'Jackets': [],
        'Headwear': [],
        'Bags': []
    }
    
    for product in unique_products_list:
        product_type = product['type']
        if product_type in products_by_type:
            products_by_type[product_type].append(product)
    
    #  debug output
    for product_type, products in products_by_type.items():
        product_names = [p['name'] for p in products]
    
    return products_by_type

@home_bp.route("/", methods=["GET"])
def index():

    products_by_type = load_products()
    return render_template("home.html", products_by_type=products_by_type, isAdmin=session["isAdmin"])

@home_bp.route("/api/products")
def get_products_api():
    products_by_type = load_products()
    return jsonify(products_by_type)

@home_bp.route("/debug-products")
def debug_products():
    products_by_type = load_products()
    
    debug_info = {}
    for product_type, products in products_by_type.items():
        debug_info[product_type] = {
            'count': len(products),
            'products': [p['name'] for p in products]
        }
    
    return jsonify(debug_info)


