"""SQLite source-of-truth persistence for AnnabanAI interactions."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from typing import Any

from annabanai.memory.backends import MemoryBackend
from annabanai.models.runtime import InteractionRecord, RuntimeConfig, RuntimeEvent, utc_now_iso


class MemoryManager(MemoryBackend):
    """Transactional SQLite memory backend with schema versioning and replay support."""

    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self.db_path = Path(config.db_path)
        if self.db_path.parent != Path("."):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def initialize(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    correlation_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    user_input TEXT NOT NULL,
                    ai_output TEXT NOT NULL,
                    sentiment_json TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    audit_hash TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    correlation_id TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    UNIQUE(correlation_id, sequence)
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (self.config.schema_version, utc_now_iso()),
            )
            conn.commit()

    def store_interaction(self, record: InteractionRecord, events: list[RuntimeEvent]) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("BEGIN")
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO interactions(
                        correlation_id, timestamp, user_id, user_input, ai_output,
                        sentiment_json, provider, metadata_json, audit_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.correlation_id,
                        record.timestamp,
                        record.user_id,
                        record.user_input,
                        record.ai_output,
                        json.dumps(asdict(record.sentiment), sort_keys=True),
                        record.provider,
                        json.dumps(record.metadata, sort_keys=True),
                        record.audit_hash,
                    ),
                )
                for event in events:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO runtime_events(
                            correlation_id, sequence, event_type, timestamp, payload_json
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            event.correlation_id,
                            event.sequence,
                            event.event_type.value,
                            event.timestamp,
                            json.dumps(event.payload, sort_keys=True),
                        ),
                    )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def recent_interactions(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM interactions ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._decode_interaction(row) for row in rows]

    def replay_events(self, correlation_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM runtime_events"
        params: tuple[Any, ...] = ()
        if correlation_id:
            query += " WHERE correlation_id = ?"
            params = (correlation_id,)
        query += " ORDER BY timestamp ASC, sequence ASC"
        with self._lock, self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "correlation_id": row["correlation_id"],
                "sequence": row["sequence"],
                "event_type": row["event_type"],
                "timestamp": row["timestamp"],
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]

    def verify_integrity(self) -> dict[str, Any]:
        with self._lock, self._connect() as conn:
            quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
            interaction_count = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
            event_count = conn.execute("SELECT COUNT(*) FROM runtime_events").fetchone()[0]
            schema_versions = [row[0] for row in conn.execute("SELECT version FROM schema_migrations ORDER BY version")]
        return {
            "ok": quick_check == "ok",
            "quick_check": quick_check,
            "interaction_count": interaction_count,
            "event_count": event_count,
            "schema_versions": schema_versions,
        }

    def _decode_interaction(self, row: sqlite3.Row) -> dict[str, Any]:
        return {
            "correlation_id": row["correlation_id"],
            "timestamp": row["timestamp"],
            "user_id": row["user_id"],
            "user_input": row["user_input"],
            "ai_output": row["ai_output"],
            "sentiment": json.loads(row["sentiment_json"]),
            "provider": row["provider"],
            "metadata": json.loads(row["metadata_json"]),
            "audit_hash": row["audit_hash"],
        }
