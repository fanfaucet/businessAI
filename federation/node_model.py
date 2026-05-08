"""Federated node topology for sovereignty-preserving coordination."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4

from core.contracts import AuditMetadata, JurisdictionScope, VisibilityScope


class NodeRole(str, Enum):
    SOVEREIGN_EDGE = "sovereign_edge"
    REGIONAL_RELAY = "regional_relay"
    AUDIT_RELAY = "audit_relay"
    SIMULATION_SANDBOX = "simulation_sandbox"


@dataclass(frozen=True)
class SovereignNode:
    node_id: str
    scope: JurisdictionScope
    roles: tuple[NodeRole, ...] = (NodeRole.SOVEREIGN_EDGE,)
    public_key_ref: str = "sovereign-owned-key"
    data_residency_policy: str = "local-only-by-default"


@dataclass(frozen=True)
class RegionalCluster:
    cluster_id: str
    region: str
    nodes: tuple[SovereignNode, ...]
    subnet_label: str

    def visible_nodes(self, scope: VisibilityScope) -> list[SovereignNode]:
        return [node for node in self.nodes if node.scope.visibility == scope or scope == VisibilityScope.EMERGENCY]


@dataclass(frozen=True)
class FederatedEvent:
    event_type: str
    payload: dict[str, Any]
    scope: JurisdictionScope
    audit: AuditMetadata
    event_id: str = field(default_factory=lambda: str(uuid4()))
    advisory_only: bool = True


class EventBus:
    """In-memory placeholder for scoped, append-only event exchange."""

    def __init__(self) -> None:
        self._events: list[FederatedEvent] = []

    def publish(self, event: FederatedEvent) -> None:
        if not event.advisory_only:
            raise ValueError("Federated events must remain advisory-only")
        self._events.append(event)

    def replay(self, scope: JurisdictionScope | None = None) -> list[FederatedEvent]:
        if scope is None:
            return list(self._events)
        return [event for event in self._events if event.scope.jurisdiction_id == scope.jurisdiction_id]


class AuditRelay:
    """Append-only relay index; payload storage remains with sovereign owners."""

    def __init__(self) -> None:
        self._index: list[tuple[str, str, str]] = []

    def index(self, event: FederatedEvent) -> None:
        self._index.append((event.event_id, event.audit.correlation_id, event.scope.jurisdiction_id))

    def entries(self) -> list[tuple[str, str, str]]:
        return list(self._index)
