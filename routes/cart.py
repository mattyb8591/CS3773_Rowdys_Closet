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

    # Create cursor with buffered=True to avoid unread results
    cursor = db.cursor(dictionary=True, buffered=True)

    try:
        # Grab all products that are in the users cart
        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
        customer_id = cursor.fetchone()
        
        # Check if a customer exists for the the user
        if customer_id is None:
            user_cart_items = []
            cart_items_json = json.dumps(user_cart_items)
            print("No customer found for user")  # Debug log
            return render_template("cart.html", cartItemsJson=cart_items_json)
            
        customer_id = customer_id['customer_id']
        print(f"Customer ID: {customer_id}")  # Debug log
        
        # Get the current active cart for the customer
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart_id_data = cursor.fetchone()

        # Check if a cart exists for the customer
        if cart_id_data is None:
            user_cart_items = []
            print("No cart found for customer")  # Debug log
        else:
            cart_id = cart_id_data['cart_id']
            print(f"Cart ID: {cart_id}")  # Debug log
            
            # Updated query to include size from products table
            query = """ 
            SELECT 
                products.product_id as id, 
                products.name as name, 
                products.img_file_path as image, 
                products.price as price, 
                products.size as size,  -- Get size from products table
                products.type as category,
                COUNT(products.product_id) AS quantity
            FROM cart_products 
            INNER JOIN products ON cart_products.product_id = products.product_id 
            WHERE cart_products.cart_id = %s
            GROUP BY products.product_id, products.size  -- Group by both product_id and size
            """
            cursor.execute(query,(cart_id,))
            user_cart_items = cursor.fetchall()
            
            # Convert NULL sizes to "One Size" for display
            for item in user_cart_items:
                if item['size'] is None:
                    item['size'] = "One Size"
            
            print(f"Processed cart items with sizes: {user_cart_items}")  # Debug log
        
        cart_items_json = json.dumps(user_cart_items)
        print(f"Cart items JSON: {cart_items_json}")  # Debug log

        return render_template("cart.html", cartItemsJson=cart_items_json)
        
    except Exception as e:
        print(f"Error in cart index: {e}")
        return jsonify({"error": "Error loading cart"}), 500
    finally:
        cursor.close()
        db.close()

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
    size = data.get('size')  # Add size parameter
    change = data.get('change', 0)  # +1 for increment, -1 for decrement
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    # Convert "One Size" back to None for database query
    db_size_value = None if size == "One Size" else size

    cursor = db.cursor(dictionary=True, buffered=True)
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
            # Add item to cart - we don't store size in cart_products since it's in products table
            cursor.execute(
                "INSERT INTO cart_products (cart_id, product_id) VALUES (%s, %s)",
                (cart_id, product_id)
            )
        elif change < 0:
            # Remove one instance of the item
            # Since size is in products table, we need to join to filter by size
            if db_size_value is None:
                # Handle NULL size (One Size)
                cursor.execute("""
                    DELETE FROM cart_products 
                    WHERE cart_product_id IN (
                        SELECT cart_product_id FROM (
                            SELECT cp.cart_product_id 
                            FROM cart_products cp
                            INNER JOIN products p ON cp.product_id = p.product_id
                            WHERE cp.cart_id = %s AND cp.product_id = %s AND p.size IS NULL
                            LIMIT 1
                        ) AS tmp
                    )
                """, (cart_id, product_id))
            else:
                cursor.execute("""
                    DELETE FROM cart_products 
                    WHERE cart_product_id IN (
                        SELECT cart_product_id FROM (
                            SELECT cp.cart_product_id 
                            FROM cart_products cp
                            INNER JOIN products p ON cp.product_id = p.product_id
                            WHERE cp.cart_id = %s AND cp.product_id = %s AND p.size = %s
                            LIMIT 1
                        ) AS tmp
                    )
                """, (cart_id, product_id, db_size_value))
        
        db.commit()
        
        # Get updated quantity for this product with specific size
        if db_size_value is None:
            cursor.execute("""
                SELECT COUNT(*) as quantity 
                FROM cart_products cp
                INNER JOIN products p ON cp.product_id = p.product_id
                WHERE cp.cart_id = %s AND cp.product_id = %s AND p.size IS NULL
            """, (cart_id, product_id))
        else:
            cursor.execute("""
                SELECT COUNT(*) as quantity 
                FROM cart_products cp
                INNER JOIN products p ON cp.product_id = p.product_id
                WHERE cp.cart_id = %s AND cp.product_id = %s AND p.size = %s
            """, (cart_id, product_id, db_size_value))
        
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
    size = data.get('size')  # Add size parameter
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    # Convert "One Size" back to None for database query
    db_size_value = None if size == "One Size" else size

    cursor = db.cursor(dictionary=True, buffered=True)
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
        
        # Remove all instances of this product with specific size from cart
        if db_size_value is None:
            cursor.execute("""
                DELETE cp FROM cart_products cp
                INNER JOIN products p ON cp.product_id = p.product_id
                WHERE cp.cart_id = %s AND cp.product_id = %s AND p.size IS NULL
            """, (cart_id, product_id))
        else:
            cursor.execute("""
                DELETE cp FROM cart_products cp
                INNER JOIN products p ON cp.product_id = p.product_id
                WHERE cp.cart_id = %s AND cp.product_id = %s AND p.size = %s
            """, (cart_id, product_id, db_size_value))
        
        db.commit()
        
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error removing item: {e}")
        db.rollback()
        return jsonify({"error": "Error removing item"}), 500
    finally:
        cursor.close()
        db.close()

