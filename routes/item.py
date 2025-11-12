from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app, session, abort
import os
import uuid
from werkzeug.security import check_password_hash

item_bp = Blueprint("item", __name__, template_folder="templates", static_folder="static")

@item_bp.route("/<int:item_id>", methods=["GET"])
def index(item_id):
    #db connection

    db = current_app.get_db_connection()

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (item_id,))
    item_data = cursor.fetchone()
    cursor.close()
    db.close()

    if not item_data:
        abort(404)

    # pass full product dict to template
    return render_template("item.html", item=item_data)
    
#!!!!!!!!THE CODE BELOW IS item.py BEFORE I (Roman) EDITED IT, JUST IN CASE!!!!!!!!
# from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app,session
# import os
# import uuid
# from werkzeug.security import check_password_hash

# item_bp = Blueprint("item", __name__, template_folder="templates", static_folder="static")

# @item_bp.route("/<int:item_id>", methods=["GET"])
# def index(item_id):
#     #db connection

#     db = current_app.get_db_connection()

#     cursor = db.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM products where product_id =%s", (item_id,))
#     item_data = cursor.fetchone()
#     #get data for selected item
#     print(item_data) 
#     if item_data is None:
#         return("Error item not found") # Debug log
#     else:
#         name = item_data['name']
#         price = item_data['price']
#         size = item_data['size']
#         type = item_data['type']
#         description = item_data['description']
#         img = item_data['img_file_path']
#         stock = item_data['stock']
    
#     if request.method == "GET":
#         return render_template("item.html", item_name=name, price=price,size=size, stock=stock)

#     if request.method == "POST":
#         quantity = request.method['quantity']
#         stock = stock - quantity
#         cursor.execute("UPDATE products SET stock = %s WHERE product_id = %s", (stock, item_id))
#         cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
#         customer_id = cursor.fetchone()
#         cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
#         cart_id = cursor.fetchone()
    
#         cursor.execute("INSERT INTO cart_products (cart_product_id, cart_id, product_id) VALUES(%s, %s, %s)", (int(uuid.uuid1),cart_id ,item_id))
#         db.commit()
#     cursor.close()
#     db.close()
#     return render_template("item.html", item_name=name, price=price,size=size, stock=stock, description=description,img_file=img)
    