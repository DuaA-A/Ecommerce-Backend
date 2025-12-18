from flask import jsonify
from app.database import get_db
from datetime import datetime


def get_product(product_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT *"
                   " FROM inventory WHERE product_id=%s", (product_id,))
    product = cursor.fetchone()
    cursor.close()

    if not product:
        return None

    return {
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "quantity_available": product["quantity_available"],
        "unit_price": float(product["unit_price"]),
        "last_updated": product["last_updated"]
    }


def validate(data):
    # data formate: product_id , stock_change
    if "product_id" not in data:
        return "product_id is required!"
    if "stock_change" not in data:
        return "stock_change is required!"
    if int(data["stock_change"]) >= 0:
        return "The requested quantity must be below 0!"

    product = get_product(data["product_id"])
    if not product:
        return "product not available"

    if int(product["quantity_available"]) + int(data["stock_change"]) < 0:
        return "Quantity requested exceeds stock's ability"

    return None


def update_inventory(data):
    product_id = data["product_id"]
    stock_change = int(data["stock_change"])
    new_date = datetime.now()
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "UPDATE inventory "
        "SET quantity_available = quantity_available + %s, last_updated = %s "
        "WHERE product_id = %s",
        (stock_change, new_date, product_id)
    )
    db.commit()

    cursor.execute("SELECT product_id, quantity_available, last_updated "
                   "FROM inventory WHERE product_id=%s", (product_id,))
    new_product = cursor.fetchone()
    cursor.close()

    return {
        "product_id": new_product["product_id"],
        "quantity_available": int(new_product["quantity_available"]),
        "last_updated": str(new_product["last_updated"])
    }
