import json
from typing import Optional
import redis.asyncio as redis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = None):
        if not self.client:
            return
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)

    async def delete(self, key: str):
        if not self.client:
            return
        await self.client.delete(key)

    async def get_json(self, key: str):
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(self, key: str, value, ttl: int = None):
        json_str = json.dumps(value)
        await self.set(key, json_str, ttl)


redis_client = RedisClient()
