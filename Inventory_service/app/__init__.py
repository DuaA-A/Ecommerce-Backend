from flask import Flask
from .config import Config
from .database import close_db
from routes.inventory_routes import inventory_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(inventory_bp)
    app.teardown_appcontext(close_db)

    return app
