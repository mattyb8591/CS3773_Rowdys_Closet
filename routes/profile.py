from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app, session
import os
from werkzeug.security import check_password_hash

profile_bp = Blueprint("profile", __name__, template_folder="templates", static_folder="static")

@profile_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login.index"))
    
    user_id = session["user_id"]

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user is None:
        session.clear()
        return redirect(url_for("login.index"))

    return render_template("profile.html", user=user)


@profile_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.index"))