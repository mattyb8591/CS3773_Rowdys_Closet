from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app
import os
import mysql.connector
from werkzeug.security import check_password_hash

home_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static")

@home_bp.route("/", methods=["GET", "POST"])
def index():

    db = current_app.get_db_connection()

    if db is None:
        print("Database connection failed")  # Debug log
        return jsonify({"error": "Database connection failed"}), 500

    cursor = db.cursor()
    #get all products from the db
    cursor.execute("SELECT * FROM PRODUCTS")
    #store the products
    products = cursor.fetchall()

    #send the products to the frontend

    #query the db for all products

    return render_template("home.html")