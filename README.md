# AdiTradeX Milestone 6.1A-1 - Multi-Timeframe Data Layer

This is the first internal build of Milestone 6.1A.

## Adds

- `technical_pro` module
- Multi-timeframe candle fetching
- 1m, 3m, 5m, 15m, 30m, 60m, day support
- Synthetic 75m candles built from 15m data
- Candle normalization
- Timeframe summary
- Multi-timeframe dashboard
- JSON endpoints

## New URLs

- `/technical-pro/`
- `/technical-pro/?underlying=nifty`
- `/technical-pro/?underlying=banknifty`
- `/technical-pro/json/nifty`
- `/technical-pro/json/nifty?include_candles=true`
- `/technical-pro/candles/nifty/15m`
- `/technical-pro/candles/nifty/75m`

## Important

This is a data-layer milestone. It does not yet change Strategy Engine scoring.
6.1A-2 will add the advanced technical engines on top of this data layer.

## Safety

Read-only mode. No orders are placed.
