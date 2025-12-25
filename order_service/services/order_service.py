from flask import jsonify
from app.database import get_db
import requests

INVENTORY_SERVICE_CHECK_URL = "http://127.0.0.1:5002/api/inventory/check"
INVENTORY_SERVICE_UPDATE_URL = "http://127.0.0.1:5002/api/inventory/update"
PRICING_SERVICE_URL = "http://127.0.0.1:5003/api/pricing/calculate"


# ---------------- VALIDATION ---------------- #
def validate_order(data):
    if not data:
        return "Request body is missing"

    if "customer_id" not in data:
        return "customer_id is required"

    if "products" not in data or not data["products"]:
        return "products list is required"

    for p in data["products"]:
        if "product_id" not in p or "quantity" not in p:
            return "each product must have product_id and quantity"

        try:
            res = requests.get(
                f"{INVENTORY_SERVICE_CHECK_URL}/{p['product_id']}",
                timeout=5
            )
            res.raise_for_status()
            product = res.json()
        except requests.exceptions.RequestException:
            return f"Inventory service unavailable for product {p['product_id']}"

        if int(p["quantity"]) > product["quantity_available"]:
            return f"Insufficient stock for product {p['product_id']}"

    return None


# ---------------- CREATE ORDER ---------------- #
def create_order(data):
    db = get_db()
    cursor = db.cursor()

    # ---- Call Pricing Service ----
    try:
        pricing_response = requests.post(
            PRICING_SERVICE_URL,
            json={"products": data["products"]},
            timeout=5
        )
        pricing_response.raise_for_status()
        pricing_data = pricing_response.json()

    except requests.exceptions.ConnectionError:
        return {"error": "Pricing service is not running"}, 503

    except requests.exceptions.Timeout:
        return {"error": "Pricing service timeout"}, 504

    except requests.exceptions.RequestException:
        return {"error": "Failed to contact pricing service"}, 500

    # ---- Insert Order ----
    cursor.execute(
        "INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
        (data["customer_id"], pricing_data["total"])
    )
    order_id = cursor.lastrowid

    items_map = {i["product_id"]: i for i in pricing_data["items"]}

    # ---- Process Items ----
    for p in data["products"]:
        pid = p["product_id"]
        qty = p["quantity"]

        # Update inventory
        try:
            inv_res = requests.post(
                INVENTORY_SERVICE_UPDATE_URL,
                json={
                    "product_id": pid,
                    "stock_change": -qty
                },
                timeout=5
            )
            inv_res.raise_for_status()
        except requests.exceptions.RequestException:
            return {"error": "Failed to update inventory"}, 500

        cursor.execute(
            """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            """,
            (
                order_id,
                pid,
                qty,
                items_map[pid]["final_price"]
            )
        )

    db.commit()
    cursor.close()

    return order_id


def get_order(order_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id=%s", (order_id,))
    order = cursor.fetchone()

    if not order:
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
        "products": items
    }
