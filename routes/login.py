from flask import Flask, render_template, jsonify, request, Blueprint, redirect
import os
from werkzeug.security import check_password_hash
# for MySQL
import mysql.connector
from mysql.connector import Error
from app import get_db_connection

login_bp = Blueprint("login", __name__)



def login(): 
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