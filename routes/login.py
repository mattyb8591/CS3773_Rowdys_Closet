from flask import Flask, render_template, jsonify, request, Blueprint
import os
from werkzeug.security import check_password_hash
# for MySQL
import mysql.connector
from mysql.connector import Error

login_bp = Blueprint("login", __name__)

def login():

     conn = get_db_connection()
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
    cursor=conn.cursor()

    query="SELECT * FROM users Where username=%s AND password=%s"
    cursor.execute(query, (username, password))n
    if cursor.fetchall() is None:
        return jsonify({'error': 'Login failed'})
    else:
        return jsonify({'success':'Login successful'})
        