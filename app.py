from flask import Flask, g, jsonify, session, Response
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler

from routes.signup import signup_bp
from routes.login import login_bp
from routes.home import home_bp
from routes.item import item_bp
from routes.cart import cart_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.search import search_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=7)


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


class ServerSideSession(CallbackDict, SessionMixin):
    """A dictionary-like object representing the session data."""
    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True
        
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.permanent = permanent
        self.modified = False


class MySqlSessionInterface(SessionInterface):
    """Custom SessionInterface to store session data in MySQL."""
    def __init__(self, app, db_conn_func, table_name='sessions'):
        self.app = app
        self.db_conn_func = db_conn_func
        self.table_name = table_name

    def open_session(self, app, request):
        session_cookie_name = app.config.get('SESSION_COOKIE_NAME') or 'session'
        sid = request.cookies.get(session_cookie_name)
        
        if sid and len(sid) != 32: 
            app.logger.warning(f"Invalid SID length ({len(sid)}). Generating new SID.")
            sid = None 

        if not sid:
            sid = os.urandom(16).hex()
            return ServerSideSession(sid=sid, permanent=app.permanent_session_lifetime.total_seconds() > 0)
        
        conn = self.db_conn_func()
        if not conn:
            app.logger.error("Database connection failed for session open.")
            return ServerSideSession(sid=sid, permanent=app.permanent_session_lifetime.total_seconds() > 0)

        cursor = conn.cursor(dictionary=True)
        try:
            
            cursor.execute(
                f"SELECT data, expiry, is_permanent FROM {self.table_name} WHERE sid = %s", 
                (sid,)
            )
            session_row = cursor.fetchone()

            if session_row and session_row['expiry'] > datetime.now():
                data = json.loads(session_row['data'])
                return ServerSideSession(
                    data, 
                    sid=sid, 
                    permanent=session_row['is_permanent']
                )
            
            return ServerSideSession(sid=sid, permanent=app.permanent_session_lifetime.total_seconds() > 0)
            
        except Exception as e:
            app.logger.error(f"Error opening session: {e}")
            return ServerSideSession(sid=sid, permanent=app.permanent_session_lifetime.total_seconds() > 0)
        finally:
            cursor.close()
            conn.close()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)

        session_cookie_name = app.config.get('SESSION_COOKIE_NAME') or 'session'

        response.set_cookie(
            session_cookie_name,
            session.sid, 
            expires=expires, 
            httponly=httponly, 
            domain=domain, 
            path=path, 
            secure=secure
        )

        conn = self.db_conn_func()
        if not conn:
            app.logger.error("Database connection failed for session save.")
            return

        cursor = conn.cursor()
        try:
            if not session:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE sid = %s", (session.sid,))
                conn.commit()
                return

            if not session.modified:
                return 

            session_data = json.dumps(dict(session))
            
            if session.permanent:
                expiry = datetime.now() + app.permanent_session_lifetime
                is_permanent = True
            else:
                expiry = datetime.now() + timedelta(hours=1) 
                is_permanent = False
            
            sql = f"""
                INSERT INTO {self.table_name} (sid, data, expiry, is_permanent)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE data = VALUES(data), expiry = VALUES(expiry), is_permanent = VALUES(is_permanent)
            """
            cursor.execute(sql, (session.sid, session_data, expiry, is_permanent))
            conn.commit()
        except Exception as e:
            app.logger.error(f"Error saving session: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

app.session_interface = MySqlSessionInterface(app, get_db_connection)

def cleanup_expired_sessions(app):
    """Runs the cleanup query using the app context."""
    with app.app_context():
        conn = app.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE expiry <= NOW()")
                conn.commit()
                app.logger.info(f"Cleaned up {cursor.rowcount} expired sessions.")
            except Exception as e:
                app.logger.error(f"Session cleanup failed: {e}")
            finally:
                cursor.close()
                conn.close()

scheduler = APScheduler()
scheduler.init_app(app)

scheduler.add_job(
    id='session_cleanup_job',
    func=cleanup_expired_sessions,
    args=[app],
    trigger='interval',
    hours=1 
)

scheduler.start()


app.register_blueprint(signup_bp, url_prefix="/signup")
app.register_blueprint(login_bp, url_prefix="/")
app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(item_bp, url_prefix="/item")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(search_bp, url_prefix="/search") 


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db_connection'):
        g.db_connection.close()


@app.route("/")
def index():
    return "Welcome to Rowdy's Closet!"

@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()
            
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

@app.route("/test-products")
def test_products():
    try:
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SHOW TABLES LIKE 'products'")
            table_exists = cursor.fetchone()
            
            products = []
            if table_exists:
                cursor.execute("SELECT * FROM products")
                products = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return jsonify({
                "status": "success",
                "table_exists": bool(table_exists),
                "products": products,
                "product_count": len(products)
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