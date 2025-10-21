from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from werkzeug.security import generate_password_hash

signup_bp = Blueprint("signup", __name__, template_folder="templates", static_folder="static")

@signup_bp.route("/", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")

    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        flash("All fields are required.", "error")
        return render_template("signup.html")

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check if email already exists
    cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        flash("Email already registered.", "error")
        return render_template("signup.html")

    # Hash password and insert new user
    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO accounts (userName, email, passwordHash) VALUES (%s, %s, %s)",
        (username, email, password_hash)
    )
    db.commit()
    cursor.close()
    db.close()

    flash("Account created successfully! Please log in.", "success")
    return redirect(url_for("login.login"))


