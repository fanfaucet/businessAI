"""Human-in-the-loop approval gates for Heritage Stack actions."""

from __future__ import annotations

from heritage_stack.models import ApprovalRecord


class HumanApprovalGate:
    """Validate human approval evidence for gated actions."""

    def __init__(self, required_approvals: int = 1) -> None:
        if required_approvals < 1:
            raise ValueError("At least one human approval is required")
        self.required_approvals = required_approvals

    def approved_count(self, request_id: str, approvals: list[ApprovalRecord]) -> int:
        approvers = {
            approval.approver_id
            for approval in approvals
            if approval.request_id == request_id and approval.approved
        }
        return len(approvers)

    def satisfied(self, request_id: str, approvals: list[ApprovalRecord]) -> bool:
        return self.approved_count(request_id, approvals) >= self.required_approvals
