# AdiTradeX Milestone 1.5 - Core Architecture

This upgrade turns the simple auth server into a modular AdiTradeX Core foundation.

## What this version adds

- Modular folder structure
- SQLite-backed session storage
- Structured logging
- Centralized settings
- Dashboard page
- Cleaner Zerodha authentication flow
- Read-only mode

## Main URLs

- `/` - login page
- `/zerodha/callback` - Zerodha redirect callback
- `/health` - health check
- `/status` - connection status
- `/profile` - Kite profile test
- `/dashboard` - AdiTradeX dashboard
- `/logout` - clear saved session

## Render deployment

Upload all extracted files to GitHub and redeploy on Render.

Required environment variables:

- KITE_API_KEY
- KITE_API_SECRET
- FLASK_SECRET_KEY
- LOG_LEVEL

Redirect URL remains:

https://aditradex-auth.onrender.com/zerodha/callback

## Security

Do not commit `.env`, API secret, or access token.

## Next milestone

Milestone 2 will add live index quotes and the market data module.
