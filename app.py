from flask import Flask
import mysql.connector
from mysql.connector import Error

from routes.signup import signup_bp
from routes.login import login_bp
from routes.home import home_bp
from routes.cart import cart_bp
from routes.item import item_bp
from routes.profile import profile_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev_secret_key" 

    app.register_blueprint(signup_bp, url_prefix="/signup")
    app.register_blueprint(login_bp, url_prefix="/")
    app.register_blueprint(home_bp, url_prefix="/home")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(item_bp, url_prefix="/item")
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

    # Attach it to the app (so blueprints can access it via current_app)
    app.get_db_connection = get_db_connection

    @app.route("/")
    def index():
        return "Testing"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
