# AdiTradeX Milestone 5 - Quant Technical Engine

This release adds the AlphaStrike V5.0 Quant Technical Engine.

## Adds

- Historical candle fetch from Kite Connect
- Multi-timeframe support
- EMA 9 / 20 / 50 / 200
- RSI
- MACD
- ATR
- Bollinger Bands
- VWAP approximation
- Market structure detection
- Trend score
- Momentum score
- Volatility score
- Technical score
- Technical bias
- AI technical summary
- Technical dashboard
- JSON API

## URLs

- `/technical/`
- `/technical/?underlying=nifty&interval=15m`
- `/technical/?underlying=nifty&interval=5m`
- `/technical/?underlying=banknifty&interval=15m`
- `/technical/json/nifty?interval=15m`

## Supported intervals

- `1m`
- `3m`
- `5m`
- `15m`
- `30m`
- `60m`
- `day`

## Safety

Read-only mode. No orders are placed.
