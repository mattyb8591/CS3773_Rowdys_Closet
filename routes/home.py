from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app
import os
import mysql.connector
from werkzeug.security import check_password_hash

home_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static")

@home_bp.route("/", methods=["GET", "POST"])
def index():

    #db connection
    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        print("Database connection failed")  # Debug log
        return jsonify({"error": "Database connection failed"}), 500

    #create cursor
    cursor = db.cursor(dictionary=True)

    #check database if product is currently sold out
    cursor.execute("SELECT * FROM products WHERE stock < 1")

    soldout = cursor.fetchall()
    print(soldout)


    #if product is sold out send a request to js to alter the stock status of the product

    return render_template("home.html")