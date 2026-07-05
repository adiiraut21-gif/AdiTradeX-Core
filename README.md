# AdiTradeX 6.1A-5 Institutional VWAP Futures Update

## Why

NIFTY, BANKNIFTY and FINNIFTY are indices and do not have real traded volume.
So true VWAP cannot be calculated from spot index candles.

## Fix

VWAP is now calculated using current-month futures volume:

- NIFTY -> NIFTY current month futures
- BANKNIFTY -> BANKNIFTY current month futures
- FINNIFTY -> FINNIFTY current month futures
- MIDCPNIFTY -> MIDCPNIFTY current month futures

## Files

Upload/replace:

- technical_pro/futures_resolver.py
- technical_pro/vwap_engine.py
- technical_pro/service.py

## Then

Render -> Manual Deploy -> Clear build cache & deploy

## Test

- /technical-pro/
- /technical-pro/vwap/nifty
- /technical-pro/snapshot/nifty

## Notes

If futures contract resolution fails, check that Kite access token is active and NFO instruments are accessible.
