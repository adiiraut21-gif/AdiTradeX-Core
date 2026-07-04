from flask import Flask
from config.settings import Settings
from config.logger import setup_logger
from database.db import init_db
from auth.routes import auth_bp
from dashboard.routes import dashboard_bp

logger = setup_logger()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Settings.FLASK_SECRET_KEY

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/health")
    def health():
        return {
            "app": "AdiTradeX Core",
            "version": "1.5",
            "status": "ok"
        }

    logger.info("AdiTradeX Core v1.5 started")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
