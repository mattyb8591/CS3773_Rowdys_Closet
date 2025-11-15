from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session
import os
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="20.120.180.6",
            user="rowdy",
            password="rowdyscloset",
            database="rowdys_closet_db"
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

@admin_bp.before_request
def require_admin():
    if 'user_id' not in session:
        print("Admin before_request: No user_id in session, redirecting to login")
        return redirect(url_for('login.login'))
        
    if not session.get("isAdmin"):  # Changed to .get() to avoid KeyError
        print("Admin before_request: User is not admin, redirecting to home")
        return redirect(url_for('home.index'))
    
    print("Admin before_request: User is admin, allowing access")

@admin_bp.route("/")
def index():
    print("Admin index: Redirecting to dashboard")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route("/dashboard")
def dashboard(): 
    conn = get_db_connection()

    stats = {
        'total_orders': 0,
        'total_users': 0,
        'total_products': 0
    }

    if conn:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) FROM orders")
        stats['total_orders'] = cursor.fetchone()['COUNT(*)']

        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()['COUNT(*)']

        cursor.execute("SELECT COUNT(*) FROM products")
        stats['total_products'] = cursor.fetchone()['COUNT(*)']
            
        cursor.close()
        conn.close()
    
    return render_template("admin-dashboard.html", stats=stats, username=session['username'])

@admin_bp.route("/users")
def user_list():
    return render_template("user-list.html")

@admin_bp.route("/products")
def product_list():
    return render_template("items-list.html")

@admin_bp.route("/discounts")
def discount_list():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM discount_codes")
        discounts = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("discount-codes.html", discounts=discounts)
    return render_template("discount-codes.html", discounts=[])

@admin_bp.route("/discounts/new", methods=['GET', 'POST'])
def new_discount():
    if request.method == 'POST':
        code = request.form.get('code')
        discount_type = request.form.get('discount_type')
        value = request.form.get('value')
        min_purchase = request.form.get('min_purchase')
        expiration_date = request.form.get('expiration_date')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO discount_codes (code, discount_type, value, min_purchase, expiration_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (code, discount_type, value, min_purchase or None, expiration_date or None))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('admin.discount_list'))
    
    return render_template("new-discount.html")

def calculate_order_status(order_date, shipping_method):
    """Calculate order status based on time elapsed and shipping method"""
    now = datetime.now()
    
    # Handle both string and datetime objects
    if isinstance(order_date, str):
        try:
            order_datetime = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                order_datetime = datetime.strptime(order_date, '%Y-%m-%d')
            except ValueError:
                order_datetime = now
    else:
        order_datetime = order_date
    
    hours_since_order = (now - order_datetime).total_seconds() / 3600
    
    if shipping_method == 'express':
        if hours_since_order < 1:
            return 'Processing'
        elif hours_since_order < 6:
            return 'Shipped'
        elif hours_since_order < 24:
            return 'Out for Delivery'
        else:
            return 'Delivered'
    
    elif shipping_method == 'standard':
        if hours_since_order < 4:
            return 'Processing'
        elif hours_since_order < 24:
            return 'Shipped'
        elif hours_since_order < 72:
            return 'In Transit'
        else:
            return 'Delivered'
    
    elif shipping_method == 'pickup':
        if hours_since_order < 2:
            return 'Processing'
        elif hours_since_order < 6:
            return 'Ready for Pickup'
        else:
            return 'Picked Up'
    
    return 'Processing'

