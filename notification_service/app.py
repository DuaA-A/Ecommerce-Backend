# app.py
from flask import Flask, request, jsonify
import requests
from db import log_notification

app = Flask(__name__)

# URLs of other services
CUSTOMER_SERVICE_URL = 'http://localhost:5004'
INVENTORY_SERVICE_URL = 'http://localhost:5002'  # Not strictly needed now, but kept for future

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    data = request.get_json()

    if not data or 'order_id' not in data:
        return jsonify({'error': 'order_id is required'}), 400

    order_id = data['order_id']
    customer_id = data.get('customer_id')  # Optional – can be fetched from Customer Service if not provided

    try:
        # Step 1: Get customer information
        if not customer_id:
            # If customer_id not provided, you could derive it from Order Service later
            return jsonify({'error': 'customer_id is required'}), 400

        cust_resp = requests.get(f"{CUSTOMER_SERVICE_URL}/api/customers/{customer_id}")
        cust_resp.raise_for_status()
        customer = cust_resp.json()

        customer_name = customer.get('name', 'Valued Customer')
        customer_email = customer.get('email', 'no-email@example.com')
        customer_phone = customer.get('phone', 'N/A')

        # Step 2: Generate delivery estimate (simulated – you can enhance with Inventory call)
        delivery_estimate = "3-5 business days"

        # Step 3: Build notification message
        message = f"""
Order Confirmation #{order_id}

Dear {customer_name},

Thank you for your order! We're processing it right now.

Estimated delivery: {delivery_estimate}

Contact Details:
Email: {customer_email}
Phone: {customer_phone}

We'll notify you when your order ships.

Thank you for shopping with us!
E-Commerce Team
        """.strip()

        # Step 4: Simulate sending email/SMS (console output)
        print("\n" + "="*50)
        print("SIMULATED NOTIFICATION SENT")
        print("="*50)
        print(f"To Email: {customer_email}")
        print(f"To Phone: {customer_phone}")
        print(f"Subject: Your Order #{order_id} is Confirmed!")
        print(f"Message:\n{message}")
        print("="*50 + "\n")

        # Step 5: Log to database
        success = log_notification(
            order_id=order_id,
            customer_id=customer_id,
            notification_type='email_sms',
            message=message
        )

        if not success:
            return jsonify({'error': 'Failed to log notification'}), 500

        return jsonify({
            'status': 'success',
            'message': 'Notification sent and logged successfully',
            'order_id': order_id,
            'customer_id': customer_id
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to contact Customer Service: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5005)