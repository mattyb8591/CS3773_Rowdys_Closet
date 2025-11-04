from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session
import os
from werkzeug.security import check_password_hash

cart_bp = Blueprint("cart", __name__, template_folder="templates", static_folder="static")

@cart_bp.route("/", methods=["GET"])
def index():

    from app import get_db_connection
    db = get_db_connection()

    if db is None:
        print("Database connection failed")  # Debug log
        return jsonify({"error": "Database connection failed"}), 500
    
    if "user_login" not in session:
        return redirect(url_for("login.index"))

    #create cursor
    cursor = db.cursor()

    #grab all products that are in the users cart
    cursor.execute("")
    

    #return a list of all products to be rendered

    return render_template("cart.html")