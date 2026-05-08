"""Inspectable weighted constraint graph for advisory risk propagation."""

from __future__ import annotations

from dataclasses import dataclass, field
from heapq import heappop, heappush
from typing import Iterable

from core.contracts import AdvisoryRecommendation, AuditMetadata, ConstraintImpact, JurisdictionScope


@dataclass(frozen=True)
class ConstraintNode:
    node_id: str
    category: str
    baseline_load: float
    jurisdiction_id: str


@dataclass(frozen=True)
class ConstraintEdge:
    source: str
    target: str
    weight: float
    relationship: str


@dataclass
class ConstraintGraph:
    nodes: dict[str, ConstraintNode] = field(default_factory=dict)
    edges: list[ConstraintEdge] = field(default_factory=list)

    def add_node(self, node: ConstraintNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, edge: ConstraintEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Edges require existing source and target nodes")
        self.edges.append(edge)

    def neighbors(self, node_id: str) -> Iterable[ConstraintEdge]:
        return (edge for edge in self.edges if edge.source == node_id)

    def propagate_instability(self, seed_node_id: str, shock: float, depth: int = 3) -> dict[str, float]:
        if seed_node_id not in self.nodes:
            raise ValueError("Unknown seed node")
        impacts = {seed_node_id: min(1.0, max(0.0, shock))}
        queue = [(0, seed_node_id, impacts[seed_node_id])]
        while queue:
            current_depth, node_id, current_impact = heappop(queue)
            if current_depth >= depth:
                continue
            for edge in self.neighbors(node_id):
                propagated = max(0.0, min(1.0, current_impact * edge.weight))
                if propagated > impacts.get(edge.target, 0.0):
                    impacts[edge.target] = propagated
                    heappush(queue, (current_depth + 1, edge.target, propagated))
        return impacts

    def resilience_score(self, impacts: dict[str, float]) -> float:
        if not self.nodes:
            return 1.0
        weighted_load = 0.0
        for node_id, node in self.nodes.items():
            weighted_load += min(1.0, node.baseline_load + impacts.get(node_id, 0.0))
        return round(max(0.0, 1.0 - (weighted_load / len(self.nodes))), 4)

    def load_balancing_recommendation(self, impacts: dict[str, float], scope: JurisdictionScope) -> AdvisoryRecommendation:
        affected = [
            ConstraintImpact(
                constraint_id=node_id,
                category=self.nodes[node_id].category,
                weight=round(impact, 4),
                projected_delta=round(-impact * 0.25, 4),
                rationale="Reduce exposure by shifting non-critical load to less stressed capacity.",
            )
            for node_id, impact in sorted(impacts.items())
            if node_id in self.nodes and self.nodes[node_id].jurisdiction_id == scope.jurisdiction_id
        ]
        recommendation = AdvisoryRecommendation(
            title="Consider scoped load redistribution",
            rationale="Graph propagation indicates localized stress that may benefit from voluntary load balancing.",
            confidence=min(0.95, 0.5 + sum(item.weight for item in affected) / 10),
            affected_constraints=affected,
            projected_tradeoffs=[
                "May increase latency for non-critical flows.",
                "Requires human operator review and jurisdictional approval.",
            ],
            scope=scope,
            audit=AuditMetadata(actor_id="risk-engine"),
        )
        recommendation.validate_advisory_only()
        return recommendation
