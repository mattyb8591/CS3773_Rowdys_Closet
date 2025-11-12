from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session
import os
from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector
from mysql.connector import Error

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
        return redirect(url_for('login.login'))
        
    if not session["isAdmin"]:
        return redirect(url_for('home.index'))

@admin_bp.route("/")
def index():
    return render_template("admin.html")
    
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
        return render_template("admin-discounts.html", discounts=discounts)
    return render_template("admin-discounts.html", discounts=[])

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

@admin_bp.route("/orders")
def order_list():
    sort_by = request.args.get('sort', 'order_date')
    order = request.args.get('order', 'desc')
    
    valid_sorts = ['order_date', 'total', 'customer_id']
    valid_orders = ['asc', 'desc']
    
    if sort_by not in valid_sorts:
        sort_by = 'order_date'
    if order not in valid_orders:
        order = 'desc'
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        if sort_by == 'customer_id':
            order_by = f"o.customer_id {order}"
        else:
            order_by = f"o.{sort_by} {order}"
            
        cursor.execute(f"""
            SELECT o.order_id, o.total, o.discount_code, o.order_status, 
                   o.order_date, o.customer_id, c.username,
                   COUNT(cp.cart_product_id) as item_count
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id 
            LEFT JOIN cart_products cp ON o.cart_product_id = cp.cart_product_id
            GROUP BY o.order_id
            ORDER BY {order_by}
        """)
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("admin-orders.html", orders=orders, sort_by=sort_by, order=order)
    return render_template("admin-orders.html", orders=[])

@admin_bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        5
        # Get order details
        cursor.execute("""
            SELECT o.*, c.username, c.email, c.phone_number
            FROM orders o 
            JOIN customers c ON o.customer_id = c.customer_id 
            WHERE o.order_id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        # Get order items (from cart_products)
        cursor.execute("""
            SELECT cp.*, p.name, p.image_url, p.price
            FROM cart_products cp 
            JOIN products p ON cp.product_id = p.product_id 
            WHERE cp.cart_product_id = %s
        """, (order['cart_product_id'],))
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("order-detail.html", order=order, items=items)
    return redirect(url_for('admin.order_list'))

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

@admin_bp.route("/api/products", methods=["POST"])
def api_create_product():
    data = request.json
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    size = data.get('size')  # Can be 'Small', 'Medium', 'Large', or None for "One Size"
    stock = data.get('stock')
    type = data.get('type')
    img_file_path = data.get('img_file_path')
    
    if not name or not type or price is None or stock is None:
        return jsonify({"error": "Name, type, price, and stock are required"}), 400
    
    # Check for duplicate product
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Check if product with same attributes already exists
            cursor.execute("""
                SELECT COUNT(*) as count FROM products 
                WHERE name = %s AND type = %s AND size <=> %s AND price = %s 
                AND description <=> %s AND img_file_path <=> %s
            """, (name, type, size, price, description, img_file_path))
            duplicate_count = cursor.fetchone()['count']
            
            if duplicate_count > 0:
                return jsonify({"error": "A product with these exact attributes already exists."}), 400
            
            # Insert new product if no duplicate
            cursor.execute("""
                INSERT INTO products (name, description, price, size, stock, type, img_file_path)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, description, price, size, stock, type, img_file_path))
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
    price = data.get('price')
    size = data.get('size')  # Can be 'Small', 'Medium', 'Large', or None for "One Size"
    stock = data.get('stock')
    type = data.get('type')
    img_file_path = data.get('img_file_path')
    
    if not name or not type or price is None or stock is None:
        return jsonify({"error": "Name, type, price, and stock are required"}), 400
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            # Check for duplicate product (excluding current product)
            cursor.execute("""
                SELECT COUNT(*) as count FROM products 
                WHERE name = %s AND type = %s AND size <=> %s AND price = %s 
                AND description <=> %s AND img_file_path <=> %s
                AND product_id != %s
            """, (name, type, size, price, description, img_file_path, product_id))
            duplicate_count = cursor.fetchone()['count']
            
            if duplicate_count > 0:
                return jsonify({"error": "A product with these exact attributes already exists."}), 400
            
            # Update product if no duplicate
            cursor.execute("""
                UPDATE products 
                SET name = %s, description = %s, price = %s, size = %s, 
                    stock = %s, type = %s, img_file_path = %s
                WHERE product_id = %s
            """, (name, description, price, size, stock, type, img_file_path, product_id))
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