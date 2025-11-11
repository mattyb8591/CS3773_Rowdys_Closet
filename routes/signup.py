from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.security import generate_password_hash
import mysql.connector
import logging

signup_bp = Blueprint("signup", __name__, template_folder="templates", static_folder="static")

@signup_bp.route("/", methods=['GET', 'POST'])
def signup():
    print("=== SIGNUP ROUTE CALLED ===")  # Debug log
    print(f"Request method: {request.method}")  # Debug log
    
    if request.method == 'GET':
        print("GET request - returning signup form")  # Debug log
        return render_template("signup.html")

    data = request.get_json()
    print(f"Received data: {data}")  # Debug log
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    print(f"Username: {username}, Email: {email}, Password: {password}")  # Debug log

    if not username or not email or not password:
        print("Missing fields error")  # Debug log
        return jsonify({"error": "All fields are required"}), 400

    if len(password) < 6:
        print("Password too short error")  # Debug log
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    db = current_app.get_db_connection()
    if db is None:
        print("Database connection failed")  # Debug log
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor(dictionary=True)

    try:
        # Check if user already exists
        print("Checking if user exists...")  # Debug log
        cursor.execute("SELECT * FROM users WHERE email = %s OR username = %s", (email, username))
        existing = cursor.fetchone()
        print(f"Existing user check: {existing}")  # Debug log
        
        if existing:
            cursor.close()
            db.close()
            print("User already exists error")  # Debug log
            return jsonify({"error": "User with this email or username already exists"}), 400

        # Insert new user
        print("Creating password hash...")  # Debug log
        '''
            password_hash = generate_password_hash(password)
            not working at the moment
        '''
        password_hash = password
        print(f"Password hash created: {password_hash}")  # Debug log
        
        print("Executing INSERT query...")  # Debug log
        cursor.execute(
            "INSERT INTO users (username, email, password, account_type) VALUES (%s, %s, %s, %s)",
            (username, email, password_hash, "Customer")
        )

        print("Matching user to customer")
        cursor.execute(
            "SELECT user_id FROM users WHERE username = %s AND password = %s", (username, password)
        
        )

        userid = cursor.fetchone()
        print(userid)
        print("Adding user to customers")
        cursor.execute("INSERT INTO customers (user_id) VALUES (%s)", (userid["user_id"],)

        )

        #create a cart for the user when they create an account
        print("Creating a cart for the customer")
        cursor.execute(
        "SELECT customer_id FROM customers WHERE user_id = %s", (userid["user_id"],)
        )

        print("found the correct customer by searching userid")

        customerid = cursor.fetchone()
        print(customerid)
        cursor.execute(
        "INSERT INTO carts (customer_id) VALUES (%s)", (customerid["customer_id"],)
        )

        db.commit()
        print("User inserted successfully!")  # Debug log
        
        return jsonify({"message": "Account created successfully!"}), 201

    except mysql.connector.Error as e:
        print(f"Database error: {e}")  # Debug log
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debug log
        db.rollback()
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        cursor.close()
        db.close()