from fastapi import APIRouter, HTTPException
from ..core import cmc_client
from ..core.cache import TTLCache
from ..core.errors import CMCError
import os

router = APIRouter(prefix="/api/tools", tags=["tools"])
cache = TTLCache()
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))


@router.get("/convert")
async def convert(amount: float, symbol: str, convert_to: str = "USD"):
    key = f"convert:{amount}:{symbol}:{convert_to}"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.price_conversion(amount=amount, symbol=symbol, convert=convert_to)
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res

