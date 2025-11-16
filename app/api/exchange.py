from fastapi import APIRouter, HTTPException
from ..core import cmc_client
from ..core.cache import TTLCache
from ..core.errors import CMCError
import os


router = APIRouter(prefix="/api/exchange", tags=["exchange"])
cache = TTLCache()
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))

@router.get("/listings")
async def listings(start: int = 1, limit: int = 50):
    key = f"exchange_listings:{start}:{limit}"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.exchanges_listings(start=start, limit=limit)
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res