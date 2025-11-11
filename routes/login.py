from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, session

login_bp = Blueprint("login", __name__, template_folder="templates", static_folder="static")

@login_bp.route("/", methods=['GET', 'POST'])
def login():
    if "user_id" in session:
        return redirect(url_for("home.index"))

    if request.method == 'GET':
        return render_template("index.html")

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Please fill in all fields."}), 400

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM admins WHERE user_id = %s", (user["user_id"],))
    adminRow = cursor.fetchone()
    
    cursor.close()
    db.close()

    if user is None:
        return jsonify({"success": False, "message": "Invalid username or password."}), 401
    

    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["email"] = user["email"]

    if adminRow:
        print("is admin") #debug
        return redirect(url_for("home.index"))
    else:
        print("isnt admin") #debug
        return redirect(url_for("home.index"))
