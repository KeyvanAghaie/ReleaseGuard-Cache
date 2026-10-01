"""Optional Redis backend for local deployments; the demo uses MemoryCache."""

from .models import CacheEntry


class RedisCache:
    def __init__(self, client, prefix: str = "releaseguard:cache:"):
        self.client, self.prefix = client, prefix

    def put(self, entry: CacheEntry, ttl_seconds: int | None = None) -> None:
        payload = entry.model_dump_json()
        if ttl_seconds is None:
            self.client.set(self.prefix + entry.key, payload)
        else:
            self.client.setex(self.prefix + entry.key, ttl_seconds, payload)

    def get(self, key: str) -> CacheEntry | None:
        payload = self.client.get(self.prefix + key)
        if payload is None:
            return None
        if isinstance(payload, bytes):
            payload = payload.decode()
        return CacheEntry.model_validate_json(payload)

