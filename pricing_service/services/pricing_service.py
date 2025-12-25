from decimal import Decimal
import requests
from app.config import Config

def calculate_price_logic(products, cursor):
    subtotal = Decimal("0.0")
    itemized = []

    # Get tax rate
    cursor.execute("SELECT tax_rate FROM tax_rates WHERE region='default'")
    tax_row = cursor.fetchone()
    tax_rate = Decimal(str(tax_row["tax_rate"])) / Decimal("100") if tax_row else Decimal("0.15")

    for item in products:
        if "product_id" not in item or "quantity" not in item:
            raise ValueError("Each product must have 'product_id' and 'quantity'")

        product_id = item["product_id"]
        quantity = Decimal(str(item["quantity"]))
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Fetch product from inventory
        try:
            response = requests.get(f"{Config.INVENTORY_SERVICE_URL}/check/{product_id}", timeout=5)
            response.raise_for_status()
            product_data = response.json()
            if not product_data or "unit_price" not in product_data:
                raise ValueError(f"Product {product_id} missing 'unit_price'")
        except requests.RequestException as e:
            error_data = e.response.json() if e.response else {}
            error_msg = error_data.get("error", str(e))
            raise Exception(f"Failed to fetch product {product_id} from Inventory Service: {error_msg}")

        unit_price = Decimal(str(product_data["unit_price"]))
        base_price = unit_price * quantity

        # Check pricing rules
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

    return {
        "items": itemized,
        "subtotal": float(subtotal),
        "tax": float(tax),
        "total": float(total)
    }