# API Routes for User Management
@admin_bp.route("/api/users")
def api_users():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.user_id, u.username, u.email, u.phone_number, 
                CONCAT(a.street_number, " ", a.street_name, ", ", a.city, ", ", a.state_abrev, " ", a.zip_code) AS full_address,
                CASE WHEN ad.user_id IS NOT NULL THEN 'Admin' ELSE 'Customer' END AS user_role
            FROM users u
            LEFT JOIN addresses a ON u.address_id = a.address_id
            LEFT JOIN admins ad ON u.user_id = ad.user_id
            ORDER BY u.user_id DESC;
                       """)
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users)

    return jsonify([])

@admin_bp.route("/api/users/<int:user_id>")
def api_user_detail(user_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.user_id, u.username, u.email, u.phone_number, 
                a.street_number, a.street_name, a.city, a.state_abrev, a.zip_code,
                CASE WHEN ad.user_id IS NOT NULL THEN 'Admin' ELSE 'Customer' END AS user_role
            FROM users u
            LEFT JOIN addresses a ON u.address_id = a.address_id
            LEFT JOIN admins ad ON u.user_id = ad.user_id
            WHERE u.user_id = %s
        """, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@admin_bp.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    street_number = data.get('street_number')
    street_name = data.get('street_name')
    city = data.get('city')
    state_abrev = data.get('state_abrev')
    zip_code = data.get('zip_code')
    user_role = data.get('user_role', 'Customer')
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email and password are required"}), 400
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Start transaction
            conn.start_transaction()
            
            # First insert address if provided
            address_id = None
            if street_number and street_name and city and state_abrev and zip_code:
                cursor.execute("""
                    INSERT INTO addresses (street_number, street_name, city, state_abrev, zip_code)
                    VALUES (%s, %s, %s, %s, %s)
                """, (street_number, street_name, city, state_abrev, zip_code))
                address_id = cursor.lastrowid
            
            # Insert user
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, phone_number, address_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, hashed_password, phone_number, address_id))
            user_id = cursor.lastrowid
            
            # If user is admin, insert into admins table
            if user_role == 'Admin':
                cursor.execute("INSERT INTO admins (user_id) VALUES (%s)", (user_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True, "user_id": user_id})
            
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "Username or email already exists"}), 400
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/api/users/<int:user_id>", methods=["PUT"])
def api_update_user(user_id):
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    phone_number = data.get('phone_number')
    street_number = data.get('street_number')
    street_name = data.get('street_name')
    city = data.get('city')
    state_abrev = data.get('state_abrev')
    zip_code = data.get('zip_code')
    user_role = data.get('user_role')
    
    if not username or not email:
        return jsonify({"error": "Username and email are required"}), 400
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            
            # Get current user data to find address_id
            cursor.execute("SELECT address_id FROM users WHERE user_id = %s", (user_id,))
            current_user = cursor.fetchone()
            current_address_id = current_user[0] if current_user else None
            
            # Update or insert address
            if street_number and street_name and city and state_abrev and zip_code:
                if current_address_id:
                    # Update existing address
                    cursor.execute("""
                        UPDATE addresses 
                        SET street_number = %s, street_name = %s, city = %s, state_abrev = %s, zip_code = %s
                        WHERE address_id = %s
                    """, (street_number, street_name, city, state_abrev, zip_code, current_address_id))
                else:
                    # Insert new address
                    cursor.execute("""
                        INSERT INTO addresses (street_number, street_name, city, state_abrev, zip_code)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (street_number, street_name, city, state_abrev, zip_code))
                    current_address_id = cursor.lastrowid
            else:
                # No address provided, set to NULL
                current_address_id = None
            
            # Update user
            if password:
                hashed_password = generate_password_hash(password)
                cursor.execute("""
                    UPDATE users 
                    SET username = %s, email = %s, password_hash = %s, phone_number = %s, address_id = %s
                    WHERE user_id = %s
                """, (username, email, hashed_password, phone_number, current_address_id, user_id))
            else:
                cursor.execute("""
                    UPDATE users 
                    SET username = %s, email = %s, phone_number = %s, address_id = %s
                    WHERE user_id = %s
                """, (username, email, phone_number, current_address_id, user_id))
            
            # Update admin status
            cursor.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
            if user_role == 'Admin':
                cursor.execute("INSERT INTO admins (user_id) VALUES (%s)", (user_id,))
                
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True})
            
        except mysql.connector.IntegrityError as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "Username or email already exists"}), 400
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    # Prevent admin from deleting themselves
    if user_id == session.get('user_id'):
        return jsonify({"error": "You cannot delete your own account"}), 400
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            
            # Get user's address_id before deletion
            cursor.execute("SELECT address_id FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            address_id = user[0] if user else None
            
            # Delete from admins table first (foreign key constraint)
            cursor.execute("DELETE FROM admins WHERE user_id = %s", (user_id,))
            
            # Delete user
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            
            # Delete address if it exists and no other users are using it
            if address_id:
                cursor.execute("SELECT COUNT(*) FROM users WHERE address_id = %s", (address_id,))
                address_users = cursor.fetchone()[0]
                if address_users == 0:
                    cursor.execute("DELETE FROM addresses WHERE address_id = %s", (address_id,))
            
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            
            if affected_rows > 0:
                return jsonify({"success": True})
            else:
                return jsonify({"error": "User not found"}), 404
                
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

# API Routes for Product Management
@admin_bp.route("/api/products")
def api_products():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY product_id DESC")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(products)
    return jsonify([])

@admin_bp.route("/api/products/<int:product_id>")
def api_product_detail(product_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        if product:
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

# In admin.py - Update the product creation and update endpoints

@admin_bp.route("/api/products", methods=["POST"])
def api_create_product():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    original_price = data.get('original_price')
    discount = data.get('discount', 0)
    size = data.get('size')
    stock = data.get('stock')
    type = data.get('type')
    img_file_path = data.get('img_file_path')
    
    if not name or not type or original_price is None or stock is None:
        return jsonify({"error": "Name, type, original price, and stock are required"}), 400
    
    # Validate discount range
    if discount < 0 or discount > 100:
        return jsonify({"error": "Discount must be between 0 and 100 percent"}), 400
    
    # Calculate final price
    final_price = original_price * (1 - discount / 100)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if product with same attributes already exists
            cursor.execute("""
                SELECT COUNT(*) as count FROM products 
                WHERE name = %s AND type = %s AND size <=> %s AND original_price = %s 
                AND discount = %s AND description <=> %s AND img_file_path <=> %s
            """, (name, type, size, original_price, discount, description, img_file_path))
            duplicate_count = cursor.fetchone()['count']
            
            if duplicate_count > 0:
                return jsonify({"error": "A product with these exact attributes already exists."}), 400
            
            # Apply common attributes to all sizes of the same product (EXCEPT stock and size)
            cursor.execute("""
                UPDATE products 
                SET description = %s, original_price = %s, discount = %s, 
                    price = original_price * (1 - %s / 100), type = %s, img_file_path = %s
                WHERE name = %s AND type = %s AND img_file_path <=> %s
            """, (description, original_price, discount, discount, type, img_file_path, name, type, img_file_path))
            
            # Insert new product with calculated price
            cursor.execute("""
                INSERT INTO products (name, description, original_price, discount, price, size, stock, type, img_file_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, description, original_price, discount, final_price, size, stock, type, img_file_path))
            conn.commit()
            product_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return jsonify({"success": True, "product_id": product_id})
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/api/products/<int:product_id>", methods=["PUT"])
def api_update_product(product_id):
    data = request.json
    name = data.get('name')
    description = data.get('description')
    original_price = data.get('original_price')
    discount = data.get('discount', 0)
    size = data.get('size')
    stock = data.get('stock')
    type = data.get('type')
    img_file_path = data.get('img_file_path')
    
    if not name or not type or original_price is None or stock is None:
        return jsonify({"error": "Name, type, original price, and stock are required"}), 400
    
    # Validate discount range
    if discount < 0 or discount > 100:
        return jsonify({"error": "Discount must be between 0 and 100 percent"}), 400
    
    # Calculate final price
    final_price = original_price * (1 - discount / 100)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Get current product data to identify product group
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
            current_product = cursor.fetchone()
            
            if not current_product:
                return jsonify({"error": "Product not found"}), 404
            
            # Check for duplicate product (excluding current product)
            cursor.execute("""
                SELECT COUNT(*) as count FROM products 
                WHERE name = %s AND type = %s AND size <=> %s AND original_price = %s 
                AND discount = %s AND description <=> %s AND img_file_path <=> %s
                AND product_id != %s
            """, (name, type, size, original_price, discount, description, img_file_path, product_id))
            duplicate_count = cursor.fetchone()['count']
            
            if duplicate_count > 0:
                return jsonify({"error": "A product with these exact attributes already exists."}), 400
            
            # Apply common attributes to all sizes of the same product (EXCEPT stock and size)
            cursor.execute("""
                UPDATE products 
                SET name = %s, description = %s, original_price = %s, discount = %s, 
                    price = original_price * (1 - %s / 100), type = %s, img_file_path = %s
                WHERE name = %s AND type = %s AND img_file_path <=> %s
            """, (name, description, original_price, discount, discount, type, img_file_path, 
                  current_product['name'], current_product['type'], current_product['img_file_path']))
            
            # Now update the current product's specific attributes (size and stock)
            cursor.execute("""
                UPDATE products 
                SET size = %s, stock = %s
                WHERE product_id = %s
            """, (size, stock, product_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"success": True})
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500


