from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session, json
import os
from werkzeug.security import check_password_hash

cart_bp = Blueprint("cart", __name__, template_folder="templates", static_folder="static")

@cart_bp.route("/", methods=["GET"])
def index():

    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        print("Database connection failed")  # Debug log
        return jsonify({"error": "Database connection failed"}), 500
    
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    #create cursor
    cursor = db.cursor(dictionary=True)

    #grab all products that are in the users cart
    cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
    customer_id = cursor.fetchone()
    customer_id = customer_id['customer_id']
    print(customer_id) #Debug log
    cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
    cart_id = cursor.fetchone()
    cart_id = cart_id['cart_id']
    query = """ 
    
    SELECT products.product_id as id, 
    products.name as name, 
    products.img_file_path as image, 
    products.price as price, 
    products.size as size, 
    products.type as category
    COUNT(products.product_id) AS quantity
    FROM cart_products 
    INNER JOIN products ON cart_products.product_id = products.product_id 
    WHERE cart_products.cart_id = %s

    """
    cursor.execute(query,(cart_id,))
    
    user_cart_items = cursor.fetchall()
    print(user_cart_items) #Debug log
    if not user_cart_items :
        print("No items found in cart")
        jsonify([])
        
        return render_template("cart.html", cartItems=[])
    cursor.close()

    db.close()
    

    #return a list of all products to be rendered
    if request.method == 'GET':
        cart_items=request.form.get("cartItems")
        print(cart_items)
        print(user_cart_items)
        return render_template("cart.html", cartItems=user_cart_items)
    