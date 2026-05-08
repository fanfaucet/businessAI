from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

from audit.governance import RecommendationLog, explain
from auth.policy import Principal, Role, can_view
from core.contracts import JurisdictionScope, VisibilityScope
from federation.node_model import AuditRelay, EventBus
from gateways.event_gateway import GatewayPolicy, build_scoped_event
from maritime.engine import MaritimeLogisticsEngine, PortTelemetry, VesselSignal, WeatherOverlay
from simulation.tabletop import ScenarioType, SimulationEvent, TabletopSimulationEngine


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FederatedStackTests(unittest.TestCase):
    def test_gateway_redacts_and_event_bus_replays_by_scope(self) -> None:
        scope = JurisdictionScope("port-authority-a", "pacific", VisibilityScope.SOVEREIGN)
        policy = GatewayPolicy(("ais.telemetry",))
        event = build_scoped_event(
            "ais.telemetry",
            {"vessel_id": "v-1", "crew_name": "protected", "speed": 10},
            scope,
            policy,
        )
        bus = EventBus()
        relay = AuditRelay()
        bus.publish(event)
        relay.index(event)

        self.assertEqual(event.payload["crew_name"], "REDACTED")
        self.assertEqual(len(bus.replay(scope)), 1)
        self.assertEqual(relay.entries()[0][2], "port-authority-a")

    def test_constraint_graph_produces_advisory_recommendation(self) -> None:
        graph_module = load_module("risk-engine/constraint_graph.py", "constraint_graph")
        graph = graph_module.ConstraintGraph()
        graph.add_node(graph_module.ConstraintNode("port", "maritime", 0.4, "j1"))
        graph.add_node(graph_module.ConstraintNode("hospital", "healthcare", 0.2, "j1"))
        graph.add_edge(graph_module.ConstraintEdge("port", "hospital", 0.5, "supply_dependency"))

        impacts = graph.propagate_instability("port", 0.8)
        recommendation = graph.load_balancing_recommendation(impacts, JurisdictionScope("j1", "eu"))

        self.assertIn("hospital", impacts)
        self.assertLess(graph.resilience_score(impacts), 1.0)
        self.assertEqual(recommendation.status.value, "pending_human_review")
        self.assertGreater(recommendation.confidence, 0.5)

    def test_maritime_engine_and_governance_log_are_explainable(self) -> None:
        engine = MaritimeLogisticsEngine()
        scope = JurisdictionScope("j2", "eu")
        risk_map = engine.forecast_congestion(
            vessels=[VesselSignal("v1", "p1", 8, 36, 0.7)],
            weather=[WeatherOverlay("p1", 0.4)],
            telemetry=[PortTelemetry("p1", 0.8, 0.5, "j2")],
        )[0]
        recommendation = engine.advisory_rerouting(risk_map, scope)
        report = explain(recommendation)

        with tempfile.TemporaryDirectory() as tmpdir:
            log = RecommendationLog(str(Path(tmpdir) / "recommendations.jsonl"))
            log.append(recommendation)
            replayed = log.replay()

        self.assertGreater(risk_map.congestion_probability, 0)
        self.assertEqual(report.recommendation_id, recommendation.audit.correlation_id)
        self.assertEqual(len(replayed), 1)

    def test_simulation_and_auth_boundaries(self) -> None:
        result = TabletopSimulationEngine().run(
            "scenario-1",
            [SimulationEvent(ScenarioType.PORT_CLOSURE, "p1", 0.7, 24, "Synthetic closure")],
        )
        sovereign_scope = JurisdictionScope("j3", "pacific", VisibilityScope.SOVEREIGN)
        principal = Principal("user", (Role.SOVEREIGN_OPERATOR,), "j3", "key")

        self.assertTrue(result.simulation_only)
        self.assertGreater(result.cascading_delay_hours, 0)
        self.assertTrue(can_view(principal, sovereign_scope))


if __name__ == "__main__":
    unittest.main()