@admin_bp.route("/api/products/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            
            if affected_rows > 0:
                return jsonify({"success": True})
            else:
                return jsonify({"error": "Product not found"}), 404
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/api/discounts")
def api_discounts():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM discount_codes 
            ORDER BY created_at DESC
        """)
        discounts = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(discounts)
    return jsonify([])

@admin_bp.route("/api/discounts/<int:discount_id>")
def api_discount_detail(discount_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM discount_codes WHERE discount_id = %s", (discount_id,))
        discount = cursor.fetchone()
        cursor.close()
        conn.close()
        if discount:
            return jsonify(discount)
    return jsonify({"error": "Discount code not found"}), 404

@admin_bp.route("/api/discounts", methods=["POST"])
def api_create_discount():
    data = request.json
    code = data.get('code')
    discount_type = data.get('discount_type', 'percentage')
    value = data.get('value')
    min_purchase = data.get('min_purchase', 0)
    expiration_date = data.get('expiration_date')
    is_active = data.get('is_active', True)
    
    if not code or not value:
        return jsonify({"error": "Code and value are required"}), 400
    
    # Validate discount value based on type
    if discount_type == 'percentage' and (value < 0 or value > 100):
        return jsonify({"error": "Percentage discount must be between 0 and 100"}), 400
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO discount_codes (code, discount_type, value, min_purchase, expiration_date, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (code, discount_type, value, min_purchase or 0, expiration_date or None, is_active))
            conn.commit()
            discount_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return jsonify({"success": True, "discount_id": discount_id})
        except mysql.connector.IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "Discount code already exists"}), 400
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/api/discounts/<int:discount_id>", methods=["PUT"])
def api_update_discount(discount_id):
    data = request.json
    code = data.get('code')
    discount_type = data.get('discount_type', 'percentage')
    value = data.get('value')
    min_purchase = data.get('min_purchase', 0)
    expiration_date = data.get('expiration_date')
    is_active = data.get('is_active', True)
    
    if not code or not value:
        return jsonify({"error": "Code and value are required"}), 400
    
    # Validate discount value based on type
    if discount_type == 'percentage' and (value < 0 or value > 100):
        return jsonify({"error": "Percentage discount must be between 0 and 100"}), 400
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE discount_codes 
                SET code = %s, discount_type = %s, value = %s, min_purchase = %s, 
                    expiration_date = %s, is_active = %s
                WHERE discount_id = %s
            """, (code, discount_type, value, min_purchase or 0, expiration_date or None, is_active, discount_id))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            
            if affected_rows > 0:
                return jsonify({"success": True})
            else:
                return jsonify({"error": "Discount code not found"}), 404
        except mysql.connector.IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": "Discount code already exists"}), 400
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/api/discounts/<int:discount_id>", methods=["DELETE"])
def api_delete_discount(discount_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM discount_codes WHERE discount_id = %s", (discount_id,))
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()
            
            if affected_rows > 0:
                return jsonify({"success": True})
            else:
                return jsonify({"error": "Discount code not found"}), 404
        except Error as e:
            conn.rollback()
            cursor.close()
            conn.close()
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@admin_bp.route("/orders")
def order_history():
    return render_template("order-history.html")

# API Routes for Order Management
@admin_bp.route("/api/orders")
def api_orders():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                o.order_id,
                o.total,
                o.discount_code,
                o.order_date,
                o.customer_id,
                u.username,
                o.payment_id,
                p.payment_type,
                o.shipping_method,
                o.order_status
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN users u ON c.user_id = u.user_id
            LEFT JOIN payments p ON o.payment_id = p.payment_id
            ORDER BY o.order_date DESC
        """)
        orders = cursor.fetchall()
        
        # Calculate dynamic status for each order
        for order in orders:
            if order['order_status'] == 'completed':  # Only calculate for completed orders
                order['dynamic_status'] = calculate_order_status(order['order_date'], order.get('shipping_method', 'standard'))
            else:
                order['dynamic_status'] = order['order_status']
        
        cursor.close()
        conn.close()
        return jsonify(orders)
    return jsonify([])

@admin_bp.route("/api/orders/<int:order_id>")
def api_order_detail(order_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get order basic information
        cursor.execute("""
            SELECT 
                o.order_id,
                o.total,
                o.subtotal,
                o.tax_amount,
                o.shipping_cost,
                o.discount_code,
                o.order_status as status,
                o.order_date,
                o.customer_id,
                u.username,
                u.email,
                u.phone_number,
                o.payment_id,
                p.payment_type,
                o.shipping_method,
                CONCAT(a.street_number, ' ', a.street_name, ', ', a.city, ', ', a.state_abrev, ' ', a.zip_code) as shipping_address
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN users u ON c.user_id = u.user_id
            LEFT JOIN addresses a ON u.address_id = a.address_id
            LEFT JOIN payments p ON o.payment_id = p.payment_id
            WHERE o.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        if order:
            # Calculate dynamic status
            if order['status'] == 'completed':
                order['dynamic_status'] = calculate_order_status(order['order_date'], order.get('shipping_method', 'standard'))
            else:
                order['dynamic_status'] = order['status']
            
            # Get order items
            cursor.execute("""
                SELECT 
                    oi.product_id,
                    p.name as product_name,
                    p.size,
                    oi.price,
                    oi.quantity
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            order_items = cursor.fetchall()
            order['items'] = order_items
        
        cursor.close()
        conn.close()
        
        if order:
            return jsonify(order)
    
    return jsonify({"error": "Order not found"}), 404