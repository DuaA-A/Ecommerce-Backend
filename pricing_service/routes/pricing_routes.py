from flask import Blueprint, request, jsonify
from services.pricing_service import calculate_price_logic
from app.database import get_db, close_db

pricing_bp = Blueprint("pricing", __name__, url_prefix="/api/pricing")

@pricing_bp.route("/calculate", methods=["POST"])
def calculate_price():
    data = request.get_json()
    if not data or "products" not in data:
        return jsonify({"error": "Missing 'products' in request"}), 400

    products = data["products"]
    if not isinstance(products, list) or len(products) == 0:
        return jsonify({"error": "'products' must be a non-empty list"}), 400

    db = get_db()
    try:
        cursor = db.cursor()
        result = calculate_price_logic(products, cursor)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        close_db()
