from kiteconnect import KiteConnect
from config.settings import Settings

def get_kite_client(access_token=None):
    if not Settings.KITE_API_KEY:
        raise RuntimeError("KITE_API_KEY is missing")

    kite = KiteConnect(api_key=Settings.KITE_API_KEY)

    if access_token:
        kite.set_access_token(access_token)

    return kite
