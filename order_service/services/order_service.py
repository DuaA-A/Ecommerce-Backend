from flask import jsonify
from app.database import get_db

def validate_order(data):
    if "customer_id" not in data:
        return "customer_id is required"
    if "products" not in data or not data["products"]:
        return "products list is required"
    if "total_amount" not in data:
        return "total_amount is required"

    for p in data["products"]:
        if "product_id" not in p or "quantity" not in p:
            return "each product must have product_id and quantity"

    return None


def create_order(data):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
        (data["customer_id"], data["total_amount"])
    )

    order_id = cursor.lastrowid

    for product in data["products"]:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
            (order_id, product["product_id"], product["quantity"])
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
