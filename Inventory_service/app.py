# inventory_service/app.py
from flask import Flask, jsonify, request
from db import get_conn

app = Flask(__name__)

@app.get("/health")
def health():
    return {"service":"inventory","status":"running"}

@app.get("/api/inventory/check/<int:product_id>")
def check_stock(product_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT product_id, product_name, quantity_available, unit_price FROM inventory WHERE product_id = %s", (product_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error":"Product not found"}), 404
        return jsonify(row)
    finally:
        cursor.close()
        conn.close()

@app.put("/api/inventory/update")
def update_inventory():
    data = request.get_json()
    # expected {"product_id": int, "quantity_change": -2}
    pid = data.get("product_id")
    change = data.get("quantity_change", 0)
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE inventory SET quantity_available = quantity_available + %s WHERE product_id = %s", (change, pid))
        conn.commit()
        return jsonify({"updated": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
