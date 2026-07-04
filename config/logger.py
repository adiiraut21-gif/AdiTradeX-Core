import logging
from config.settings import Settings

def setup_logger():
    logger = logging.getLogger("aditradex")
    logger.setLevel(getattr(logging, Settings.LOG_LEVEL.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
