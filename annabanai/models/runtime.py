"""Typed runtime contracts for AnnabanAI orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    """Return a stable UTC timestamp for persisted runtime records."""
    return datetime.now(timezone.utc).isoformat()


class EventType(str, Enum):
    """Canonical event names emitted by the runtime spine."""

    REQUEST_RECEIVED = "request.received"
    SENTIMENT_ANALYZED = "sentiment.analyzed"
    AGENTS_COMPLETED = "agents.completed"
    PROVIDER_COMPLETED = "provider.completed"
    MEMORY_COMMITTED = "memory.committed"
    AUDIT_MIRRORED = "audit.mirrored"
    REQUEST_FAILED = "request.failed"


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuration for local deterministic runtime execution."""

    db_path: str = "annabanai_state.db"
    audit_path: str = "annabanai_outputs/interactions.jsonl"
    preferred_provider: str = "fallback"
    fallback_provider: str = "fallback"
    request_timeout_seconds: float = 30.0
    max_retries: int = 2
    schema_version: int = 1


@dataclass(frozen=True)
class ProviderRequest:
    """Provider-independent inference request."""

    prompt: str
    system_prompt: str = ""
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderResponse:
    """Provider-independent inference response."""

    text: str
    provider: str
    model: str
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    degraded: bool = False
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SentimentResult:
    """Fused sentiment output from lexical/contextual analyzers."""

    label: str
    score: float
    confidence: float
    distilbert_score: float | None = None
    textblob_score: float | None = None
    rolling_average: float = 0.0
    volatility: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuntimeEvent:
    """Deterministic trace event emitted during a runtime request."""

    sequence: int
    correlation_id: str
    event_type: EventType
    timestamp: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class InteractionRecord:
    """Canonical memory schema; SQLite source-of-truth and JSON audit mirror."""

    correlation_id: str
    timestamp: str
    user_id: str
    user_input: str
    ai_output: str
    sentiment: SentimentResult
    provider: str
    metadata: dict[str, Any]
    audit_hash: str


@dataclass(frozen=True)
class RuntimeResult:
    """Top-level response returned by AnnabanRuntime.process_input."""

    correlation_id: str
    response: str
    sentiment: SentimentResult
    provider_response: ProviderResponse
    events: list[RuntimeEvent]
    telemetry: dict[str, Any]
