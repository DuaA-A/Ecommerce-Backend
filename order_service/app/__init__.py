from flask import Flask
from .config import Config
from .database import close_db
from routes.order_routes import order_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(order_bp)
    app.teardown_appcontext(close_db)

    return app
