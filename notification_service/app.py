# notification_service/app.py
from flask import Flask, request, jsonify
import requests
from db import get_conn

app = Flask(__name__)

@app.get("/health")
def health():
    return {"service":"notification","status":"running"}

@app.post("/api/notifications/send")
def send_notification():
    data = request.get_json()
    order_id = data.get("order_id")
    if not order_id:
        return jsonify({"error":"order_id required"}), 400

    # 1) Get order details from Order Service
    r = requests.get(f"http://localhost:5001/api/orders/{order_id}")
    if r.status_code != 200:
        return jsonify({"error":"Order not found"}), 404
    order = r.json()
    customer_id = order.get("customer_id")

    # 2) Get customer info
    r2 = requests.get(f"http://localhost:5004/api/customers/{customer_id}")
    if r2.status_code != 200:
        return jsonify({"error":"Customer not found"}), 404
    customer = r2.json()
    customer_email = customer.get("email")

    # 3) Check inventory status (for each item)
    messages = []
    for item in order.get("items", []):
        pid = item['product_id']
        r3 = requests.get(f"http://localhost:5002/api/inventory/check/{pid}")
        if r3.status_code == 200:
            prod = r3.json()
            messages.append(f"{prod['product_name']} is available: {prod['quantity_available']} left")
        else:
            messages.append(f"Product {pid} info not available")

    notification_message = f"Order #{order_id} confirmed. Details: " + " | ".join(messages)

    # Log to DB
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO notification_log (order_id, customer_id, notification_type, message) VALUES (%s,%s,%s,%s)",
                        (order_id, customer_id, 'order_confirmation', notification_message))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    # Simulate send
    print(f"EMAIL SENT TO: {customer_email}")
    print(f"Subject: Order #{order_id} Confirmed")
    print(f"Body: {notification_message}")

    return jsonify({"sent": True})
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
