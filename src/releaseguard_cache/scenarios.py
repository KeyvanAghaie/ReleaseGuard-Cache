from .cache import MemoryCache
from .models import CacheMode, CacheNamespace
from .service import get_or_set

NAMESPACE = CacheNamespace(model_version="demo-model-v1", prompt_version="answer-v2", corpus_version="ops-qa-v1")


def run_batch(mode: CacheMode = CacheMode.SEMANTIC):
    cache = MemoryCache(semantic_threshold=0.35)
    calls = []
    queries = ["How do I rotate an API key?", "How should I rotate my API keys?", "What is the API key rotation process?", "How do I restart a worker?"]

    def provider(query: str) -> str:
        calls.append(query)
        return f"Replay answer for: {query}"

    rows = []
    for query in queries:
        response, lookup = get_or_set(cache, query, NAMESPACE, provider, ttl_seconds=3600, mode=mode)
        rows.append({"query": query, "response": response, "lookup": lookup.model_dump(mode="json")})
    return {"rows": rows, "provider_calls": len(calls), "stats": cache.stats().model_dump(mode="json"), "origin": "provider_replay"}
