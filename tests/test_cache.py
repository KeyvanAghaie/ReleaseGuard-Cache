from datetime import UTC, datetime, timedelta

import pytest

from releaseguard_cache import CacheMode, CacheNamespace, MemoryCache
from releaseguard_cache.scenarios import run_batch
from releaseguard_cache.service import get_or_set

NAMESPACE = CacheNamespace(model_version="m1", prompt_version="p1", corpus_version="c1")


def test_exact_hit_skips_provider():
    cache = MemoryCache()
    calls = []
    def provider(query):
        calls.append(query)
        return "answer"
    assert get_or_set(cache, "Hello world", NAMESPACE, provider)[0] == "answer"
    assert get_or_set(cache, "Hello world", NAMESPACE, provider)[1].reason == "exact_match"
    assert len(calls) == 1


def test_semantic_hit_skips_provider():
    cache = MemoryCache(semantic_threshold=0.5)
    cache.put("How rotate API key", "cached", NAMESPACE)
    lookup = cache.lookup("How do I rotate the API key?", NAMESPACE)
    assert lookup.hit and lookup.reason == "semantic_match"


def test_namespace_change_is_miss():
    cache = MemoryCache()
    cache.put("same query", "cached", NAMESPACE)
    changed = NAMESPACE.model_copy(update={"model_version": "m2"})
    assert not cache.lookup("same query", changed).hit


def test_expiry_causes_miss():
    current = [datetime(2026, 1, 1, tzinfo=UTC)]
    cache = MemoryCache(now=lambda: current[0])
    cache.put("query", "cached", NAMESPACE, ttl_seconds=10)
    current[0] += timedelta(seconds=11)
    assert cache.lookup("query", NAMESPACE).reason == "expired"


def test_threshold_rejects_false_hit():
    cache = MemoryCache(semantic_threshold=0.9)
    cache.put("billing refund policy", "cached", NAMESPACE)
    assert not cache.lookup("worker restart procedure", NAMESPACE).hit


def test_demo_semantic_saves_calls_and_marks_origin():
    result = run_batch(CacheMode.SEMANTIC)
    assert result["provider_calls"] < 4
    assert result["origin"] == "provider_replay"


def test_invalid_query_rejected():
    with pytest.raises(ValueError):
        MemoryCache().put("", "answer", NAMESPACE)
