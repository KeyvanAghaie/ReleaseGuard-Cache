from collections.abc import Callable

from .cache import MemoryCache
from .models import CacheLookup, CacheMode, CacheNamespace


def get_or_set(cache: MemoryCache, query: str, namespace: CacheNamespace, provider: Callable[[str], str], *, ttl_seconds: int | None = None, mode: CacheMode = CacheMode.SEMANTIC) -> tuple[str, CacheLookup]:
    lookup = cache.lookup(query, namespace, mode)
    if lookup.hit:
        return lookup.response or "", lookup
    response = provider(query)
    cache.record_provider_call()
    cache.put(query, response, namespace, ttl_seconds)
    return response, lookup

