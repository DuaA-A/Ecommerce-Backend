from flask import Flask
from app.config import Config
from app.database import close_db
from routes.customer_routes import customer_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(customer_bp)
    app.teardown_appcontext(close_db)

    @app.get("/health")
    def health():
        return {"service": "customer", "status": "running"}

    return app
