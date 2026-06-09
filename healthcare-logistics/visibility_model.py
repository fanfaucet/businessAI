"""Aggregate-only healthcare logistics visibility model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthcareSupplySignal:
    jurisdiction_id: str
    facility_group: str
    item_class: str
    days_on_hand: float
    demand_growth_rate: float
    transport_capacity_index: float


def stress_score(signal: HealthcareSupplySignal) -> float:
    inventory_pressure = max(0.0, min(1.0, (14 - signal.days_on_hand) / 14))
    demand_pressure = max(0.0, min(1.0, signal.demand_growth_rate))
    transport_pressure = max(0.0, min(1.0, 1 - signal.transport_capacity_index))
    return round(0.5 * inventory_pressure + 0.3 * demand_pressure + 0.2 * transport_pressure, 4)
