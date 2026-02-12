# Predicta Mini - Development Guide

## Project Overview
Crypto prediction market trading app built on Polymarket's CLOB API with gasless transactions via Polygon relayer.

## Architecture
- **Backend**: Python Flask (`backend/`) - API server integrating with Polymarket CLOB, Gamma API, and Relayer
- **Frontend**: Vanilla HTML/CSS/JS (`frontend/public/`) - Privy wallet, market browser, trading UI
- **Hosting**: Firebase Hosting (static) + Cloud Run (API)

## Key Technologies
- Polymarket py-clob-client for trading
- Polymarket py-builder-relayer-client for gasless transactions
- Privy for wallet connection
- Builder key: `019b99f0-0f93-7753-8dc3-d913cf44dcd4`

## Running Locally
```bash
cd backend && pip install -r requirements.txt && python app.py
```
Backend serves frontend static files at http://localhost:8080

## API Endpoints
- `GET /api/markets/` - List crypto markets with filters
- `GET /api/markets/search?q=` - Search markets
- `GET /api/markets/event/<id>` - Event detail
- `GET /api/markets/orderbook/<token_id>` - Orderbook
- `POST /api/trading/order/limit` - Place limit order
- `POST /api/trading/order/market` - Place market order
- `DELETE /api/trading/order/<id>` - Cancel order
- `POST /api/wallet/safe/deploy` - Deploy Safe wallet
- `POST /api/wallet/safe/approve` - Approve tokens

## Environment Variables
Copy `.env.example` to `.env` and fill in credentials.
