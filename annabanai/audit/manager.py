"""Append-only JSON audit mirror for AnnabanAI."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from typing import Any

from annabanai.models.runtime import InteractionRecord, RuntimeEvent

GENESIS_AUDIT_HASH = "GENESIS"


class AuditManager:
    """Write deterministic JSONL audit records with chained integrity metadata."""

    def __init__(self, audit_path: str) -> None:
        self.audit_path = Path(audit_path)
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def compute_hash(self, payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def previous_hash(self) -> str:
        """Return the latest audit event hash or the genesis marker."""
        if not self.audit_path.exists():
            return GENESIS_AUDIT_HASH
        with self._lock, self.audit_path.open("r", encoding="utf-8") as audit_file:
            for line in reversed(audit_file.readlines()):
                if line.strip():
                    return json.loads(line).get("event_hash", GENESIS_AUDIT_HASH)
        return GENESIS_AUDIT_HASH

    def build_payload(self, record: InteractionRecord, events: list[RuntimeEvent]) -> dict[str, Any]:
        return {
            "interaction": asdict(record),
            "events": [asdict(event) for event in events],
        }

    def build_chained_record(self, record: InteractionRecord, events: list[RuntimeEvent]) -> dict[str, Any]:
        """Create a tamper-evident audit record linked to the previous line."""
        payload = self.build_payload(record, events)
        previous_hash = self.previous_hash()
        payload_hash = self.compute_hash(payload)
        event_hash = self.compute_hash({"previous_hash": previous_hash, "payload_hash": payload_hash})
        return {
            "event_hash": event_hash,
            "previous_hash": previous_hash,
            "payload_hash": payload_hash,
            "payload": payload,
        }

    def mirror(self, record: InteractionRecord, events: list[RuntimeEvent]) -> None:
        chained_record = self.build_chained_record(record, events)
        with self._lock, self.audit_path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(chained_record, sort_keys=True, default=str))
            audit_file.write("\n")

    def read_events(self, limit: int = 100) -> list[dict[str, Any]]:
        if not self.audit_path.exists():
            return []
        with self._lock, self.audit_path.open("r", encoding="utf-8") as audit_file:
            lines = audit_file.readlines()[-limit:]
        return [json.loads(line) for line in lines if line.strip()]

    def verify_chain(self) -> dict[str, Any]:
        """Verify audit JSONL continuity and payload hashes from genesis to tail."""
        if not self.audit_path.exists():
            return {"ok": True, "record_count": 0, "tail_hash": GENESIS_AUDIT_HASH, "errors": []}
        errors: list[str] = []
        expected_previous = GENESIS_AUDIT_HASH
        tail_hash = GENESIS_AUDIT_HASH
        records = self.read_events(limit=1_000_000)
        for index, record in enumerate(records):
            previous_hash = record.get("previous_hash")
            payload = record.get("payload")
            payload_hash = record.get("payload_hash")
            event_hash = record.get("event_hash")
            if previous_hash != expected_previous:
                errors.append(f"record {index}: previous hash mismatch")
            recomputed_payload_hash = self.compute_hash(payload)
            if payload_hash != recomputed_payload_hash:
                errors.append(f"record {index}: payload hash mismatch")
            recomputed_event_hash = self.compute_hash({"previous_hash": previous_hash, "payload_hash": payload_hash})
            if event_hash != recomputed_event_hash:
                errors.append(f"record {index}: event hash mismatch")
            expected_previous = event_hash
            tail_hash = event_hash
        return {"ok": not errors, "record_count": len(records), "tail_hash": tail_hash, "errors": errors}
