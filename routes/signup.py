from flask import render_template, jsonify, Blueprint, redirect, request, json, url_for
import os
from werkzeug.security import check_password_hash

signup_bp = Blueprint("signup", __name__, template_folder="templates", static_folder="static")

def generate_password_has():
    return

@signup_bp.route("/", methods=['POST', 'GET'])
def signup():

    username = ''
    email = ''
    password = ''

    from app import get_db_connection
    conn = get_db_connection()

    if request.method == 'POST':
        
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
    '''
    #browser throws error that fields are empty find out how to populate data
    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

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
    '''
    return render_template("signup.html")
    # return jsonify({"message": "User created successfully"}), 201

