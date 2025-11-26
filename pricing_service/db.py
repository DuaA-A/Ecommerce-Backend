# db.py
from dotenv import load_dotenv
load_dotenv()

import os
from mysql.connector import pooling
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME")
}

cnxpool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=3,
    **DB_CONFIG
)

def get_conn():
    return cnxpool.get_connection()

