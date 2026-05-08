from __future__ import annotations

import unittest
from datetime import datetime, timezone

from heritage_stack import (
    ActionCategory,
    ActionRequest,
    ApprovalRecord,
    DeterministicSha256Verifier,
    GovernanceStatus,
    SignatureEnvelope,
    ZYXKernel,
)


class HeritageStackTests(unittest.TestCase):
    def _signatures(self, kernel: ZYXKernel, request: ActionRequest) -> list[SignatureEnvelope]:
        verifier = DeterministicSha256Verifier()
        digest = kernel.watchdog.message_sha256(request)
        return [
            SignatureEnvelope("watcher-a", "key-a", verifier.algorithm, digest, verifier.sign("key-a", digest)),
            SignatureEnvelope("watcher-b", "key-b", verifier.algorithm, digest, verifier.sign("key-b", digest)),
        ]

    def test_read_only_action_is_allowed_without_approval(self) -> None:
        kernel = ZYXKernel()
        request = ActionRequest(
            title="Inspect audit log",
            description="Read local audit entries for review.",
            category=ActionCategory.READ_ONLY,
            actor_id="analyst",
            target="audit-log",
            jurisdiction_id="j1",
        )

        decision = kernel.evaluate(request)

        self.assertEqual(decision.status, GovernanceStatus.ALLOW)
        self.assertEqual(decision.required_approvals, 0)
        self.assertEqual(decision.required_signatures, 0)

    def test_external_action_requires_human_approval_then_signature_quorum(self) -> None:
        kernel = ZYXKernel()
        request = ActionRequest(
            title="Publish advisory summary",
            description="Send a public advisory summary to coalition observers.",
            category=ActionCategory.EXTERNAL_FACING,
            actor_id="operator",
            target="coalition-feed",
            jurisdiction_id="j1",
            external_effect=True,
        )

        missing_approval = kernel.evaluate(request)
        self.assertEqual(missing_approval.status, GovernanceStatus.REQUIRE_HUMAN_APPROVAL)

        approvals = [
            ApprovalRecord(
                approver_id="human-1",
                request_id=request.request_id,
                rationale="Reviewed advisory text and scope.",
                approved=True,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        ]
        missing_signatures = kernel.evaluate(request, approvals=approvals)
        self.assertEqual(missing_signatures.status, GovernanceStatus.REQUIRE_SIGNATURE_QUORUM)

        allowed = kernel.evaluate(request, approvals=approvals, signatures=self._signatures(kernel, request))
        self.assertEqual(allowed.status, GovernanceStatus.ALLOW)
        self.assertTrue(allowed.allowed)

    def test_zero_damage_mandate_denies_binding_command_language(self) -> None:
        kernel = ZYXKernel()
        request = ActionRequest(
            title="Issue binding command",
            description="Attempt to bypass human authority and centralize sovereign authority.",
            category=ActionCategory.HIGH_STAKES,
            actor_id="system",
            target="fleet",
            jurisdiction_id="j1",
            high_stakes=True,
        )

        decision = kernel.evaluate(request, signatures=self._signatures(kernel, request))

        self.assertEqual(decision.status, GovernanceStatus.DENY_ZERO_DAMAGE)
        self.assertGreaterEqual(len(decision.zero_damage_findings), 2)


if __name__ == "__main__":
    unittest.main()
