"""Versioned cache contracts."""
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class CacheMode(StrEnum):
    EXACT = "exact"
    SEMANTIC = "semantic"


class CacheNamespace(Contract):
    model_version: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    corpus_version: str = Field(min_length=1)


class CacheEntry(Contract):
    key: str
    namespace: CacheNamespace
    normalized_query: str
    response: str
    created_at: datetime
    expires_at: datetime | None


class CacheLookup(Contract):
    hit: bool
    mode: CacheMode
    response: str | None = None
    similarity: float = Field(ge=0, le=1)
    key: str
    reason: Literal["exact_match", "semantic_match", "miss", "expired", "namespace_mismatch"]


class CacheStats(Contract):
    lookups: int = Field(ge=0)
    hits: int = Field(ge=0)
    misses: int = Field(ge=0)
    exact_hits: int = Field(ge=0)
    semantic_hits: int = Field(ge=0)
    false_hits: int = Field(ge=0)
    provider_calls: int = Field(ge=0)

