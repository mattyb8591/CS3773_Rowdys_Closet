from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session, json
import os
from werkzeug.security import check_password_hash
from datetime import datetime

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

@cart_bp.route("/api/update-quantity", methods=["POST"])
def update_quantity():
    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    product_id = data.get('product_id')
    change = data.get('change', 0)  # +1 for increment, -1 for decrement
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    cursor = db.cursor(dictionary=True)
    try:
        # Get customer_id and cart_id
        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
        customer = cursor.fetchone()
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
            
        customer_id = customer['customer_id']
        
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
        
        if not cart:
            # Create a new cart if it doesn't exist
            cursor.execute("INSERT INTO carts (customer_id) VALUES (%s)", (customer_id,))
            db.commit()
            cart_id = cursor.lastrowid
        else:
            cart_id = cart['cart_id']
        
        if change > 0:
            # Add item to cart
            cursor.execute(
                "INSERT INTO cart_products (cart_id, product_id) VALUES (%s, %s)",
                (cart_id, product_id)
            )
        elif change < 0:
            # Remove one instance of the item
            cursor.execute("""
                DELETE FROM cart_products 
                WHERE cart_product_id IN (
                    SELECT cart_product_id FROM (
                        SELECT cart_product_id 
                        FROM cart_products 
                        WHERE cart_id = %s AND product_id = %s 
                        LIMIT 1
                    ) AS tmp
                )
            """, (cart_id, product_id))
        
        db.commit()
        
        # Get updated quantity for this product
        cursor.execute("""
            SELECT COUNT(*) as quantity 
            FROM cart_products 
            WHERE cart_id = %s AND product_id = %s
        """, (cart_id, product_id))
        
        result = cursor.fetchone()
        new_quantity = result['quantity'] if result else 0
        
        return jsonify({
            "success": True,
            "new_quantity": new_quantity
        })
        
    except Exception as e:
        print(f"Error updating quantity: {e}")
        db.rollback()
        return jsonify({"error": "Error updating quantity"}), 500
    finally:
        cursor.close()
        db.close()

@cart_bp.route("/api/remove-item", methods=["POST"])
def remove_item():
    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    cursor = db.cursor(dictionary=True)
    try:
        # Get customer_id and cart_id
        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
        customer = cursor.fetchone()
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
            
        customer_id = customer['customer_id']
        
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
        
        if not cart:
            return jsonify({"error": "Cart not found"}), 404
            
        cart_id = cart['cart_id']
        
        # Remove all instances of this product from cart
        cursor.execute(
            "DELETE FROM cart_products WHERE cart_id = %s AND product_id = %s",
            (cart_id, product_id)
        )
        
        db.commit()
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error removing item: {e}")
        db.rollback()
        return jsonify({"error": "Error removing item"}), 500
    finally:
        cursor.close()
        db.close()

@cart_bp.route("/api/checkout", methods=["POST"])
def checkout():
    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    payment_type = data.get('payment_type')
    payment_details = data.get('payment_details', '')
    discount_code = data.get('discount_code')  # Get discount code from request
    
    if not payment_type:
        return jsonify({"error": "Payment type is required"}), 400

    cursor = db.cursor(dictionary=True)
    try:
        # Get customer_id and current cart
        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
        customer = cursor.fetchone()
        
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
            
        customer_id = customer['customer_id']
        
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        current_cart = cursor.fetchone()
        
        if not current_cart:
            return jsonify({"error": "Cart not found"}), 404
            
        current_cart_id = current_cart['cart_id']
        
        # Calculate total from cart items
        cursor.execute("""
            SELECT SUM(products.price) as subtotal
            FROM cart_products 
            INNER JOIN products ON cart_products.product_id = products.product_id 
            WHERE cart_products.cart_id = %s
        """, (current_cart_id,))
        
        total_result = cursor.fetchone()
        subtotal = total_result['subtotal'] if total_result and total_result['subtotal'] else 0.00
        
        # Apply discount if provided
        final_total = subtotal
        applied_discount_code = None
        
        if discount_code:
            # Validate discount code
            cursor.execute("""
                SELECT * FROM discount_codes 
                WHERE code = %s AND is_active = TRUE 
                AND (expiration_date IS NULL OR expiration_date > NOW())
            """, (discount_code,))
            
            discount = cursor.fetchone()
            
            if discount:
                # Check minimum purchase requirement
                if not discount['min_purchase'] or subtotal >= discount['min_purchase']:
                    applied_discount_code = discount_code
                    
                    if discount['discount_type'] == 'percentage':
                        discount_amount = subtotal * (discount['value'] / 100)
                    else:  # fixed amount
                        discount_amount = discount['value']
                    
                    final_total = max(0, subtotal - discount_amount)
        
        # Create payment record
        cursor.execute(
            "INSERT INTO payments (payment_type, details, status, customer_id) VALUES (%s, %s, %s, %s)",
            (payment_type, payment_details, 'completed', customer_id)
        )
        payment_id = cursor.lastrowid
        
        # Create order record using the current cart_id
        order_date = datetime.now()
        
        cursor.execute(
            "INSERT INTO orders (total, discount_code, order_status, order_date, customer_id, cart_id, payment_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (final_total, applied_discount_code, 'completed', order_date, customer_id, current_cart_id, payment_id)
        )
        order_id = cursor.lastrowid
        
        # Create a new empty cart for the customer
        cursor.execute("INSERT INTO carts (customer_id) VALUES (%s)", (customer_id,))
        new_cart_id = cursor.lastrowid
        
        db.commit()
        
        return jsonify({
            "success": True,
            "message": "Order placed successfully!",
            "order_id": order_id,
            "payment_id": payment_id,
            "new_cart_id": new_cart_id,
            "total": final_total,
            "discount_applied": applied_discount_code is not None
        })
        
    except Exception as e:
        print(f"Error during checkout: {e}")
        db.rollback()
        return jsonify({"error": "Error during checkout"}), 500
    finally:
        cursor.close()
        db.close()

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