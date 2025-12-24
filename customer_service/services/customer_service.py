from app.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def create_customer(name, email, phone, password):
    conn = get_db()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO customers (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, hashed_password)
        )
        conn.commit()
        return {
            "customer_id": cursor.lastrowid,
            "name": name,
            "email": email,
            "phone": phone,
            "loyalty_points": 0
        }
    finally:
        cursor.close()
        conn.close()

def login_customer(email, password):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers WHERE email=%s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user["password"], password):
            return {
                "customer_id": user["customer_id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone"],
                "loyalty_points": user["loyalty_points"]
            }
        return None
    finally:
        cursor.close()
        conn.close()

def get_customer(customer_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT customer_id, name, email, phone, loyalty_points, created_at FROM customers WHERE customer_id=%s", (customer_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def update_loyalty(customer_id, points):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id=%s", (points, customer_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()
