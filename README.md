# 🚀 CryptoStream-MCP
### *A Python-based MCP Server for Real-Time & Historical Cryptocurrency Market Data*

---

# 📌 1. Overview

**CryptoStream-MCP** is a fully asynchronous **Model Context Protocol (MCP)** server built with **FastAPI**, designed to fetch, process, and stream cryptocurrency market data using the **CoinMarketCap Sandbox API**.

This project supports:

- Real-time crypto prices using **WebSockets**
- Historical + latest market data using **REST APIs**
- Modular, production-style architecture
- In-memory caching for performance
- Comprehensive test suite
- Clean separation of concerns (API / Core / WebSocket layers)

---

# 📌 2. Features

### 🟦 Core MCP Features

| Feature | Description |
|--------|-------------|
| Latest Listings | Latest crypto market listings |
| Quotes | Price + volume + market data |
| Historical Data | OHLCV-style historical pricing |
| Exchange Data | Exchange + market pair data |
| Global Metrics | Market cap, BTC dominance |
| Price Conversion | Crypto ↔ Fiat conversion |
| Real-Time Streaming | WebSocket live updates |
| Caching | Async TTL cache |
| Error Handling | Safe fallback on API errors |
| Testing | REST + WS + cache + mocks |

---

# 📌 3. Project Structure

crypto-mcp/
│
├── app/
│ ├── main.py # FastAPI entrypoint
│ ├── api/
│ │ ├── cryptocurrency.py # Crypto endpoints
│ │ ├── exchange.py # Exchange endpoints
│ │ ├── metrics.py # Global metrics
│ │ ├── tools.py # Conversion tools
│ │
│ ├── core/
│ │ ├── cmc_client.py # CMC API Wrapper
│ │ ├── cache.py # TTL Cache
│ │
│ ├── ws/
│ ├── realtime.py 
│
├── tests/
│ ├── test_app.py # Test suite
│
├── .env # API key
├── requirements.txt
└── README.md


---

# 📌 4. Architecture

## 🟦 A. REST API Layer
Each route performs:

1. Input validation  
2. Calls to `cmc_client`  
3. Caching via `TTLCache`  
4. Error-safe JSON responses  

---

## 🟦 B. CMC Client (Async HTTP Wrapper)
Located in:

app/core/cmc_client.py

Responsibilities:

- Async interaction with CoinMarketCap Sandbox  
- Request signing + headers  
- Endpoint path building  
- Error handling for upstream failures  

Supported patterns:

- `/cryptocurrency/*`
- `/exchange/*`
- `/global-metrics/*`
- `/tools/*`

---

## 🟦 C. Cache Layer (Async TTL Cache)

app/core/cache.py

Provides:

- Async `get()` and `set()`  
- Auto-expiring TTL entries  
- Useful for rate-limited API calls  

---

## 🟦 D. Real-Time WebSocket Engine

### WebSocket Route

ws://localhost:8000/ws/price/{symbol}?convert=USD
### How It Works

1. Client connects → server accepts  
2. Client added to subscription pool  
3. Background `broadcaster_loop()` polls CMC every few seconds  
4. All subscribed sockets receive fresh prices  
5. Client must send `"ping"` or any text to keep connection alive

## Rest API Endpoints

| Method | Endpoint                 | Description            |
| ------ | ------------------------ | ---------------------- |
| GET    | `/api/crypto/listings`   | Latest crypto listings |
| GET    | `/api/crypto/quote`      | Quote by symbol or ID  |
| GET    | `/api/crypto/historical` | Historical OHLCV       |
| GET    | `/api/crypto/info`       | Metadata               |

## Installation 
pip install -r requirements.txt
SANDBOX_COIN_BASE_API_KEY=your_sandbox_key_here
uvicorn app.main:app --reload
