"""AnnabanOS advisory execution evaluation.

Execution in this package means local evaluation and dry-run planning only. It does
not invoke shell commands, network calls, sensors, actuators, or external systems.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from core.contracts import JurisdictionScope
from heritage_stack import ActionCategory, ActionRequest, ApprovalRecord, GovernanceDecision, SignatureEnvelope, ZYXKernel


@dataclass(frozen=True)
class AnnabanExecutionRequest:
    """A proposed AnnabanOS task evaluated by Heritage Stack controls."""

    title: str
    description: str
    category: ActionCategory
    actor_id: str
    target: str
    scope: JurisdictionScope
    external_effect: bool = False
    destructive: bool = False
    high_stakes: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_action_request(self) -> ActionRequest:
        return ActionRequest(
            title=self.title,
            description=self.description,
            category=self.category,
            actor_id=self.actor_id,
            target=self.target,
            jurisdiction_id=self.scope.jurisdiction_id,
            external_effect=self.external_effect,
            destructive=self.destructive,
            high_stakes=self.high_stakes,
            metadata={**self.metadata, "visibility": self.scope.visibility.value, "region": self.scope.region},
        )


@dataclass(frozen=True)
class AnnabanExecutionResult:
    """Dry-run execution result; no external action is performed."""

    request_title: str
    dry_run: bool
    advisory_only: bool
    status: str
    governance_decision: GovernanceDecision
    planned_steps: list[str]
    blocked_reason: str | None = None


class AnnabanExecutionEngine:
    """Evaluate Annaban execution payloads under ZYX/Zero-Damage controls."""

    def __init__(self, kernel: ZYXKernel | None = None) -> None:
        self.kernel = kernel or ZYXKernel()

    def evaluate(
        self,
        request: AnnabanExecutionRequest,
        approvals: list[ApprovalRecord] | None = None,
        signatures: list[SignatureEnvelope] | None = None,
    ) -> AnnabanExecutionResult:
        action = request.to_action_request()
        decision = self.kernel.evaluate(action, approvals=approvals, signatures=signatures)
        if not decision.allowed:
            return AnnabanExecutionResult(
                request_title=request.title,
                dry_run=True,
                advisory_only=True,
                status="blocked_by_governance",
                governance_decision=decision,
                planned_steps=[],
                blocked_reason=decision.rationale,
            )
        return AnnabanExecutionResult(
            request_title=request.title,
            dry_run=True,
            advisory_only=True,
            status="dry_run_ready",
            governance_decision=decision,
            planned_steps=[
                "Validate scoped input payload.",
                "Generate advisory execution plan.",
                "Record dry-run audit summary.",
                "Return plan for human review; perform no external action.",
            ],
        )

    def evaluate_payload(self, payload: dict[str, Any], scope: JurisdictionScope) -> AnnabanExecutionResult:
        category_value = payload.get("category", ActionCategory.ADVISORY.value)
        request = AnnabanExecutionRequest(
            title=payload.get("title", "Untitled AnnabanOS advisory execution"),
            description=payload.get("description", "No description supplied."),
            category=ActionCategory(category_value),
            actor_id=payload.get("actor_id", "aetheros-emulator"),
            target=payload.get("target", "local-advisory-plane"),
            scope=scope,
            external_effect=bool(payload.get("external_effect", False)),
            destructive=bool(payload.get("destructive", False)),
            high_stakes=bool(payload.get("high_stakes", False)),
            metadata=payload.get("metadata", {}),
        )
        return self.evaluate(request)

    def result_dict(self, result: AnnabanExecutionResult) -> dict[str, Any]:
        return asdict(result)
