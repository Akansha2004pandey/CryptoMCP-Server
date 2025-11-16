import os
import urllib.parse
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv
from .errors import CMCError, NotFoundError, RateLimitError


load_dotenv()


CMC_SANDBOX_KEY = os.getenv("SANDBOX_COIN_BASE_API_KEY")
BASE = "https://sandbox-api.coinmarketcap.com/v1"


HEADERS = {
"Accept": "application/json",
}
if CMC_SANDBOX_KEY:
   HEADERS["X-CMC_PRO_API_KEY"] = CMC_SANDBOX_KEY



async def _get(path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Dict[str, Any]:
    url = urllib.parse.urljoin(BASE + "/", path.lstrip("/"))
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
          r = await client.get(url, params=params, headers=HEADERS)
        except httpx.RequestError as e:
          raise CMCError(f"Request error: {e}")


    if r.status_code == 404:
       raise NotFoundError(r.text)
    if r.status_code == 429:
       raise RateLimitError("Rate limited by CMC")
    if r.status_code >= 400:
       raise CMCError(f"CMC error {r.status_code}: {r.text}")
    try:
       return r.json()
    except Exception:
       raise CMCError("Invalid JSON from CMC")


async def listings_latest(start: int = 1, limit: int = 100, convert: str = "USD") -> Dict[str, Any]:
    params = {"start": start, "limit": limit, "convert": convert}
    return await _get("/cryptocurrency/listings/latest", params=params)


async def quotes_latest(symbol: str = None, id: int = None, convert: str = "USD") -> Dict[str, Any]:
    params = {"convert": convert}
    if symbol:
      params["symbol"] = symbol
    if id:
      params["id"] = id
    return await _get("/cryptocurrency/quotes/latest", params=params)

async def quotes_historical(id: int = None, symbol: str = None, time_start: str = None, time_end: str = None, interval: str = "daily", convert: str = "USD") -> Dict[str, Any]:
    params = {"convert": convert}
    if id:
      params["id"] = id
    if symbol:
      params["symbol"] = symbol
    if time_start:
      params["time_start"] = time_start
    if time_end:
      params["time_end"] = time_end
    if interval:
      params["interval"] = interval
    return await _get("/cryptocurrency/quotes/historical", params=params)


async def info(symbol: str = None, id: int = None) -> Dict[str, Any]:
    params = {}
    if symbol:
     params["symbol"] = symbol
    if id:
     params["id"] = id
    return await _get("/cryptocurrency/info", params=params)


async def exchanges_listings(start: int = 1, limit: int = 50) -> Dict[str, Any]:
    params = {"start": start, "limit": limit}
    return await _get("/exchange/listings/latest", params=params)


async def global_metrics() -> Dict[str, Any]:
    return await _get("/global-metrics/quotes/latest")


async def price_conversion(amount: float, symbol: str, convert: str = "USD") -> Dict[str, Any]:
    params = {"amount": amount, "symbol": symbol, "convert": convert}
    return await _get("/tools/price-conversion", params=params)