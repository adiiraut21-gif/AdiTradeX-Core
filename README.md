# AdiTradeX Milestone 3 - Option Chain Engine

This release adds the first read-only Option Chain Engine to the AdiStrike v5 institutional dashboard.

## Adds

- NIFTY option chain
- BANKNIFTY option chain
- FINNIFTY option chain
- MIDCPNIFTY option chain
- Nearest expiry detection
- ATM detection
- CE/PE OI table
- PCR calculation
- Approximate Max Pain
- Option chain dashboard page
- JSON endpoints

## URLs

- `/options/`
- `/options/?underlying=nifty`
- `/options/?underlying=banknifty`
- `/options/chain/nifty`
- `/options/chain/banknifty`
- `/options/reload-instruments`

## Notes

This is still read-only. No orders are placed.

Max Pain is an approximation based on available strike OI in the displayed range.
