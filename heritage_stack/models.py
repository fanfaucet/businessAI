"""Typed Heritage Stack governance contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class ActionCategory(str, Enum):
    """Action categories used to decide whether approval gates are mandatory."""

    READ_ONLY = "read_only"
    ADVISORY = "advisory"
    EXTERNAL_FACING = "external_facing"
    DESTRUCTIVE = "destructive"
    HIGH_STAKES = "high_stakes"
    SYSTEM_STATE_TRANSITION = "system_state_transition"


class GovernanceStatus(str, Enum):
    """Outcome states emitted by the ZYX governance kernel."""

    ALLOW = "allow"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"
    REQUIRE_SIGNATURE_QUORUM = "require_signature_quorum"
    DENY_ZERO_DAMAGE = "deny_zero_damage"


@dataclass(frozen=True)
class ActionRequest:
    """A proposed action that must be evaluated before execution."""

    title: str
    description: str
    category: ActionCategory
    actor_id: str
    target: str
    jurisdiction_id: str
    external_effect: bool = False
    destructive: bool = False
    high_stakes: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class ApprovalRecord:
    """Human-in-the-loop approval evidence."""

    approver_id: str
    request_id: str
    rationale: str
    approved: bool
    timestamp: str


@dataclass(frozen=True)
class SignatureEnvelope:
    """Signature metadata for critical Watchdog Daemon checks.

    Production deployments should bind this interface to Ed25519 verification with
    sovereign-owned keys. The local deterministic verifier is for tests and offline
    scaffolding only.
    """

    signer_id: str
    key_id: str
    algorithm: str
    message_sha256: str
    signature: str


@dataclass(frozen=True)
class GovernanceDecision:
    """Inspectable decision emitted by the Heritage Stack kernel."""

    request_id: str
    status: GovernanceStatus
    rationale: str
    required_approvals: int
    approvals_present: int
    required_signatures: int
    signatures_present: int
    zero_damage_findings: list[str]
    watchdog_findings: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def allowed(self) -> bool:
        return self.status == GovernanceStatus.ALLOW
