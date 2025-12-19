from flask import Blueprint, request, jsonify
from services.inventory_service import (
    get_all_products,
    validate,
    update_inventory,
    get_product
)
inventory_bp = Blueprint("inventory", __name__, url_prefix="/api/inventory")

#check(product)     return id,name,stock and price
@inventory_bp.route("/check/<int:product_id>",methods=["GET"])
def check(product_id):
    product = get_product(product_id) #pid,pname,quantity,price
    if not product:
        return jsonify({"status": "error", "message": "Product not found"}), 404
    return jsonify(product), 200

#update_stock(product)   update with new quantity,
@inventory_bp.route("/update",methods=["PUT"])
def update():  # will recieve pid,stockchange
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "message": "Missing request body"}), 400
    
    error = validate(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    try:
        product = update_inventory(data)
        
        return jsonify({
            "status": "success",
            "product_id": product["product_id"],
            "quantity_available": product["quantity_available"],
            "last_updated": product["last_updated"]
        }), 201
        
    except Exception as e:
        return jsonify({"status": "error", "message": "Database update failed"}), 500
    
@inventory_bp.route("/all", methods=["GET"])
def get_all():
    products = get_all_products()
    return jsonify(products), 200
