from flask import Flask
from config.settings import Settings
from config.logger import setup_logger
from database.db import init_db
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from market.routes import market_bp

logger = setup_logger()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Settings.FLASK_SECRET_KEY

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(market_bp, url_prefix="/market")

    @app.route("/health")
    def health():
        return {
            "app": "AdiTradeX Core",
            "version": "2.0-AdiStrike-v5-UI",
            "status": "ok",
            "modules": ["auth", "dashboard", "market"]
        }

    logger.info("AdiTradeX Core v2.0 AdiStrike v5 UI started")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
