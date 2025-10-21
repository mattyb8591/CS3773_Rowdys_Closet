from flask import Flask, render_template, jsonify, request, Blueprint, redirect
import os
from werkzeug.security import check_password_hash
# for MySQL

login_bp = Blueprint("login", __name__, template_folder="templates", static_folder="static")

login_bp.route("/login", methods = ['GET', 'POST'])
def index():
    return render_template("index.html")

def login(): 
    from app import get_db_connection
    conn = get_db_connection()
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
    cursor=conn.cursor()

    query="SELECT * FROM accounts Where userName=%s AND passwordHash=%s"
    cursor.execute(query, (username, password))
    if cursor.fetchall() is None:
        return jsonify({'error': 'Login failed'})
    else:
        return jsonify({'success':'Login successful'})