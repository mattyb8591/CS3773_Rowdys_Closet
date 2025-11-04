from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,session
import os
import uuid
from werkzeug.security import check_password_hash

item_bp = Blueprint("item", __name__, template_folder="templates", static_folder="static")

@item_bp.route("/", methods=["GET"])
def index(item_id,cart_id):
    #db connection

    db = current_app.get_db_connection()

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products where product_id =%s", (item_id))
    item_data = cursor.fetchone()
    #get data for selected item
    for row in item_data:
        name = row['name']
        price = row['price']
        size = row['size']
        type = row['type']
        description = row['description']
        img = row['img_file_path']

        stock = row['stock']
    
    if request.method == "GET":
        return render_template("item.html", item_name=name, price=price,size=size, stock=stock)

    if request.method == "POST":
        quantity = request.method['quantity']
        if quantity >= stock:
            return 'not enough of stock'
        
        stock = stock - quantity
        cursor.execute("UPDATE products SET stock = %s WHERE product_id = %s", (stock, item_id))
    
        cursor.execute("INSERT INTO cart_products (cart_product_id, cart_id, product_id) VALUES(%s, %s, %s)", (int(uuid.uuid1),cart_id ,item_id))
        db.commit()
    cursor.close()
    db.close()
    return render_template("item.html", item_name=name, price=price,size=size, stock=stock, description=description,img_file=img)
    