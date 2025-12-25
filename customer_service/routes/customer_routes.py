from flask import Blueprint, request, jsonify
import requests
from services.customer_service import create_customer, login_customer, get_customer, update_loyalty, customer_orders

customer_bp = Blueprint("customers", __name__)

# Register new customer
@customer_bp.route("/api/customer/register", methods=["POST"])
def register_customer_route():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    if not all([name, email, password]):
        return jsonify({"error": "name, email, and password are required"}), 400
    try:
        customer = create_customer(name, email, phone, password)
        return jsonify(customer), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Login customer
@customer_bp.route("/api/customers/login", methods=["POST"])
def login_customer_route():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not all([email, password]):
        return jsonify({"error": "email and password required"}), 400
    customer = login_customer(email, password)
    if not customer:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify(customer), 200

# Get customer profile
@customer_bp.route("/api/customers/<int:customer_id>", methods=["GET"])
def get_customer_route(customer_id):
    customer = get_customer(customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer)

# Update loyalty points
@customer_bp.route("/api/customers/<int:customer_id>/loyalty", methods=["PUT"])
def update_loyalty_route(customer_id):
    data = request.get_json()
    points = data.get("points_to_add", 0)
    # print("loyality points :",points)
    updated = update_loyalty(customer_id, points)
    if not updated:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify({"updated": True})

@customer_bp.route("/api/customers/<int:customer_id>/orders", methods=["GET"])
def customer_orders_route(customer_id):
    orders = customer_orders(customer_id)
    if not orders:
        return jsonify({"order_ids": []}),200
    
    order_ids = [order["order_id"] for order in orders]
    return jsonify({
        "order_ids": order_ids
    })

@customer_bp.route("/test", methods=["GET"])
def test_route():
    return "Blueprint working!"
