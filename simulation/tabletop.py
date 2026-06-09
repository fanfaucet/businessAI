"""Deterministic tabletop simulation framework for federated resilience planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ScenarioType(str, Enum):
    PORT_CLOSURE = "port_closure"
    FUEL_SHOCK = "fuel_shock"
    HEALTHCARE_CRISIS = "healthcare_crisis"
    SUPPLY_CHAIN_DISRUPTION = "supply_chain_disruption"
    GEOPOLITICAL_EVENT = "geopolitical_event"


@dataclass(frozen=True)
class SimulationEvent:
    event_type: ScenarioType
    target_id: str
    severity: float
    duration_hours: int
    description: str


@dataclass(frozen=True)
class SimulationResult:
    scenario_id: str
    cascading_delay_hours: float
    infrastructure_saturation: float
    resilience_score: float
    confidence: float
    notes: list[str] = field(default_factory=list)
    simulation_only: bool = True


class TabletopSimulationEngine:
    def run(self, scenario_id: str, events: list[SimulationEvent]) -> SimulationResult:
        if not events:
            return SimulationResult(scenario_id, 0.0, 0.0, 1.0, 0.95, ["No events supplied."])
        severity_load = sum(max(0.0, min(1.0, event.severity)) for event in events)
        duration_load = sum(max(1, event.duration_hours) for event in events) / 24
        cascading_delay = round(severity_load * duration_load * 6, 2)
        saturation = round(min(1.0, severity_load / max(1, len(events)) + duration_load / 100), 4)
        resilience = round(max(0.0, 1.0 - saturation), 4)
        confidence = round(max(0.25, min(0.9, 0.9 - 0.03 * len(events))), 4)
        notes = [f"Synthetic {event.event_type.value} at {event.target_id}: {event.description}" for event in events]
        return SimulationResult(scenario_id, cascading_delay, saturation, resilience, confidence, notes)
