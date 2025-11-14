from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app, session, abort
import os
import uuid
from werkzeug.security import check_password_hash

item_bp = Blueprint("item", __name__, template_folder="templates", static_folder="static")

@item_bp.route("/<int:item_id>", methods=["GET", "POST"])
def index(item_id):
    #db connection

    db = current_app.get_db_connection()

    cursor = db.cursor(dictionary=True)
    #get data for selected item
    cursor.execute("SELECT * FROM products WHERE product_id = %s", (item_id,))
    item_data = cursor.fetchone()
    # Fetch size options for the item
    cursor.execute("SELECT product_id, size, stock FROM products WHERE name = %s AND type=%s", (item_data['name'],item_data['type']))
    size_selector_data = cursor.fetchall()
    select_size_list = []
    selectedProduct = None

    # Create a list of available sizes
    for dictionary in size_selector_data:
        if dictionary['stock'] > 0:
            select_size_list.append(dictionary['size'])
    # Handle POST request to add item to cart
    if request.method == "POST":
        selectedProduct = request.form.get('sizeDropdown')
        print("Selected Product ID:", selectedProduct)
        cursor.execute("SELECT product_id FROM products WHERE name = %s AND type = %s AND size = %s", (item_data['name'], item_data['type'], selectedProduct))
        
        selectedProductID= cursor.fetchone()
        selectedProductID= selectedProductID['product_id']  
        # Get customer ID and cart id from session user_id
        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
        customer = cursor.fetchone()
            
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
                
        customer_id = customer['customer_id']
            
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
            
        if not cart:
            return jsonify({"error": "Cart not found"}), 404
                
        cart_id = cart['cart_id']
        print("Cart ID:", cart_id)
        #put selected product into cart_products
        cursor.execute("INSERT INTO cart_products (cart_id, product_id) VALUES( %s, %s)", ( cart_id, selectedProductID))
        db.commit()


        print("Selected Product ID from DB:", selectedProductID)
    cursor.close()
    db.close()

    if not item_data:
        abort(404)

    # pass full product dict to template
    return render_template("item.html", item=item_data, options=select_size_list)
    
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
    