from flask import Blueprint, request, jsonify
from services.order_service import (
    validate_order,
    create_order,
    get_order
)
import requests
order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@order_bp.route("/create", methods=["POST"])
def create():
    data = request.get_json()
    error = validate_order(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    result = create_order(data)

    if isinstance(result[0], tuple):
        error, status_code = result[0]
        return jsonify(error), status_code

    order_id, customer_id = result

    req_body = {
        "order_id": order_id,
        "customer_id": customer_id
    }
    response = requests.post(
        "http://127.0.0.1:5005/api/notifications/send", json=req_body, timeout=5)
    response.raise_for_status()

    return jsonify({
        "status": "success",
        "order_id": order_id
    }), 201


@order_bp.route("/<int:order_id>", methods=["GET"])
def get(order_id):
    order = get_order(order_id)
    if not order:
        return jsonify({"status": "error", "message": "Order not found"}), 404
    return jsonify(order), 200
