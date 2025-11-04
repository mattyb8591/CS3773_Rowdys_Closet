from flask import Blueprint, render_template, redirect, url_for, current_app, session

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

    if not user:
        cursor.close()
        db.close()
        session.clear()
        return redirect(url_for("login.index"))

    address = None
    if user.get("address_id"):
        cursor.execute("SELECT * FROM addresses WHERE address_id = %s", (user["address_id"],))
        address = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("profile.html", user=user, address=address)


@profile_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.index"))
