from flask import Flask, render_template, jsonify, request
import os

# for MySQL
import mysql.connector
from mysql.connector import Error

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
        