from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from annabanai import AnnabanRuntime, RuntimeConfig
from annabanai.models.runtime import SentimentResult
from annabanai.sentiment.engine import SentimentEngine


class StaticSentimentEngine(SentimentEngine):
    def analyze(self, text: str) -> SentimentResult:
        return SentimentResult(
            label="neutral",
            score=0.0,
            confidence=1.0,
            rolling_average=0.0,
            volatility=0.0,
        )


class RuntimeTests(unittest.TestCase):
    def test_process_input_persists_interaction_and_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RuntimeConfig(
                db_path=str(Path(tmpdir) / "state.db"),
                audit_path=str(Path(tmpdir) / "audit.jsonl"),
                preferred_provider="fallback",
            )
            runtime = AnnabanRuntime(config, sentiment_engine=StaticSentimentEngine())

            result = runtime.process_input("Build a deterministic test plan", user_id="tester")

            self.assertEqual(result.provider_response.provider, "fallback")
            self.assertTrue(result.provider_response.degraded)
            self.assertGreaterEqual(len(result.events), 6)
            self.assertEqual(result.events, sorted(result.events, key=lambda event: event.sequence))

            interactions = runtime.memory_manager.recent_interactions()
            self.assertEqual(len(interactions), 1)
            self.assertEqual(interactions[0]["correlation_id"], result.correlation_id)

            replayed = runtime.memory_manager.replay_events(result.correlation_id)
            self.assertGreaterEqual(len(replayed), 5)
            self.assertTrue(Path(config.audit_path).exists())
            chain = runtime.audit_manager.verify_chain()
            self.assertTrue(chain["ok"])
            self.assertEqual(chain["record_count"], 1)

    def test_runtime_health_reports_integrity_and_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RuntimeConfig(
                db_path=str(Path(tmpdir) / "state.db"),
                audit_path=str(Path(tmpdir) / "audit.jsonl"),
            )
            runtime = AnnabanRuntime(config, sentiment_engine=StaticSentimentEngine())
            health = runtime.health()

            self.assertTrue(health["memory"]["ok"])
            self.assertIn("planner", health["agents"])
            self.assertIn("telemetry", health)
            self.assertTrue(health["audit_chain"]["ok"])


if __name__ == "__main__":
    unittest.main()
