"""Zero-Damage Mandate checks for Heritage Stack actions."""

from __future__ import annotations

from heritage_stack.models import ActionCategory, ActionRequest


class ZeroDamageMandate:
    """Deterministic guardrail that prevents unauthorized high-impact actions."""

    forbidden_phrases = (
        "bypass human authority",
        "override human",
        "disable safety",
        "conceal objective",
        "merge protected datasets",
        "centralize sovereign authority",
        "issue binding command",
    )

    gated_categories = {
        ActionCategory.EXTERNAL_FACING,
        ActionCategory.DESTRUCTIVE,
        ActionCategory.HIGH_STAKES,
        ActionCategory.SYSTEM_STATE_TRANSITION,
    }

    def evaluate(self, request: ActionRequest) -> list[str]:
        """Return mandate findings; an empty list means no mandate violation."""
        text = f"{request.title} {request.description}".lower()
        findings = [f"Forbidden phrase detected: {phrase}" for phrase in self.forbidden_phrases if phrase in text]
        if request.destructive and request.category == ActionCategory.READ_ONLY:
            findings.append("Destructive action cannot be labeled read-only")
        if request.high_stakes and request.category == ActionCategory.ADVISORY and request.external_effect:
            findings.append("High-stakes external action cannot be advisory-only without approval gates")
        return findings

    def requires_human_approval(self, request: ActionRequest) -> bool:
        return (
            request.category in self.gated_categories
            or request.external_effect
            or request.destructive
            or request.high_stakes
        )
