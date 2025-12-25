from flask import jsonify
from app.database import get_db
import requests

INVENTORY_SERVICE_CHECK_URL = "http://127.0.0.1:5002/api/inventory/check"  # + pid
INVENTORY_SERVICE_UPDATE_URL = "http://127.0.0.1:5002/api/inventory/update"
PRICING_SERVICE_URL = "http://127.0.0.1:5003/api/pricing/calculate"


def validate_order(data):
    if "customer_id" not in data:
        return jsonify({"error": "customer_id is required"}), 400
    if "products" not in data or not data["products"]:
        return jsonify({"error": "products list is required"}), 400

    for p in data["products"]:
        if "product_id" not in p or "quantity" not in p:
            return jsonify({"error": "each product must have product_id and quantity"}), 400
        try:
            response = requests.get(
                f"{INVENTORY_SERVICE_CHECK_URL}/{p['product_id']}", timeout=5)
            response.raise_for_status()
            product = response.json()
        except requests.RequestException as e:
            error_data = response.json()
            error_msg = error_data.get("error", "Unknown error")
            return jsonify({"error": f"Failed to fetch product {p['product_id']} from Inventory Service: Product not found!"}), 500

        p_quantity = int(p["quantity"])

        if p_quantity > product["quantity_available"]:
            return jsonify({"error": f"The required quantity for product {p['product_id']} exceeds the stock availability"}), 400

    return None

def create_order(data):
    db = get_db()
    cursor = db.cursor()

    # fetching pricing service to get each product price and total price
    req_body = {
        "products": data["products"]
    }
    try:
        response = requests.post(
            f"{PRICING_SERVICE_URL}", json=req_body, timeout=5)
        response.raise_for_status()
        pricing_res = response.json()
    except requests.RequestException as e:
        error_data = response.json()
        error_msg = error_data.get("error", "Unknown error")
        return jsonify({"error": f"Failed to get products prices from Pricing Service: {error_msg}"}), 500

    items = pricing_res["items"]
    items_lookup = {item["product_id"]                    : item for item in items}  # restructure as map

    cursor.execute(
        "INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
        (data["customer_id"], pricing_res["total"])
    )
    order_id = cursor.lastrowid

    for p in data["products"]:

        pid = p["product_id"]
        target_item = items_lookup.get(pid)

        req_body = {
            "product_id": p["product_id"],
            "stock_change": -p["quantity"]
        }
        try:
            response = requests.put(
                f"{INVENTORY_SERVICE_UPDATE_URL}", json=req_body, timeout=5)
            response.raise_for_status()
            product = response.json()
        except requests.RequestException as e:
            error_data = response.json()
            error_msg = error_data.get("error", "Unknown error")
            return jsonify({"error": f"Failed to update products to Inventory Service: {error_msg}"}), 500

        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            (order_id, p["product_id"], p["quantity"],
             target_item["final_price"])
        )
    customer_id = data["customer_id"]
    db.commit()
    cursor.close()

    return order_id, customer_id


def get_order(order_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
    order = cursor.fetchone()

    if not order:
        cursor.close()
        return None

    cursor.execute(
        "SELECT product_id, quantity FROM order_items WHERE order_id=%s",
        (order_id,)
    )

    items = cursor.fetchall()
    cursor.close()

    return {
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "total_amount": float(order["total_amount"]),
        "created_at": str(order["created_at"]),
        "products": [
            {"product_id": item["product_id"], "quantity": item["quantity"]} for item in items
        ]
    }
