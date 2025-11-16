import time
import asyncio
from typing import Any, Optional


class TTLCache:
    def __init__(self):
        self._data = {}
        self._lock = asyncio.Lock()


    async def set(self, key: str, value: Any, ttl: int = 30):
        expires = time.time() + ttl
        async with self._lock:
          self._data[key] = (value, expires)


    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
           entry = self._data.get(key)
           if not entry:
               return None
           value, expires = entry
           if time.time() > expires:
              del self._data[key]
              return None
        return value


    async def delete(self, key: str):
        async with self._lock:
         if key in self._data:
           del self._data[key]


    async def clear(self):
       async with self._lock:
         self._data.clear()