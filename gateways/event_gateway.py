"""Scoped event gateway helpers for federated ingress."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.contracts import AuditMetadata, JurisdictionScope
from federation.node_model import FederatedEvent


@dataclass(frozen=True)
class GatewayPolicy:
    allowed_event_types: tuple[str, ...]
    redact_keys: tuple[str, ...] = ("patient_id", "crew_name", "personal_identifier")


def redact(payload: dict[str, Any], policy: GatewayPolicy) -> dict[str, Any]:
    return {key: ("REDACTED" if key in policy.redact_keys else value) for key, value in payload.items()}


def build_scoped_event(event_type: str, payload: dict[str, Any], scope: JurisdictionScope, policy: GatewayPolicy) -> FederatedEvent:
    if event_type not in policy.allowed_event_types:
        raise ValueError("Event type is not allowed by this gateway policy")
    return FederatedEvent(event_type=event_type, payload=redact(payload, policy), scope=scope, audit=AuditMetadata(actor_id="gateway"))
