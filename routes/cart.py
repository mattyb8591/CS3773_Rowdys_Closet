from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session
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
    
    if "user_login" not in session:
        return redirect(url_for("login.login"))

    #create cursor
    cursor = db.cursor(dictionary=True)

    #grab all products that are in the users cart
    cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
    customer_id = cursor.fetchone()
    cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
    cart_id = cursor.fetchone()
    query = """ 
    
    SELECT cart_products.cart_id, products.name, products.img_file_path, products.price
    FROM cart_products 
    INNER JOIN products ON cart_products.product_id = products.product_id 
    WHERE cart_products.cart_id = %s

    """
    cursor.execute(query, (cart_id,))
    
    user_cart_items = cursor.fetchall()
    print(user_cart_items) #Debug log
    if not user_cart_items :
        print("Cart is empty")  # Debug log
        return jsonify({"success": False, "message": "Your cart is empty."}), 401 
    cursor.close()
    db.close()
    

    #return a list of all products to be rendered

    return render_template("cart.html", user_cart_items=user_cart_items)