from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash

login_bp = Blueprint("login", __name__, template_folder="templates", static_folder="static")

@login_bp.route("/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash("Please fill in all fields.", "error")
        return render_template("login.html")

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE userName = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if not user or not check_password_hash(user['passwordHash'], password):
        flash("Invalid username or password.", "error")
        return render_template("login.html")

    flash("Login successful!", "success")
    return redirect(url_for("home.home"))
