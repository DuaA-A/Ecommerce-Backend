# customer_service/app.py
from flask import Flask, jsonify, request
import requests
from db import get_conn

app = Flask(__name__)

@app.get("/health")
def health():
    return {"service":"customer","status":"running"}

@app.get("/api/customers/<int:customer_id>")
def get_customer(customer_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        c = cursor.fetchone()
        if not c:
            return jsonify({"error":"Customer not found"}), 404
        return jsonify(c)
    finally:
        cursor.close()
        conn.close()

@app.get("/api/customers/<int:customer_id>/orders")
def get_order_history(customer_id):
    # Call Order Service to get orders for this customer (Order Service stores orders)
    # Assuming Order Service provides a /api/orders?customer_id=... endpoint (not implemented above)
    r = requests.get(f"http://localhost:5001/api/orders?customer_id={customer_id}")
    if r.status_code != 200:
        return jsonify({"error": "Failed to get order history"}), 500
    return jsonify(r.json())

@app.put("/api/customers/<int:customer_id>/loyalty")
def update_loyalty(customer_id):
    data = request.get_json()
    points = data.get("points",0)
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id = %s", (points, customer_id))
        conn.commit()
        return jsonify({"updated": True})
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
