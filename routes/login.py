from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.security import check_password_hash

login_bp = Blueprint("login", __name__, template_folder="templates", static_folder="static")

@login_bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")

    username = request.form['username']
    password = request.form['password']

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM accounts WHERE userName = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()

    if user is None:
        return jsonify({'error': 'Invalid username or password'})

    if not check_password_hash(user['passwordHash'], password):
        return jsonify({'error': 'Invalid username or password'})

    return jsonify({'success': 'Login successful', 'user': user['userName']})
