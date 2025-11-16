from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..core import cmc_client
from ..core.cache import TTLCache
from ..core.errors import CMCError
import os

router = APIRouter(prefix="/api/crypto", tags=["crypto"])
cache = TTLCache()
CACHE_TTL = int(os.getenv("CACHE_TTL", "30"))

@router.get("/listings")
async def listings(start: int = 1, limit: int = 100, convert: str = "USD"):
    key = f"listings:{start}:{limit}:{convert}"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.listings_latest(start=start, limit=limit, convert=convert)
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res

@router.get("/quote")
async def quote(symbol: Optional[str] = Query(None), id: Optional[int] = Query(None), convert: str = "USD"):
    if not symbol and not id:
      raise HTTPException(status_code=400, detail="Provide symbol or id")
    key = f"quote:{symbol or id}:{convert}"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.quotes_latest(symbol=symbol, id=id, convert=convert)
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res



@router.get("/historical")
async def historical(symbol: Optional[str] = Query(None), id: Optional[int] = Query(None), time_start: Optional[str] = Query(None), time_end: Optional[str] = Query(None), interval: str = "daily", convert: str = "USD"):
    if not symbol and not id:
      raise HTTPException(status_code=400, detail="Provide symbol or id")
    key = f"hist:{symbol or id}:{time_start}:{time_end}:{interval}:{convert}"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.quotes_historical(id=id, symbol=symbol, time_start=time_start, time_end=time_end, interval=interval, convert=convert)
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res

@router.get("/info")
async def info(symbol: Optional[str] = Query(None), id: Optional[int] = Query(None)):
    if not symbol and not id:
      raise HTTPException(status_code=400, detail="Provide symbol or id")
    key = f"info:{symbol or id}"
    cached = await cache.get(key)
    if cached:
      return cached
    try:
      res = await cmc_client.info(symbol=symbol, id=id)
    except CMCError as e:
      raise HTTPException(status_code=502, detail=str(e))
    await cache.set(key, res, ttl=CACHE_TTL)
    return res