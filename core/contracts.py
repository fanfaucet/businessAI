"""Shared advisory-first contracts for the federated governance stack."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class VisibilityScope(str, Enum):
    """Visibility modes that preserve jurisdiction-specific access boundaries."""

    SOVEREIGN = "sovereign"
    COALITION = "coalition"
    EMERGENCY = "emergency"
    SIMULATION_ONLY = "simulation_only"


class CapabilityClass(str, Enum):
    """Capability classes for advisory escalation and audit classification."""

    READ_ONLY = "read_only"
    ADVISORY = "advisory"
    SIMULATION = "simulation"
    EXTERNAL_EFFECT = "external_effect"
    CRITICAL = "critical"


CAPABILITY_ORDER = {
    CapabilityClass.READ_ONLY: 0,
    CapabilityClass.ADVISORY: 1,
    CapabilityClass.SIMULATION: 2,
    CapabilityClass.EXTERNAL_EFFECT: 3,
    CapabilityClass.CRITICAL: 4,
}


def capability_allows(maximum: CapabilityClass, requested: CapabilityClass) -> bool:
    """Return whether a route/agent capability ceiling allows a request."""
    return CAPABILITY_ORDER[requested] <= CAPABILITY_ORDER[maximum]


class RecommendationStatus(str, Enum):
    """Recommendation lifecycle; there is deliberately no auto-execute state."""

    DRAFT = "draft"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    APPROVED_BY_HUMAN = "approved_by_human"
    REJECTED_BY_HUMAN = "rejected_by_human"
    SUPERSEDED = "superseded"


@dataclass(frozen=True)
class JurisdictionScope:
    """A sovereign visibility boundary for data, policies, and recommendations."""

    jurisdiction_id: str
    region: str
    visibility: VisibilityScope = VisibilityScope.SOVEREIGN
    coalition_id: str | None = None
    expires_at: str | None = None

    def is_expired(self, now: datetime | None = None) -> bool:
        """Return whether temporary visibility has expired."""
        if self.expires_at is None:
            return False
        current = now or datetime.now(timezone.utc)
        expires = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return current >= expires


@dataclass(frozen=True)
class AuditMetadata:
    """Metadata required for replayable and explainable audit trails."""

    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    actor_id: str = "system"
    source_node_id: str = "local-node"
    policy_version: str = "v1"


@dataclass(frozen=True)
class ConstraintImpact:
    """A single weighted constraint affected by a recommendation or event."""

    constraint_id: str
    category: str
    weight: float
    projected_delta: float
    rationale: str


@dataclass(frozen=True)
class AdvisoryRecommendation:
    """A non-binding recommendation requiring human review before action."""

    title: str
    rationale: str
    confidence: float
    affected_constraints: list[ConstraintImpact]
    projected_tradeoffs: list[str]
    scope: JurisdictionScope
    audit: AuditMetadata
    status: RecommendationStatus = RecommendationStatus.PENDING_HUMAN_REVIEW
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_advisory_only(self) -> None:
        if self.status == RecommendationStatus.APPROVED_BY_HUMAN:
            return
        forbidden_terms = ["must reroute", "command", "override", "force"]
        text = f"{self.title} {self.rationale}".lower()
        if any(term in text for term in forbidden_terms):
            raise ValueError("Recommendation language must remain advisory and non-coercive")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
