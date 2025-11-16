# app/ws/realtime.py

import asyncio
from fastapi import WebSocket
from typing import Dict, Set, Tuple
from ..core import cmc_client
import os

# Poll interval for pushing realtime updates (in seconds)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

# Mapping: (symbol, convert) → Set of active WebSockets
SUBSCRIPTIONS: Dict[Tuple[str, str], Set[WebSocket]] = {}


async def subscribe(ws: WebSocket, symbol: str, convert: str = "USD"):
    """
    Register a WebSocket connection for a specific symbol + convert pair.
    """
    symbol = symbol.upper()
    convert = convert.upper()
    key = (symbol, convert)
    SUBSCRIPTIONS.setdefault(key, set()).add(ws)


async def unsubscribe(ws: WebSocket):
    """
    Remove a WebSocket connection from all subscriptions.
    """
    to_remove = []

    for key, sockets in SUBSCRIPTIONS.items():
        if ws in sockets:
            sockets.remove(ws)
        if not sockets:  # clean up empty group
            to_remove.append(key)

    for key in to_remove:
        del SUBSCRIPTIONS[key]


async def _fetch_and_push(symbol: str, convert: str, sockets: Set[WebSocket]):
    """
    Fetch latest price for symbol+convert and push it to all connected clients.
    Removes dead sockets quietly.
    """
    try:
        data = await cmc_client.quotes_latest(symbol=symbol, convert=convert)
    except Exception:
        # If CMC API fails temporarily, skip this round
        return

    dead_sockets = []

    for ws in list(sockets):
        try:
            await ws.send_json(data)
        except Exception:
            # Client disconnected or error — mark for removal
            dead_sockets.append(ws)

    # Remove dead clients
    for ws in dead_sockets:
        sockets.discard(ws)


async def broadcaster_loop():
    """
    Background loop running during server lifetime.
    Periodically polls CMC Sandbox and pushes updates.
    """
    while True:
        if not SUBSCRIPTIONS:
            # No active WS clients — sleep efficiently
            await asyncio.sleep(0.5)
            continue

        tasks = []

        for (symbol, convert), sockets in list(SUBSCRIPTIONS.items()):
            if sockets:
                tasks.append(_fetch_and_push(symbol, convert, sockets))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        await asyncio.sleep(POLL_INTERVAL)
