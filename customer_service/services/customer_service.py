from app.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

def create_customer(name, email, phone, password):
    db = get_db()
    cursor = db.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute(
            """
            INSERT INTO customers (name, email, phone, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (name, email, phone, hashed_password)
        )
        db.commit()
        return {
            "customer_id": cursor.lastrowid,
            "name": name,
            "email": email,
            "phone": phone,
            "loyalty_points": 0
        }
    finally:
        cursor.close()

def login_customer(email, password):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT * FROM customers WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()
        if user and check_password_hash(user["password_hash"], password):
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

def get_customer(customer_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            SELECT customer_id, name, email, phone, loyalty_points, created_at
            FROM customers
            WHERE customer_id=%s
            """,
            (customer_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()

def update_loyalty(customer_id, points):
    db = get_db()
    cursor = db.cursor()
    # print("points before: ",points)
    try:
        cursor.execute("SELECT loyalty_points from customers WHERE customer_id =%s ",(customer_id,))
        lp = cursor.fetchone()
        current_lp = lp["loyalty_points"]
        cursor.execute(
            "UPDATE customers SET loyalty_points = loyalty_points + %s WHERE customer_id=%s",
            (points,customer_id)
        )
        db.commit()
        result = cursor.rowcount
        final_points = int(points)+current_lp
        # print( "the result is:",result)
        return {
            "updated":result > 0,
            "points":final_points
        }
    finally:
        cursor.close()

def get_all_customers():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT customer_id, name, email, phone, loyalty_points, created_at FROM customers"
        )
        return cursor.fetchall()
    finally:
        cursor.close()

def customer_orders(customer_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT order_id FROM orders WHERE customer_id =%s",(customer_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()