# db.py
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',        # change if needed
    'password': 'tas123//*999',
    'database': 'ecommerce_system'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def log_notification(order_id, customer_id, notification_type, message):
    """
    Insert a notification record into notification_log table
    Returns True on success, False on failure
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notification_log 
            (order_id, customer_id, notification_type, message)
            VALUES (%s, %s, %s, %s)
        """, (order_id, customer_id, notification_type, message))
        
        conn.commit()
        return True
    
    except Error as e:
        print(f"Error logging notification: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()