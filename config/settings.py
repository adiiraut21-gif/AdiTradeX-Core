import os

class Settings:
    APP_NAME = "AdiTradeX Core"
    VERSION = "4.0-Institutional-Analytics"

    KITE_API_KEY = os.getenv("KITE_API_KEY")
    KITE_API_SECRET = os.getenv("KITE_API_SECRET")

    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-secret")
    DATABASE_PATH = os.getenv("DATABASE_PATH", "aditradex.db")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
