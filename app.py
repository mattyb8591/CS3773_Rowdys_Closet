
from flask import Flask, g, jsonify, session, Response, request
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
import mysql.connector
from mysql.connector import pooling
from mysql.connector import Error
import os
import json
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler
from flask_caching import Cache

from routes.signup import signup_bp
from routes.login import login_bp
from routes.home import home_bp
from routes.item import item_bp
from routes.cart import cart_bp
from routes.profile import profile_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=7)

# Initialize caching
cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes
})
cache.init_app(app)

# Connection pooling
connection_pool = None

def init_connection_pool():
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="app_pool",
            pool_size=10,
            pool_reset_session=True,
            host="20.120.180.6",
            user="rowdy",
            password="rowdyscloset",
            database="rowdys_closet_db",
            autocommit=True
        )
        print("Connection pool created successfully")
    except Error as e:
        print(f"Error creating connection pool: {e}")

def get_db_connection():
    global connection_pool
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if connection_pool is None:
                init_connection_pool()
            
            conn = connection_pool.get_connection()
            if conn and conn.is_connected():
                return conn
            else:
                retry_count += 1
                print(f"Failed to get connection, retry {retry_count}/{max_retries}")
                
        except Error as e:
            retry_count += 1
            print(f"Error getting connection (attempt {retry_count}/{max_retries}): {e}")
            if retry_count >= max_retries:
                print("Max retries reached, falling back to direct connection")
                # Fall back to direct connection
                try:
                    return mysql.connector.connect(
                        host="20.120.180.6",
                        user="rowdy",
                        password="rowdyscloset",
                        database="rowdys_closet_db",
                        autocommit=True
                    )
                except Error as fallback_error:
                    print(f"Fallback connection also failed: {fallback_error}")
                    return None
    
    return None

# Make get_db_connection available as an app method
app.get_db_connection = get_db_connection

class ServerSideSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.permanent = permanent
        self.modified = False

