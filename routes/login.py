from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, session

login_bp = Blueprint("login", __name__, template_folder="templates", static_folder="static")

@login_bp.route("/", methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if "user_id" in session:
        if session.get("isAdmin"):
            return redirect(url_for("admin.index"))
        else:
            return redirect(url_for("home.index"))

    if request.method == 'GET':
        return render_template("index.html")

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Please fill in all fields."}), 400

    db = current_app.get_db_connection()
    if not db:
        return jsonify({"success": False, "message": "Database connection failed."}), 500
        
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        db.close()
        return jsonify({"success": False, "message": "Invalid username or password."}), 401
    
    cursor.execute("SELECT * FROM admins WHERE user_id = %s", (user["user_id"],))
    adminRow = cursor.fetchone()
    
    cursor.close()
    db.close()

    # Clear any existing session data first
    session.clear()
    
    # Set session data
    session["user_id"] = user["user_id"]
    session["username"] = user["username"]
    session["email"] = user["email"]
    session["isAdmin"] = bool(adminRow)

    # Force session to be saved immediately
    session.modified = True
    session.accessed = True
    
    # Debug logging
    print(f"Login successful - User: {user['username']}, Admin: {bool(adminRow)}")
    print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'unknown'}")
    print(f"Session data set: user_id={session.get('user_id')}, isAdmin={session.get('isAdmin')}")

    # Create a response with redirect to ensure session is saved
    if adminRow:
        print("Redirecting to admin index")
        response = redirect(url_for("admin.index"))
        return response
    else:
        print("Redirecting to home index")
        response = redirect(url_for("home.index"))
        return response