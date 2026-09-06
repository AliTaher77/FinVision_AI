# FinVision AI — Real Functional Educational Prototype

FinVision AI is a functional educational prototype for financial-risk analysis. It fetches public market/FX data, computes technical indicators (SMA, RSI, volatility and momentum), reads Google News RSS headlines for simple sentiment scoring, and exposes the analysis through FastAPI.

## Endpoints
- `/` — interactive dashboard
- `/health` — service health
- `/risk-summary?asset=USD/YER` — live analysis
- `/risk-summary?asset=BTC/USD` — live market analysis
- `/risk-summary?asset=GOLD` — live gold futures analysis
- `/risk-summary?asset=AAPL` — live equity analysis

## Important
This is a real working prototype, but it is not a production financial-advisory system. Data comes from public web endpoints and can be delayed, unavailable, or rate-limited. Results are educational and not investment advice.
