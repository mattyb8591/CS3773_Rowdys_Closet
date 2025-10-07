from flask import Flask, render_template, jsonify, request, Blueprint
import os
from werkzeug.security import check_password_hash
from app import get_db_connection

signup_bp = Blueprint("signup", __name__)

@signup_bp.route("/", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400
    
    conn = get_db_connection()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE email=%s", (email,))
    existing = cursor.fetchone()

    if existing:
        return jsonify({"error": "User already exists"}), 400
    
    password_hash = generate_password_has(password)
    cursor.execute(
        "INSERT INTO accounts(userName, email, passwordHash) VALUES (%s, %s, %s)", 
        (username, email, password_hash)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "User created successfully"}), 201
