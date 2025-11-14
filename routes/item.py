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
    print("Item Data:", item_data)
    if not item_data:
        cursor.close()
        db.close()
        abort(404)

    # Fetch size options for the item
    cursor.execute("SELECT product_id, size, stock, img_file_path as image FROM products WHERE name = %s AND type=%s", (item_data['name'], item_data['type']))
    size_selector_data = cursor.fetchall()
    select_size_list = []
    selectedProduct = None

    # Create a list of available sizes
    for dictionary in size_selector_data:
        if dictionary['stock'] > 0:
            # Handle NULL size (one size products)
            size_display = dictionary['size'] if dictionary['size'] is not None else "One Size"
            select_size_list.append(size_display)
    
    # Handle POST request to add item to cart
    if request.method == "POST":
        selectedProduct = request.form.get('sizeDropdown')
        print("Selected Product Size:", selectedProduct)
        
        if not selectedProduct:
            cursor.close()
            db.close()
            return jsonify({"error": "No size selected"}), 400
        
        # Handle "One Size" selection - convert back to NULL for database query
        db_size_value = None if selectedProduct == "One Size" else selectedProduct
        
        cursor.execute("SELECT product_id FROM products WHERE name = %s AND type = %s AND ((%s IS NULL AND size IS NULL) OR size = %s)", 
                      (item_data['name'], item_data['type'], db_size_value, db_size_value))
        
        selectedProductID_result = cursor.fetchone()
        
        if not selectedProductID_result:
            cursor.close()
            db.close()
            return jsonify({"error": "Selected product not found"}), 404
            
        selectedProductID = selectedProductID_result['product_id']  
        print("Selected Product ID:", selectedProductID)
        
        # Get customer ID and cart id from session user_id
        if 'user_id' not in session:
            cursor.close()
            db.close()
            return jsonify({"error": "User not logged in"}), 401
            
        cursor.execute("SELECT customer_id FROM customers WHERE user_id = %s", (session['user_id'],))
        customer = cursor.fetchone()
            
        if not customer:
            cursor.close()
            db.close()
            return jsonify({"error": "Customer not found"}), 404
                
        customer_id = customer['customer_id']
            
        cursor.execute("SELECT cart_id FROM carts WHERE customer_id = %s", (customer_id,))
        cart = cursor.fetchone()
            
        if not cart:
            cursor.close()
            db.close()
            return jsonify({"error": "Cart not found"}), 404
                
        cart_id = cart['cart_id']
        print("Cart ID:", cart_id)
        
        #put selected product into cart_products
        cursor.execute("INSERT INTO cart_products (cart_id, product_id) VALUES(%s, %s)", (cart_id, selectedProductID))
        db.commit()

        print("Selected Product ID from DB:", selectedProductID)
    
    cursor.close()
    db.close()
    print("item_data being sent to template:", item_data)

    # pass full product dict to template
    return render_template("item.html", item=item_data, options=select_size_list)