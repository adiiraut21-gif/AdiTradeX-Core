from flask import Flask
from config.settings import Settings
from config.logger import setup_logger
from database.db import init_db
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from market.routes import market_bp
from options.routes import options_bp
from analytics.routes import analytics_bp

logger = setup_logger()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Settings.FLASK_SECRET_KEY

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(market_bp, url_prefix="/market")
    app.register_blueprint(options_bp, url_prefix="/options")
    app.register_blueprint(analytics_bp, url_prefix="/analytics")

    @app.route("/health")
    def health():
        return {
            "app": "AdiTradeX Core",
            "version": "4.0-Institutional-Analytics",
            "status": "ok",
            "modules": ["auth", "dashboard", "market", "option_chain", "analytics"]
        }

    logger.info("AdiTradeX Core v4.0 Institutional Analytics Engine started")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
