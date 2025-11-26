# order_service/app.py
from flask import Flask, request, jsonify
from db import get_conn

app = Flask(__name__)

@app.get("/health")
def health():
    return {"service":"order","status":"running"}

@app.post("/api/orders/create")
def create_order():
    data = request.get_json()
    # Expected: {"customer_id": int, "products":[{"product_id":int,"quantity":int}], "total_amount": decimal}
    if not data:
        return jsonify({"error":"No JSON provided"}), 400
    customer_id = data.get("customer_id")
    products = data.get("products", [])
    total_amount = data.get("total_amount", 0)

    if customer_id is None or not products:
        return jsonify({"error":"Missing customer or products"}), 400

    conn = get_conn()
    cursor = conn.cursor()
    try:
        # 1) Insert order
        cursor.execute("INSERT INTO orders (customer_id, total_amount, status) VALUES (%s,%s,%s)",
                        (customer_id, total_amount, 'created'))
        order_id = cursor.lastrowid

        # 2) Insert items
        for p in products:
            cursor.execute("SELECT unit_price FROM inventory WHERE product_id = %s", (p['product_id'],))
            price_row = cursor.fetchone()
            unit_price = price_row[0] if price_row else 0
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)",
                            (order_id, p['product_id'], p['quantity'], unit_price))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error":str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"order_id": order_id, "status":"created"}), 201

@app.get("/api/orders/<int:order_id>")
def get_order(order_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({"error":"Order not found"}), 404
        cursor.execute("SELECT product_id, quantity, unit_price FROM order_items WHERE order_id = %s", (order_id,))
        items = cursor.fetchall()
        order['items'] = items
    finally:
        cursor.close()
        conn.close()
    return jsonify(order)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


