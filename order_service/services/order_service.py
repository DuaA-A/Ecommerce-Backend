from flask import jsonify
from app.database import get_db
import requests

INVENTORY_SERVICE_CHECK_URL = "http://127.0.0.1:5002/api/inventory/check"  # + pid
INVENTORY_SERVICE_UPDATE_URL = "http://127.0.0.1:5002/api/inventory/update"
PRICING_SERVICE_URL = "http://127.0.0.1:5003/api/pricing/calculate"


def validate_order(data):
    for p in data["products"]:
        if "product_id" not in p or "quantity" not in p:
            return "each product must have product_id and quantity"

        try:
            response = requests.get(
                f"{INVENTORY_SERVICE_CHECK_URL}/{p['product_id']}",
                timeout=5
            )
            response.raise_for_status()
            product = response.json()

        except requests.exceptions.ConnectionError:
            return "Inventory Service is unavailable", 503

        except requests.exceptions.Timeout:
            return "Inventory Service timeout", 504

        except requests.exceptions.HTTPError:
            return f"Product {p['product_id']} not found in inventory", 404

        except requests.RequestException as e:
            return f"Inventory service error: {str(e)}", 500

        if int(p["quantity"]) > product["quantity"]:
            return f"Insufficient stock for product {p['product_id']}"
    if "customer_id" not in data:
        return "customer_id is required"
    if "products" not in data or not data["products"]:
        return "products list is required"

    for p in data["products"]:
        if "product_id" not in p or "quantity" not in p:
            return "each product must have product_id and quantity"
        try:
            response = requests.get(
                f"{INVENTORY_SERVICE_CHECK_URL}/{p['product_id']}", timeout=5)
            response.raise_for_status()
            product = response.json()
        except requests.RequestException as e:
            error_data = response.json()
            error_msg = error_data.get("error", "Unknown error")
            return {"error": f"Failed to fetch product {p['product_id']} from Inventory Service: Product not found!"}, 500

        p_quantity = int(p["quantity"])

        if p_quantity > product["quantity_available"]:
            return f"The required quantity for product {p['product_id']} exceeds the stock availability"

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
        return {"error": f"Failed to get products prices from Pricing Service: {error_msg}"}, 500

    items = pricing_res["items"]
    items_lookup = {item["product_id"]
        : item for item in items}  # restructure as map

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
            response = requests.post(
                f"{INVENTORY_SERVICE_UPDATE_URL}", json=req_body, timeout=5)
            response.raise_for_status()
            product = response.json()
        except requests.RequestException as e:
            error_data = response.json()
            error_msg = error_data.get("error", "Unknown error")
            return {"error": f"Failed to update products to Inventory Service: {error_msg}"}, 500

        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            (order_id, p["product_id"], p["quantity"],
             target_item["final_price"])
        )

    db.commit()
    cursor.close()

    return order_id


def get_order(order_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
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
        "order_id": order["id"],
        "customer_id": order["customer_id"],
        "total_amount": float(order["total_amount"]),
        "created_at": str(order["created_at"]),
        "products": [
            {"product_id": item["product_id"], "quantity": item["quantity"]} for item in items
        ]
    }
