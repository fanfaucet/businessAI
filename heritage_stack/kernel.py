"""ZYX Kernel orchestration for the Heritage Stack Zero-Damage Mandate."""

from __future__ import annotations

from heritage_stack.hitl import HumanApprovalGate
from heritage_stack.models import ActionRequest, ApprovalRecord, GovernanceDecision, GovernanceStatus, SignatureEnvelope
from heritage_stack.watchdog import WatchdogDaemon
from heritage_stack.zero_damage import ZeroDamageMandate


class ZYXKernel:
    """Governance-first kernel that gates proposed actions before execution."""

    def __init__(
        self,
        mandate: ZeroDamageMandate | None = None,
        approval_gate: HumanApprovalGate | None = None,
        watchdog: WatchdogDaemon | None = None,
    ) -> None:
        self.mandate = mandate or ZeroDamageMandate()
        self.approval_gate = approval_gate or HumanApprovalGate(required_approvals=1)
        self.watchdog = watchdog or WatchdogDaemon(required_signatures=2)

    def evaluate(
        self,
        request: ActionRequest,
        approvals: list[ApprovalRecord] | None = None,
        signatures: list[SignatureEnvelope] | None = None,
    ) -> GovernanceDecision:
        approvals = approvals or []
        signatures = signatures or []
        zero_damage_findings = self.mandate.evaluate(request)
        approvals_present = self.approval_gate.approved_count(request.request_id, approvals)
        requires_approval = self.mandate.requires_human_approval(request)
        signature_ok, watchdog_findings, signatures_present = self.watchdog.validate(request, signatures)

        if zero_damage_findings:
            status = GovernanceStatus.DENY_ZERO_DAMAGE
            rationale = "Zero-Damage Mandate violation detected."
        elif requires_approval and not self.approval_gate.satisfied(request.request_id, approvals):
            status = GovernanceStatus.REQUIRE_HUMAN_APPROVAL
            rationale = "Human-in-the-loop approval is required before this action can proceed."
        elif requires_approval and not signature_ok:
            status = GovernanceStatus.REQUIRE_SIGNATURE_QUORUM
            rationale = "Watchdog signature quorum is required for critical system calls."
        else:
            status = GovernanceStatus.ALLOW
            rationale = "Action satisfies Zero-Damage, HITL, and Watchdog checks."

        return GovernanceDecision(
            request_id=request.request_id,
            status=status,
            rationale=rationale,
            required_approvals=self.approval_gate.required_approvals if requires_approval else 0,
            approvals_present=approvals_present,
            required_signatures=self.watchdog.required_signatures if requires_approval else 0,
            signatures_present=signatures_present,
            zero_damage_findings=zero_damage_findings,
            watchdog_findings=watchdog_findings if requires_approval else [],
            metadata={"zyx_kernel": "heritage-stack-v1", "requires_approval": requires_approval},
        )
