from fastapi import APIRouter, HTTPException
from ..core import cmc_client
from ..core.cache import TTLCache
from ..core.errors import CMCError
import os

router = APIRouter(prefix="/api/metrics", tags=["metrics"])
cache = TTLCache()
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))


@router.get("/global")
async def global_metrics():
    key = "global_metrics"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.global_metrics()
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res