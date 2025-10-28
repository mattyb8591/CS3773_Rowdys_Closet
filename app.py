from flask import Flask, g, jsonify
import mysql.connector
from mysql.connector import Error

# Import all Blueprints
from routes.signup import signup_bp
from routes.login import login_bp
from routes.home import home_bp
from routes.item import item_bp
from routes.cart import cart_bp
from routes.profile import profile_bp

app = Flask(__name__)

app.register_blueprint(signup_bp, url_prefix="/signup")
app.register_blueprint(login_bp, url_prefix="/")
app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(item_bp, url_prefix="/item")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(profile_bp, url_prefix="/profile")


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="20.120.180.6",
            user="rowdy",
            password="rowdyscloset",
            database="rowdys_closet_db"
        )
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

app.get_db_connection = get_db_connection

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db_connection'):
        g.db_connection.close()

@app.route("/")
def index():
    return "Welcome to Rowdy’s Closet!"

# test the database conneciton
@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            
            # Check if users table exists (not accounts)
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()
            
            # Get all users from users table
            users = []
            if table_exists:
                cursor.execute("SELECT user_id, username, email FROM users")
                users = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "status": "success",
                "table_exists": bool(table_exists),
                "users": users,
                "user_count": len(users)
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Database connection failed"
            }), 500
            
    except Error as e:
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500
    
if __name__ == "__main__":
    app.run(debug=True)

    