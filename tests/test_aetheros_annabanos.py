from __future__ import annotations

import unittest

from datetime import datetime, timedelta, timezone

from aetheros import AetherOSAPIEmulator, AetherOSMode, AetherOSRequest, AetherOSRoute
from core.contracts import JurisdictionScope, VisibilityScope
from heritage_stack import GovernanceStatus


class AetherOSAnnabanOSTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = JurisdictionScope("j-test", "test-region", VisibilityScope.SOVEREIGN)
        self.emulator = AetherOSAPIEmulator()

    def test_status_route_exposes_advisory_constraints(self) -> None:
        response = self.emulator.handle(AetherOSRequest(AetherOSRoute.STATUS, self.scope))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.advisory_only)
        self.assertIn("no_binding_commands", response.body["constraints"])
        self.assertTrue(response.body["routes"][0].startswith("/api/v1/"))
        self.assertEqual(response.body["capabilities"][AetherOSRoute.STATUS.value], "read_only")

    def test_annabanos_execution_blocks_external_action_without_hitl(self) -> None:
        response = self.emulator.handle(
            AetherOSRequest(
                AetherOSRoute.ANNABANOS_EXECUTION,
                self.scope,
                payload={
                    "title": "Publish external advisory",
                    "description": "Prepare an external advisory summary for review.",
                    "category": "external_facing",
                    "external_effect": True,
                },
            )
        )

        result = response.body["execution_result"]
        self.assertEqual(result["status"], "blocked_by_governance")
        self.assertEqual(result["governance_decision"]["status"], GovernanceStatus.REQUIRE_HUMAN_APPROVAL.value)
        self.assertTrue(result["dry_run"])
        self.assertTrue(result["advisory_only"])

    def test_annabanos_read_only_execution_returns_dry_run_plan(self) -> None:
        response = self.emulator.handle(
            AetherOSRequest(
                AetherOSRoute.ANNABANOS_EXECUTION,
                self.scope,
                payload={
                    "title": "Inspect local advisory cache",
                    "description": "Review cached advisory metadata.",
                    "category": "read_only",
                },
            )
        )

        result = response.body["execution_result"]
        self.assertEqual(result["status"], "dry_run_ready")
        self.assertGreater(len(result["planned_steps"]), 0)
        self.assertTrue(result["dry_run"])

    def test_annabanai_automation_uses_fallback_and_returns_advisory_output(self) -> None:
        response = self.emulator.handle(
            AetherOSRequest(
                AetherOSRoute.ANNABANAI_AUTOMATION,
                self.scope,
                payload={"prompt": "Summarize the local advisory state.", "user_id": "test-user"},
            )
        )

        result = response.body["automation_result"]
        self.assertTrue(result["advisory_only"])
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["provider"]["provider"], "fallback")

    def test_capability_policy_rejects_escalation_above_route_ceiling(self) -> None:
        response = self.emulator.handle(
            AetherOSRequest(
                AetherOSRoute.ANNABANAI_AUTOMATION,
                self.scope,
                payload={"prompt": "Summarize state", "capability": "critical"},
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("exceeds route ceiling", response.errors[0])

    def test_expired_scope_is_rejected(self) -> None:
        expired_scope = JurisdictionScope(
            "j-expired",
            "test-region",
            VisibilityScope.SOVEREIGN,
            expires_at=(datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        )
        response = self.emulator.handle(AetherOSRequest(AetherOSRoute.STATUS, expired_scope))

        self.assertEqual(response.status_code, 400)
        self.assertIn("expired", response.errors[0])

    def test_simulation_mode_requires_simulation_scope(self) -> None:
        response = self.emulator.handle(AetherOSRequest(AetherOSRoute.STATUS, self.scope, mode=AetherOSMode.SIMULATION_ONLY))

        self.assertEqual(response.status_code, 400)
        self.assertTrue(response.advisory_only)


class AnnabanBootSimulationTests(unittest.TestCase):
    def test_annaban_boot_simulation_returns_persona_stages_from_emulation(self) -> None:
        scope = JurisdictionScope("j-boot", "test-region", VisibilityScope.SOVEREIGN)
        emulator = AetherOSAPIEmulator()

        response = emulator.handle(
            AetherOSRequest(
                AetherOSRoute.ANNABAN_BOOT,
                scope,
                payload={"boot_id": "boot-test", "courses": ["python_basics"], "memory_buckets": ["skills"]},
            )
        )

        result = response.body["boot_result"]
        stage_names = {stage["name"] for stage in result["stages"]}
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result["dry_run"])
        self.assertTrue(result["advisory_only"])
        self.assertEqual(result["profile"]["persona_name"], "Annaban Advanced Persona Agent")
        self.assertIn("sle_module", stage_names)
        self.assertIn("memory_buckets", stage_names)
        self.assertEqual(result["automation_summary"]["provider"]["provider"], "fallback")


if __name__ == "__main__":
    unittest.main()
