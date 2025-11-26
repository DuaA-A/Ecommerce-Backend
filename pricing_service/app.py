from flask import Flask, request, jsonify
from db import get_conn    
import requests

app = Flask(__name__)

@app.get("/health")
def health():
    return {"service": "pricing", "status": "running"}

@app.post("/api/pricing/calculate")
def calculate():
    data = request.get_json()
    if not data or "products" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    products = data["products"]
    results = []
    total = 0.0

    for p in products:
        pid = p.get("product_id")
        qty = p.get("quantity", 1)
        # Example: call inventory service for price
        inv_resp = requests.get(f"http://localhost:5002/api/inventory/check/{pid}")
        if inv_resp.status_code != 200:
            return jsonify({"error": f"product {pid} not found"}), 404
        prod = inv_resp.json()
        unit_price = float(prod.get("unit_price", 0.0))
        subtotal = unit_price * qty

        # apply pricing rule from DB
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT discount_percentage FROM pricing_rules WHERE product_id = %s AND min_quantity <= %s ORDER BY discount_percentage DESC LIMIT 1",
                (pid, qty)
            )
            rule = cursor.fetchone()
            discount_pct = float(rule['discount_percentage']) if rule else 0.0
        finally:
            cursor.close()
            conn.close()

        discount_amount = subtotal * discount_pct / 100.0
        net = subtotal - discount_amount
        results.append({
            "product_id": pid,
            "quantity": qty,
            "unit_price": unit_price,
            "discount_pct": discount_pct,
            "total": round(net,2)
        })
        total += net

    return jsonify({"items": results, "total": round(total,2)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
