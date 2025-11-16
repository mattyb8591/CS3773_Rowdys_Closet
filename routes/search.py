from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import json

search_bp = Blueprint("search", __name__, template_folder="templates", static_folder="static")

def get_db_connection():
    # Import from app to avoid circular imports
    from app import get_db_connection as app_get_db_connection
    return app_get_db_connection()

@search_bp.route("/search", methods=["GET"])
def search_page():
    # Check if user is logged in first
    if "user_id" not in session:
        print("Search: No user_id in session, redirecting to login")
        return redirect(url_for("login.login"))
    
    # Get search query from URL parameters
    query = request.args.get('q', '').strip()
    
    # Don't perform search here - let JavaScript handle it dynamically
    return render_template("search.html", 
                         search_query=query)

@search_bp.route("/api/search", methods=["GET"])
def api_search():
    """API endpoint for search functionality"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"error": "No search query provided"}), 400
    
    products = perform_search(query)
    
    return jsonify({
        "query": query,
        "results": products,
        "count": len(products)
    })

def perform_search(search_query):
    """Perform the actual search in the database"""
    if not search_query:
        return []
    
    conn = get_db_connection()
    if not conn:
        print("Database connection failed")
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Search in product name OR description - make it case-insensitive
        search_wildcard = f"%{search_query}%"
        
        print(f"Searching for: {search_query}")
        print(f"Using wildcard: {search_wildcard}")
        
        cursor.execute("""
            SELECT product_id, name, price, original_price, stock, type, img_file_path, size, description, discount
            FROM products 
            WHERE name LIKE %s OR description LIKE %s
            ORDER BY product_id
        """, (search_wildcard, search_wildcard))
        
        all_products = cursor.fetchall()
        
        print(f"Found {len(all_products)} products before deduplication")
        
        # Use dictionary with product name as key to automatically handle duplicates
        # Same logic as home.py
        products_dict = {}
        
        for product in all_products:
            product_name = product['name']
            
            # If this product name is already in our dictionary, skip it
            if product_name in products_dict:
                continue
                
            products_dict[product_name] = {
                'product_id': product['product_id'],
                'name': product['name'],
                'price': product['price'],
                'original_price': product['original_price'],
                'type': product['type'],
                'img_file_path': product['img_file_path'],
                'description': product['description'],
                'stock': product['stock'],
                'discount': product['discount'] or 0  # Ensure discount is never None
            }
        
        unique_products_list = list(products_dict.values())
        
        # Process image paths
        for product in unique_products_list:
            if product['img_file_path'] and not product['img_file_path'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                product['img_file_path'] += '.png'
        
        print(f"Found {len(unique_products_list)} products after deduplication")
        
        return unique_products_list
        
    except Exception as e:
        print(f"Search error: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn:
            conn.close()