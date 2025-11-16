# app/main.py

import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Routers
from .api import cryptocurrency, exchange, metrics, tools

# WebSocket realtime broadcaster
from .ws.realtime import subscribe, unsubscribe, broadcaster_loop

load_dotenv()

app = FastAPI(
    title="Crypto MCP Server (Sandbox)",
    description="A structured MCP server that wraps CoinMarketCap Sandbox API.",
    version="1.0.0",
)

# ---------------------------------------------------------
# CORS Setup (frontend can call this server from anywhere)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ---------------------------------------------------------
# Register Routers
# ---------------------------------------------------------
app.include_router(cryptocurrency.router)
app.include_router(exchange.router)
app.include_router(metrics.router)
app.include_router(tools.router)

# ---------------------------------------------------------
# Background Task (WebSocket broadcaster)
# ---------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    """
    Create and run the real-time broadcaster in background.
    """
    app.state.broadcaster_task = asyncio.create_task(broadcaster_loop())


@app.on_event("shutdown")
async def on_shutdown():
    """
    Stop background polling safely.
    """
    task = app.state.broadcaster_task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# ---------------------------------------------------------
# WebSocket Route — Real-Time Price Updates
# ---------------------------------------------------------
@app.websocket("/ws/price/{symbol}")
async def ws_price(websocket: WebSocket, symbol: str):
    """
    Simulated real-time price updates.
    Clients must send something occasionally to keep connection alive.
    """
    convert = websocket.query_params.get("convert", "USD")

    await websocket.accept()
    await subscribe(websocket, symbol, convert)

    try:
        while True:
            # Used to keep the connection open.
            # Client can send ping or any text.
            await websocket.receive_text()

    except WebSocketDisconnect:
        await unsubscribe(websocket)

    except Exception:
        await unsubscribe(websocket)
        try:
            await websocket.close()
        except:
            pass
