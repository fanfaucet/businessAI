"""Persistence backend contracts for AnnabanAI memory.

The runtime depends on this protocol instead of concrete SQLite APIs so future
PostgreSQL or immutable-audit backends can be introduced without rewriting the
orchestration spine.
"""

from __future__ import annotations

from typing import Any, Protocol

from annabanai.models.runtime import InteractionRecord, RuntimeEvent


class MemoryBackend(Protocol):
    """Source-of-truth persistence contract for runtime memory."""

    def store_interaction(self, record: InteractionRecord, events: list[RuntimeEvent]) -> None:
        """Persist an interaction and its deterministic event trace transactionally."""

    def recent_interactions(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return recent canonical interaction records."""

    def replay_events(self, correlation_id: str | None = None) -> list[dict[str, Any]]:
        """Replay deterministic runtime events, optionally scoped by correlation id."""

    def verify_integrity(self) -> dict[str, Any]:
        """Return backend-specific integrity status."""
