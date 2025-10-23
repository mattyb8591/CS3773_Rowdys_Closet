from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash

login_bp = Blueprint("login", __name__, template_folder="templates", static_folder="static")

@login_bp.route("/", methods=['GET', 'POST'])
def login():
    username =""
    password =""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

    if not username or not password:
        return render_template("index.html")

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username,password))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user is None:
        return render_template("index.html")
    else:
        return redirect(url_for("home.home"))

