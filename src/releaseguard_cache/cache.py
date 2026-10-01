"""Deterministic in-memory exact and token-semantic cache."""
import hashlib
import re
from datetime import UTC, datetime, timedelta
from threading import RLock

from .models import CacheEntry, CacheLookup, CacheMode, CacheNamespace, CacheStats


def normalize(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def similarity(left: str, right: str) -> float:
    a, b = set(normalize(left).split()), set(normalize(right).split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class MemoryCache:
    def __init__(self, semantic_threshold: float = 0.82, now=None):
        if not 0 <= semantic_threshold <= 1:
            raise ValueError("semantic_threshold must be between 0 and 1")
        self.semantic_threshold = semantic_threshold
        self._entries: dict[str, CacheEntry] = {}
        self._lock = RLock()
        self._now = now or (lambda: datetime.now(UTC))
        self._stats = CacheStats(lookups=0, hits=0, misses=0, exact_hits=0, semantic_hits=0, false_hits=0, provider_calls=0)

    @staticmethod
    def key(query: str, namespace: CacheNamespace) -> str:
        raw = "|".join([namespace.model_version, namespace.prompt_version, namespace.corpus_version, normalize(query)])
        return hashlib.sha256(raw.encode()).hexdigest()

    def lookup(self, query: str, namespace: CacheNamespace, mode: CacheMode = CacheMode.SEMANTIC) -> CacheLookup:
        normalized = normalize(query)
        key = self.key(query, namespace)
        now = self._now()
        with self._lock:
            self._stats = self._stats.model_copy(update={"lookups": self._stats.lookups + 1})
            entry = self._entries.get(key)
            if entry and entry.expires_at and entry.expires_at <= now:
                del self._entries[key]
                entry = None
                reason = "expired"
            elif entry:
                self._stats = self._stats.model_copy(update={"hits": self._stats.hits + 1, "exact_hits": self._stats.exact_hits + 1})
                return CacheLookup(hit=True, mode=CacheMode.EXACT, response=entry.response, similarity=1, key=key, reason="exact_match")
            else:
                reason = "miss"
            if mode == CacheMode.SEMANTIC:
                candidates = [e for e in self._entries.values() if e.namespace == namespace and not (e.expires_at and e.expires_at <= now)]
                ranked = sorted(((similarity(normalized, e.normalized_query), e) for e in candidates), key=lambda pair: (-pair[0], pair[1].key))
                if ranked and ranked[0][0] >= self.semantic_threshold:
                    score, candidate = ranked[0]
                    self._stats = self._stats.model_copy(update={"hits": self._stats.hits + 1, "semantic_hits": self._stats.semantic_hits + 1})
                    return CacheLookup(hit=True, mode=mode, response=candidate.response, similarity=score, key=candidate.key, reason="semantic_match")
            self._stats = self._stats.model_copy(update={"misses": self._stats.misses + 1})
            return CacheLookup(hit=False, mode=mode, similarity=0, key=key, reason=reason if reason == "expired" else "miss")

    def put(self, query: str, response: str, namespace: CacheNamespace, ttl_seconds: int | None = None) -> CacheEntry:
        if not query.strip() or not response:
            raise ValueError("query and response are required")
        now = self._now()
        entry = CacheEntry(key=self.key(query, namespace), namespace=namespace, normalized_query=normalize(query), response=response, created_at=now, expires_at=now + timedelta(seconds=ttl_seconds) if ttl_seconds is not None else None)
        with self._lock:
            self._entries[entry.key] = entry
        return entry

    def record_provider_call(self):
        with self._lock:
            self._stats = self._stats.model_copy(update={"provider_calls": self._stats.provider_calls + 1})

    def stats(self) -> CacheStats:
        with self._lock:
            return self._stats

