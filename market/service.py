from auth.kite_client import get_kite_client
from auth.session_store import get_latest_session
from database.db import get_connection, log_event
from market.symbols import DEFAULT_INDEX_LIST, INDEX_SYMBOLS

def require_session():
    session = get_latest_session()
    if not session:
        raise RuntimeError("Not logged in. Open / and login with Zerodha first.")
    return session

def fetch_quotes(symbols=None):
    session = require_session()
    kite = get_kite_client(session["access_token"])
    return kite.quote(symbols or DEFAULT_INDEX_LIST)

def normalize_quote(symbol, quote):
    ohlc = quote.get("ohlc", {}) or {}
    last_price = quote.get("last_price")
    close = ohlc.get("close")
    change = None
    change_pct = None

    if last_price is not None and close:
        change = round(last_price - close, 2)
        change_pct = round((change / close) * 100, 2)

    return {
        "symbol": symbol,
        "last_price": last_price,
        "open": ohlc.get("open"),
        "high": ohlc.get("high"),
        "low": ohlc.get("low"),
        "close": close,
        "net_change": quote.get("net_change", change),
        "change_pct": change_pct,
        "volume": quote.get("volume"),
        "oi": quote.get("oi"),
        "timestamp": str(quote.get("timestamp")) if quote.get("timestamp") else None
    }

def get_index_quotes():
    raw = fetch_quotes(DEFAULT_INDEX_LIST)
    return {symbol: normalize_quote(symbol, quote) for symbol, quote in raw.items()}

def save_market_snapshot(quotes):
    conn = get_connection()
    cur = conn.cursor()

    for symbol, q in quotes.items():
        cur.execute('''
            INSERT INTO market_snapshots (
                symbol, last_price, open_price, high_price, low_price,
                close_price, net_change, volume, oi
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            symbol,
            q.get("last_price"),
            q.get("open"),
            q.get("high"),
            q.get("low"),
            q.get("close"),
            q.get("net_change"),
            q.get("volume"),
            q.get("oi"),
        ))

    conn.commit()
    conn.close()
    log_event("MARKET", f"Market snapshot saved for {len(quotes)} symbols")

def latest_snapshots(limit=25):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT symbol, last_price, open_price, high_price, low_price,
               close_price, net_change, volume, oi, created_at
        FROM market_snapshots
        ORDER BY id DESC
        LIMIT ?
    ''', (limit,))
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "symbol": r[0],
            "last_price": r[1],
            "open": r[2],
            "high": r[3],
            "low": r[4],
            "close": r[5],
            "net_change": r[6],
            "volume": r[7],
            "oi": r[8],
            "created_at": r[9],
        }
        for r in rows
    ]

def resolve_symbol(name):
    return INDEX_SYMBOLS.get(name.lower().strip(), name)

def safe_index_quotes():
    try:
        quotes = get_index_quotes()
        save_market_snapshot(quotes)
        return list(quotes.values()), None
    except Exception as e:
        return [], str(e)
