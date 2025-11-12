from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,url_for, session
import os
from werkzeug.security import check_password_hash

admin_bp = Blueprint("admin", __name__, template_folder="templates", static_folder="static")

@admin_bp.before_request
def require_admin():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))
        
    if not session["isAdmin"]:
        return redirect(url_for('home.index'))

@admin_bp.route("/")
def index():
    return render_template("admin.html")
    
@admin_bp.route("/dashboard")
def dashboard(): 
    db = current_app.get_db_connection()

    stats = {
        'total_orders': 0,
        'total_users': 0,
        'total_products': 0
    }

    if db:
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) FROM orders")
        stats['total_orders'] = cursor.fetchone()['COUNT(*)']

        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()['COUNT(*)']

        cursor.execute("SELECT COUNT(*) FROM products")
        stats['total_products'] = cursor.fetchone()['COUNT(*)']
            
        cursor.close()
        db.close()
    
    return render_template("admin-dashboard.html", stats=stats, username=session['username'])

@admin_bp.route("/users")
def user_list():
    return render_template("admin.html")

@admin_bp.route("/users/<int:user_id>/edit", methods=['GET', 'POST'])
def edit_user(user_id):
    return render_template("admin.html")

@admin_bp.route("/products")
def product_list():
    return render_template("admin.html")

@admin_bp.route("/products/<int:product_id>/edit", methods=['GET', 'POST'])
def edit_product():
    return render_template("admin.html")

@admin_bp.route("/products/new", methods=['GET', 'POST'])
def new_product():
    return render_template("admin.html")

@admin_bp.route("/discounts")
def discount_list():
    return render_template("admin.html")

@admin_bp.route("/discounts/new", methods=['GET', 'POST'])
def new_discount():
    return render_template("admin.html")

@admin_bp.route("/orders")
def order_list():
    return render_template("admin.html")

@admin_bp.route("/orders/<int:order_id>")
def order_detail(order_id):
    return render_template("admin.html")