class FixedMySqlSessionInterface(SessionInterface):
    def __init__(self, app, db_conn_func, table_name='sessions'):
        self.app = app
        self.db_conn_func = db_conn_func
        self.table_name = table_name

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        
        if not sid:
            # Create new session
            sid = os.urandom(16).hex()
            return ServerSideSession(sid=sid, permanent=self.get_permanent_status(app))
        
        conn = self.db_conn_func()
        if not conn:
            app.logger.error("Database connection failed for session open")
            return ServerSideSession(sid=sid, permanent=self.get_permanent_status(app))

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT data, expiry, is_permanent FROM {self.table_name} WHERE sid = %s", 
                (sid,)
            )
            session_row = cursor.fetchone()

            if session_row:
                # Check if session is expired
                if session_row['expiry'] and session_row['expiry'] <= datetime.now():
                    cursor.execute(f"DELETE FROM {self.table_name} WHERE sid = %s", (sid,))
                    conn.commit()
                    return ServerSideSession(sid=sid, permanent=self.get_permanent_status(app))
                
                # Parse session data and handle legacy formats
                try:
                    data = json.loads(session_row['data'])
                    
                    # Fix legacy session formats
                    data = self._fix_legacy_session_data(data)
                    
                    session_obj = ServerSideSession(
                        data, 
                        sid=sid, 
                        permanent=session_row['is_permanent']
                    )
                    return session_obj
                except json.JSONDecodeError:
                    # Handle corrupted session data
                    app.logger.warning(f"Corrupted session data for SID: {sid}")
                    return ServerSideSession(sid=sid, permanent=self.get_permanent_status(app))
            
            # Session not found in database
            return ServerSideSession(sid=sid, permanent=self.get_permanent_status(app))
            
        except Exception as e:
            app.logger.error(f"Error opening session: {e}")
            return ServerSideSession(sid=sid, permanent=self.get_permanent_status(app))
        finally:
            cursor.close()
            conn.close()

    def _fix_legacy_session_data(self, data):
        """Fix legacy session data formats"""
        # Handle sessions with _user_id instead of user_id
        if '_user_id' in data and 'user_id' not in data:
            data['user_id'] = data.pop('_user_id')
        
        # Handle sessions with _username instead of username
        if '_username' in data and 'username' not in data:
            data['username'] = data.pop('_username')
        
        # Handle sessions with _email instead of email
        if '_email' in data and 'email' not in data:
            data['email'] = data.pop('_email')
        
        # Handle sessions with _isAdmin instead of isAdmin
        if '_isAdmin' in data and 'isAdmin' not in data:
            data['isAdmin'] = data.pop('_isAdmin')
        
        # Ensure _permanent flag is handled correctly
        if '_permanent' in data:
            # This should be handled by the session interface, not stored in data
            data.pop('_permanent', None)
        
        return data

    def get_permanent_status(self, app):
        """Determine if session should be permanent based on app settings"""
        return app.permanent_session_lifetime and app.permanent_session_lifetime.total_seconds() > 0

    def save_session(self, app, session, response):
        if not session:
            if session.modified:
                self._delete_session_from_db(session.sid)
                response.delete_cookie(app.session_cookie_name)
            return

        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)

        # Always set the cookie
        response.set_cookie(
            app.session_cookie_name,
            session.sid,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure
        )

        if not session.modified:
            return

        # Clean session data before saving
        session_data = dict(session)
        
        # Remove any Flask internal keys that shouldn't be stored
        session_data.pop('_permanent', None)
        
        conn = self.db_conn_func()
        if not conn:
            app.logger.error("Database connection failed for session save")
            return

        cursor = conn.cursor()
        try:
            session_data_json = json.dumps(session_data)
            
            if session.permanent:
                expiry = datetime.now() + app.permanent_session_lifetime
                is_permanent = True
            else:
                expiry = datetime.now() + timedelta(hours=1)
                is_permanent = False
            
            sql = f"""
                INSERT INTO {self.table_name} (sid, data, expiry, is_permanent)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    data = VALUES(data), 
                    expiry = VALUES(expiry), 
                    is_permanent = VALUES(is_permanent)
            """
            cursor.execute(sql, (session.sid, session_data_json, expiry, is_permanent))
            conn.commit()
        except Exception as e:
            app.logger.error(f"Error saving session to database: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def _delete_session_from_db(self, sid):
        conn = self.db_conn_func()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM {self.table_name} WHERE sid = %s", (sid,))
            conn.commit()
        except Exception as e:
            app.logger.error(f"Error deleting session from database: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

# Use the fixed session interface
app.session_interface = FixedMySqlSessionInterface(app, get_db_connection)

def cleanup_expired_sessions(app):
    """Optimized session cleanup that runs less frequently"""
    with app.app_context():
        conn = app.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Only clean up sessions expired more than 1 hour ago to avoid contention
                cursor.execute("DELETE FROM sessions WHERE expiry <= NOW() - INTERVAL 1 HOUR")
                conn.commit()
                app.logger.info(f"Cleaned up {cursor.rowcount} expired sessions.")
                
                # Also clear expired cache entries (they auto-expire but this helps memory)
                cache.clear()  # SimpleCache doesn't need manual cleanup, but other backends might
                
            except Exception as e:
                app.logger.error(f"Session cleanup failed: {e}")
            finally:
                cursor.close()
                conn.close()

# Initialize scheduler with optimized intervals
scheduler = APScheduler()
scheduler.init_app(app)

# Run cleanup less frequently - every 6 hours instead of every hour
scheduler.add_job(
    id='session_cleanup_job',
    func=cleanup_expired_sessions,
    args=[app],
    trigger='interval',
    hours=6  # Reduced frequency
)

scheduler.start()

# Register blueprints
app.register_blueprint(signup_bp, url_prefix="/signup")
app.register_blueprint(login_bp, url_prefix="/")
app.register_blueprint(home_bp, url_prefix="/home")
app.register_blueprint(item_bp, url_prefix="/item")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(profile_bp, url_prefix="/profile")
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.before_request
def debug_session_before():
    """Debug session state before each request"""
    if request.endpoint and 'debug' not in request.endpoint:
        print(f"=== BEFORE REQUEST: {request.method} {request.path} ===")
        print(f"Session ID: {session.sid if hasattr(session, 'sid') else 'unknown'}")
        print(f"Session data: {dict(session)}")
        print(f"User ID in session: {session.get('user_id')}")
        print(f"isAdmin in session: {session.get('isAdmin')}")

@app.after_request
def debug_session_after(response):
    """Debug session state after each request"""
    if request.endpoint and 'debug' not in request.endpoint:
        print(f"=== AFTER REQUEST: {request.method} {request.path} ===")
        print(f"Session modified: {session.modified if hasattr(session, 'modified') else 'N/A'}")
        print(f"Response status: {response.status_code}")
        print("=" * 50)
    return response

@app.teardown_appcontext
def close_db(error):
    # Connection pooling handles closing, but clean up any direct connections
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

@app.route("/test-session-perf")
def test_session_perf():
    """Test endpoint to verify session performance"""
    import time
    start_time = time.time()
    
    # Access session to trigger loading
    session['test_timestamp'] = datetime.now().isoformat()
    session.modified = True
    
    load_time = time.time() - start_time
    
    return jsonify({
        "session_id": session.sid if hasattr(session, 'sid') else 'unknown',
        "load_time_ms": round(load_time * 1000, 2),
        "session_data": dict(session)
    })

@app.route("/debug-session")
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        "session_id": session.sid if hasattr(session, 'sid') else 'unknown',
        "session_data": dict(session),
        "user_id": session.get('user_id'),
        "username": session.get('username'),
        "isAdmin": session.get('isAdmin'),
        "permanent": session.permanent if hasattr(session, 'permanent') else False
    })

@app.route("/debug-cookies")
def debug_cookies():
    """Debug endpoint to check cookies"""
    return jsonify({
        "cookies": dict(request.cookies),
        "session_cookie": request.cookies.get('session')
    })

if __name__ == "__main__":
    # Initialize connection pool on startup
    init_connection_pool()
    app.run(debug=True)
