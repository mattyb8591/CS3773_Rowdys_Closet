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
    
    # Check if a customer exists for the user
    if customer_id is None:
        user_cart_items = []
        cart_items_json = json.dumps(user_cart_items)
        print("No customer found for user")  # Debug log
        return render_template("cart.html", cartItemsJson=cart_items_json)
        
    customer_id = customer_id['customer_id']
    print(f"Customer ID: {customer_id}")  # Debug log
    
    cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
    cart_id_data = cursor.fetchone()

    # Check if a cart exists for the customer
    if cart_id_data is None:
        user_cart_items = []
        print("No cart found for customer")  # Debug log
    else:
        cart_id = cart_id_data['cart_id']
        print(f"Cart ID: {cart_id}")  # Debug log
        
        # Debug: Check what's in cart_products
        cursor.execute("SELECT * FROM cart_products WHERE cart_id = %s", (cart_id,))
        raw_cart_items = cursor.fetchall()
        print(f"Raw cart products: {raw_cart_items}")  # Debug log
        
        query = """ 
        SELECT products.product_id as id, 
        products.name as name, 
        products.img_file_path as image, 
        products.price as price, 
        products.size as size, 
        products.type as category,
        COUNT(products.product_id) AS quantity
        FROM cart_products 
        INNER JOIN products ON cart_products.product_id = products.product_id 
        WHERE cart_products.cart_id = %s
        GROUP BY products.product_id
        """
        cursor.execute(query,(cart_id,))
        user_cart_items = cursor.fetchall()
        print(f"Processed cart items: {user_cart_items}")  # Debug log
    
    cursor.close()
    db.close()
    
    cart_items_json = json.dumps(user_cart_items)
    print(f"Cart items JSON: {cart_items_json}")  # Debug log

    if request.method == 'GET':
        return render_template("cart.html", cartItemsJson=cart_items_json)

@cart_bp.route("/api/validate-discount", methods=["POST"])
def validate_discount():
    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    data = request.json
    code = data.get('code')
    subtotal = data.get('subtotal', 0)
    
    if not code:
        return jsonify({"error": "Promo code is required"}), 400
    
    cursor = db.cursor(dictionary=True)
    try:
        # Check if discount code exists and is valid
        cursor.execute("""
            SELECT * FROM discount_codes 
            WHERE code = %s AND is_active = TRUE 
            AND (expiration_date IS NULL OR expiration_date > NOW())
        """, (code,))
        
        discount = cursor.fetchone()
        
        if not discount:
            return jsonify({"error": "Invalid or expired promo code"}), 400
        
        # Check minimum purchase requirement
        if discount['min_purchase'] and discount['min_purchase'] > 0:
            if subtotal < discount['min_purchase']:
                return jsonify({
                    "error": f"Minimum purchase of ${discount['min_purchase']:.2f} required for this promo code"
                }), 400
        
        return jsonify({
            "valid": True,
            "discount": {
                "discount_id": discount['discount_id'],
                "code": discount['code'],
                "discount_type": discount['discount_type'],
                "value": float(discount['value']),
                "min_purchase": float(discount['min_purchase']) if discount['min_purchase'] else 0
            }
        })
        
    except Exception as e:
        print(f"Error validating discount: {e}")
        return jsonify({"error": "Error validating promo code"}), 500
    finally:
        cursor.close()
        db.close()