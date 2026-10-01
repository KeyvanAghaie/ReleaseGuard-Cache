# ReleaseGuard Cache

**Reduce provider calls without pretending similar means identical.**

Capability **06 / 09** in the AI ReleaseGuard portfolio. The package provides exact and token-semantic cache lookup, a versioned namespace, TTL expiry, observable similarity scores, and a small optional Redis adapter.

## Quickstart

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[demo,dev]"
.\.venv\Scripts\python.exe -m pytest -q
pnpm install --frozen-lockfile
pnpm build
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000` and run the semantic or exact batch. Provider answers are replay fixtures. The UI shows every lookup, hit reason, similarity, and provider call count. Replay time saved is not presented as real LLM cost savings.

## Contract

Every key includes `model_version`, `prompt_version`, `corpus_version`, and normalized query. A namespace change is a miss. TTL expiry is a miss. Semantic hits require a configurable Jaccard token threshold and return their score; below-threshold queries remain misses so false hits can be measured rather than hidden.

```python
from releaseguard_cache import CacheNamespace, MemoryCache
from releaseguard_cache.service import get_or_set

namespace = CacheNamespace(model_version="model-v1", prompt_version="answer-v2", corpus_version="ops-v1")
cache = MemoryCache(semantic_threshold=0.82)
answer, lookup = get_or_set(cache, "How do I rotate an API key?", namespace, provider)
```

The in-memory backend is used by the demo. `RedisCache` is an optional adapter for local deployments:

```powershell
docker compose up -d redis
```

The adapter deliberately does not claim cross-region coordination or production eviction policy in this v0.1 release.

## Limits

The semantic matcher is a deterministic lexical token similarity baseline, not an embedding model. Corpus and prompt versioning are caller responsibilities. The public demo has batch-local state and no user upload, authentication, persistence, or live provider call.

License: MIT.