# The rest of cart.py remains the same...
@cart_bp.route("/api/checkout", methods=["POST"])
def checkout():
    from app import get_db_connection
    from decimal import Decimal
    db = get_db_connection()

    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    payment_type = data.get('payment_type')
    payment_details = data.get('payment_details', '')
    discount_code = data.get('discount_code')  # Get discount code from request
    shipping_method = data.get('shipping_method', 'standard')  # Get shipping method from request
    
    if not payment_type:
        return jsonify({"error": "Payment type is required"}), 400

    cursor = db.cursor(dictionary=True, buffered=True)
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
        
        # Calculate subtotal from cart items
        cursor.execute("""
            SELECT SUM(products.price) as subtotal
            FROM cart_products 
            INNER JOIN products ON cart_products.product_id = products.product_id 
            WHERE cart_products.cart_id = %s
        """, (current_cart_id,))
        
        total_result = cursor.fetchone()
        subtotal = total_result['subtotal'] if total_result and total_result['subtotal'] else Decimal('0.00')
        
        # Convert to float for calculations to avoid Decimal/float mixing
        subtotal_float = float(subtotal)
        
        # Calculate tax (8.25%)
        tax_rate = 0.0825
        tax_amount = subtotal_float * tax_rate
        
        # Calculate shipping cost based on selected method
        shipping_cost = 0.0
        if shipping_method == "standard":
            shipping_cost = 5.0
        elif shipping_method == "express":
            shipping_cost = 15.0
        # pickup is free (0.0)
        
        # Calculate total before discount (subtotal + tax + shipping)
        total_before_discount = subtotal_float + tax_amount + shipping_cost
        
        # Apply discount if provided
        final_total = total_before_discount
        applied_discount_code = None
        discount_amount = 0.0
        
        if discount_code:
            # Validate discount code
            cursor.execute("""
                SELECT * FROM discount_codes 
                WHERE code = %s AND is_active = TRUE 
                AND (expiration_date IS NULL OR expiration_date > NOW())
            """, (discount_code,))
            
            discount = cursor.fetchone()
            
            if discount:
                # Convert discount values to appropriate types
                discount_value = float(discount['value'])
                min_purchase = float(discount['min_purchase']) if discount['min_purchase'] else 0.0
                
                # Check minimum purchase requirement (based on subtotal as per e-commerce standards)
                if not discount['min_purchase'] or subtotal_float >= min_purchase:
                    applied_discount_code = discount_code
                    
                    if discount['discount_type'] == 'percentage':
                        # Percentage discounts apply to subtotal only (typical e-commerce practice)
                        discount_amount = subtotal_float * (discount_value / 100)
                    else:  # fixed amount
                        # Fixed discounts apply to the total (including tax and shipping)
                        discount_amount = min(discount_value, total_before_discount)
                    
                    final_total = max(0, total_before_discount - discount_amount)
        
        # Create payment record
        cursor.execute(
            "INSERT INTO payments (payment_type, details, status, customer_id) VALUES (%s, %s, %s, %s)",
            (payment_type, payment_details, 'completed', customer_id)
        )
        payment_id = cursor.lastrowid
        
        # Create order record using the current cart_id
        order_date = datetime.now()
        
        cursor.execute(
            "INSERT INTO orders (total, discount_code, order_status, order_date, customer_id, cart_id, payment_id, subtotal, tax_amount, shipping_cost, shipping_method) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                Decimal(str(final_total)), 
                applied_discount_code, 
                'completed', 
                order_date, 
                customer_id, 
                current_cart_id, 
                payment_id, 
                Decimal(str(subtotal_float)), 
                Decimal(str(tax_amount)), 
                Decimal(str(shipping_cost)), 
                shipping_method
            )
        )
        order_id = cursor.lastrowid
        
        # Delete all cart_products for this cart (clear the cart contents)
        cursor.execute("DELETE FROM cart_products WHERE cart_id = %s", (current_cart_id,))
        
        # We don't create a new cart - the customer will keep using the same cart ID
        # but it will be empty after checkout
        
        db.commit()
        
        return jsonify({
            "success": True,
            "message": "Order placed successfully!",
            "order_id": order_id,
            "payment_id": payment_id,
            "subtotal": subtotal_float,
            "tax_amount": tax_amount,
            "shipping_cost": shipping_cost,
            "discount_amount": discount_amount,
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
    
    cursor = db.cursor(dictionary=True, buffered=True)
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