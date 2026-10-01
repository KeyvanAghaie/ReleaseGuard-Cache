from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from releaseguard_cache.models import CacheMode
from releaseguard_cache.scenarios import run_batch

app = FastAPI(title="ReleaseGuard Cache", version="0.1.0")


class CacheRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Literal["exact", "semantic"] = "semantic"


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.post("/api/cache-demo")
def cache_demo(request: CacheRequest):
    return run_batch(CacheMode(request.mode))

