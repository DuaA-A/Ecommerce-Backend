from flask import Flask, request, jsonify
import mysql.connector
import requests
from decimal import Decimal

app = Flask(__name__)
db = mysql.connector.connect(
    host="localhost",
    user="ecommerce_user",
    password="1234",  # must match your DB
    database="ecommerce_system"
)
cursor = db.cursor(dictionary=True)

INVENTORY_SERVICE_URL = "http://127.0.0.1:5002/api/inventory/check"

@app.route("/api/pricing/calculate", methods=["POST"])
def calculate_price():
    try:
        data = request.get_json()
        if not data or "products" not in data:
            return jsonify({"error": "Missing 'products' in request"}), 400

        products = data["products"]
        if not isinstance(products, list) or len(products) == 0:
            return jsonify({"error": "'products' must be a non-empty list"}), 400

        subtotal = Decimal("0.0")
        itemized = []

        cursor.execute("SELECT tax_rate FROM tax_rates WHERE region='default'")
        tax_row = cursor.fetchone()
        tax_rate = Decimal(str(tax_row["tax_rate"])) / Decimal("100") if tax_row else Decimal("0.15")

        for item in products:
            if "product_id" not in item or "quantity" not in item:
                return jsonify({"error": "Each product must have 'product_id' and 'quantity'"}), 400

            product_id = item["product_id"]
            quantity = Decimal(str(item["quantity"]))
            if quantity <= 0:
                return jsonify({"error": "Quantity must be positive"}), 400

            try:
                response = requests.get(f"{INVENTORY_SERVICE_URL}/{product_id}", timeout=5)
                response.raise_for_status()
                product_data = response.json()
            except requests.RequestException as e:
                return jsonify({"error": f"Failed to fetch product {product_id} from Inventory Service: {str(e)}"}), 500

            unit_price = Decimal(str(product_data.get("unit_price", "0")))
            base_price = unit_price * quantity

            cursor.execute(
                """
                SELECT discount_percentage 
                FROM pricing_rules 
                WHERE product_id = %s AND min_quantity <= %s
                ORDER BY min_quantity DESC LIMIT 1
                """,
                (product_id, int(quantity))
            )
            rule = cursor.fetchone()
            discount = Decimal("0.0")
            if rule and rule["discount_percentage"] is not None:
                discount = base_price * (Decimal(str(rule["discount_percentage"])) / Decimal("100"))

            final_price = base_price - discount
            subtotal += final_price

            itemized.append({
                "product_id": product_id,
                "quantity": int(quantity),
                "unit_price": float(unit_price),
                "discount": float(discount),
                "final_price": float(final_price)
            })

        tax = subtotal * tax_rate
        total = subtotal + tax

        return jsonify({
            "items": itemized,
            "subtotal": float(subtotal),
            "tax": float(tax),
            "total": float(total)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5003, debug=True)
