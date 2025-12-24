import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("DB_HOST")
    MYSQL_PORT = int(os.getenv("DB_PORT"))
    MYSQL_USER = os.getenv("DB_USER")
    MYSQL_PASSWORD = os.getenv("DB_PASSWORD")
    MYSQL_DB = os.getenv("DB_NAME")
    ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL")
