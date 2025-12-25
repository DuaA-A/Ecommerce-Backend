from flask import Blueprint, request, jsonify
from services.order_service import (
    validate_order,
    create_order,
    get_order
)
order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@order_bp.route("/create", methods=["POST"])
def create():
    data = request.get_json()
    error = validate_order(data)
    if error:
        return jsonify({"status": "error", "message": error}), 400

    order_id = create_order(data)

    if isinstance(order_id, tuple):
        error, status_code = order_id
        return jsonify(error), status_code

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