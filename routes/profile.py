from flask import Blueprint, render_template, redirect, url_for, current_app, session, request, jsonify

profile_bp = Blueprint("profile", __name__, template_folder="templates", static_folder="static")

@profile_bp.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    user_id = session["user_id"]

    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.close()
        db.close()
        session.clear()
        return redirect(url_for("login.login"))

    address = None
    if user.get("address_id"):
        cursor.execute("SELECT * FROM addresses WHERE address_id = %s", (user["address_id"],))
        address = cursor.fetchone()

    cursor.close()
    db.close()

    if session.get("isAdmin"):
        return render_template("admin-profile.html", user=user, address=address)
    else:
        return render_template("profile.html", user=user, address=address)

@profile_bp.route("/edit", methods=['GET'])
def edit():
    """Display the edit profile form"""
    if "user_id" not in session:
        return redirect(url_for("login.login"))

    user_id = session["user_id"]
    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

    address = None
    if user and user.get("address_id"):
        cursor.execute("SELECT * FROM addresses WHERE address_id = %s", (user["address_id"],))
        address = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("profile-edit.html", user=user, address=address)

@profile_bp.route("/update", methods=['POST'])
def update():
    """Handle profile updates via AJAX"""
    if "user_id" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    user_id = session["user_id"]
    data = request.get_json()
    
    db = current_app.get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        address_id = user.get("address_id")
        
        if any(key in data for key in ['street_number', 'street_name', 'city', 'state', 'zip_code']):
            if address_id:
                cursor.execute("SELECT * FROM addresses WHERE address_id = %s", (address_id,))
                current_address = cursor.fetchone()
                
                street_number = data.get('street_number') or current_address['street_number']
                street_name = data.get('street_name') or current_address['street_name']
                city = data.get('city') or current_address['city']
                state = data.get('state') or current_address['state_abrev']
                zip_code = data.get('zip_code') or current_address['zip_code']
                
                cursor.execute("""
                    UPDATE addresses 
                    SET street_number = %s, street_name = %s, city = %s, state_abrev = %s, zip_code = %s
                    WHERE address_id = %s
                """, (
                    street_number,
                    street_name, 
                    city,
                    state,
                    zip_code,
                    address_id
                ))
            else:
                street_number = data.get('street_number') or ''
                street_name = data.get('street_name') or ''
                city = data.get('city') or ''
                state = data.get('state') or ''
                zip_code = data.get('zip_code') or ''
                
                if any([street_number, street_name, city, state, zip_code]):
                    cursor.execute("""
                        INSERT INTO addresses (street_number, street_name, city, state_abrev, zip_code)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        street_number,
                        street_name,
                        city,
                        state,
                        zip_code
                    ))
                    address_id = cursor.lastrowid
                    
                    cursor.execute("""
                        UPDATE users SET address_id = %s WHERE user_id = %s
                    """, (address_id, user_id))
        
        update_fields = []
        update_values = []
        
        if 'username' in data and data['username']:
            update_fields.append("username = %s")
            update_values.append(data['username'])
        
        if 'email' in data and data['email']:
            update_fields.append("email = %s")
            update_values.append(data['email'])
        
        if 'phone' in data and data['phone']:
            update_fields.append("phone_number = %s")
            update_values.append(data['phone'])
        
        if update_fields:
            update_values.append(user_id)
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE user_id = %s
            """, update_values)
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({"success": True, "redirect_url": url_for('profile.index')})
        
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/logout")
def logout():
    # Clear all session data
    session.clear()
    # Ensure session is saved
    session.modified = True
    return redirect(url_for("login.login"))