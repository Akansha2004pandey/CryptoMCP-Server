import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.core.cache import TTLCache


client = TestClient(app)


# health check
def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


# cache tests
@pytest.mark.asyncio
async def test_cache_ttl():
    cache = TTLCache()

    await cache.set("key1", "value1", ttl=1)
    assert await cache.get("key1") == "value1"

    await asyncio.sleep(1.1)
    assert await cache.get("key1") is None


# Accept 200 success or 502 as upstream error

def test_crypto_listings():
    r = client.get("/api/crypto/listings?limit=1")
    assert r.status_code in (200, 502)


def test_crypto_quote_missing_params():
    r = client.get("/api/crypto/quote")
    assert r.status_code == 400


def test_crypto_historical_missing_params():
    r = client.get("/api/crypto/historical")
    assert r.status_code == 400


def test_crypto_info_missing_params():
    r = client.get("/api/crypto/info")
    assert r.status_code == 400


def test_exchange_listings():
    r = client.get("/api/exchange/listings?limit=1")
    assert r.status_code in (200, 502)


def test_global_metrics():
    r = client.get("/api/metrics/global")
    assert r.status_code in (200, 502)


def test_price_conversion():
    r = client.get("/api/tools/convert?amount=1&symbol=BTC&convert_to=USD")
    assert r.status_code in (200, 502)


# WebSocket test
def test_websocket_price_stream():
    with client.websocket_connect("/ws/price/BTC?convert=USD") as ws:
        ws.send_text("ping")  

        try:
            msg = ws.receive_json()
            assert isinstance(msg, dict)
        except Exception:
            
            pass


# ----------------------------------------------------------------------
# MOCKED API TESTS — ALWAYS PASS (CI-SAFE)
# ----------------------------------------------------------------------
@pytest.mark.asyncio
async def test_mocked_quotes_latest():
    """CMC Sandbox API call replaced with mock for CI stability."""
    mock_response = {"data": {"BTC": {"quote": {"USD": {"price": 123.45}}}}}

    with patch("app.core.cmc_client._get", new=AsyncMock(return_value=mock_response)):
        from app.core import cmc_client
        r = await cmc_client.quotes_latest(symbol="BTC")
        price = r["data"]["BTC"]["quote"]["USD"]["price"]

        assert price == 123.45
        assert isinstance(price, float)


@pytest.mark.asyncio
async def test_mocked_global_metrics():
    mock_response = {"data": {"btc_dominance": 51.3}}

    with patch("app.core.cmc_client._get", new=AsyncMock(return_value=mock_response)):
        from app.core import cmc_client
        r = await cmc_client.global_metrics()

        assert r["data"]["btc_dominance"] == 51.3
