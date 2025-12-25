from flask import Flask
from app.config import Config
from app.database import close_db
from routes.pricing_routes import pricing_bp

def create_app():
    app = Flask(__name__)  # <-- use __name__ instead of os.name
    app.config.from_object(Config)

    app.register_blueprint(pricing_bp)
    app.teardown_appcontext(close_db)

    @app.get("/health")
    def health():
        return {"service": "pricing", "status": "running"}

    return app
