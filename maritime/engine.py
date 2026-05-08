"""Conceptual maritime logistics analytics with explainable outputs."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from core.contracts import AdvisoryRecommendation, AuditMetadata, ConstraintImpact, JurisdictionScope


@dataclass(frozen=True)
class VesselSignal:
    vessel_id: str
    port_id: str
    speed_knots: float
    dwell_hours: float
    manifest_complexity: float


@dataclass(frozen=True)
class WeatherOverlay:
    port_id: str
    disruption_index: float


@dataclass(frozen=True)
class PortTelemetry:
    port_id: str
    berth_utilization: float
    customs_backlog: float
    jurisdiction_id: str


@dataclass(frozen=True)
class MaritimeRiskMap:
    port_id: str
    congestion_probability: float
    weather_disruption_probability: float
    customs_friction_probability: float
    confidence_interval: tuple[float, float]


class MaritimeLogisticsEngine:
    def forecast_congestion(
        self,
        vessels: list[VesselSignal],
        weather: list[WeatherOverlay],
        telemetry: list[PortTelemetry],
    ) -> list[MaritimeRiskMap]:
        weather_by_port = {item.port_id: item for item in weather}
        vessels_by_port: dict[str, list[VesselSignal]] = {}
        for vessel in vessels:
            vessels_by_port.setdefault(vessel.port_id, []).append(vessel)

        maps: list[MaritimeRiskMap] = []
        for port in telemetry:
            port_vessels = vessels_by_port.get(port.port_id, [])
            dwell_pressure = mean([v.dwell_hours for v in port_vessels]) / 72 if port_vessels else 0.0
            manifest_pressure = mean([v.manifest_complexity for v in port_vessels]) if port_vessels else 0.0
            weather_index = weather_by_port.get(port.port_id, WeatherOverlay(port.port_id, 0.0)).disruption_index
            congestion = min(1.0, 0.5 * port.berth_utilization + 0.3 * dwell_pressure + 0.2 * weather_index)
            customs = min(1.0, 0.65 * port.customs_backlog + 0.35 * manifest_pressure)
            confidence = max(0.1, min(0.9, 0.35 + 0.1 * len(port_vessels)))
            spread = round((1 - confidence) / 2, 4)
            maps.append(
                MaritimeRiskMap(
                    port_id=port.port_id,
                    congestion_probability=round(congestion, 4),
                    weather_disruption_probability=round(weather_index, 4),
                    customs_friction_probability=round(customs, 4),
                    confidence_interval=(max(0.0, round(congestion - spread, 4)), min(1.0, round(congestion + spread, 4))),
                )
            )
        return maps

    def advisory_rerouting(self, risk: MaritimeRiskMap, scope: JurisdictionScope) -> AdvisoryRecommendation:
        recommendation = AdvisoryRecommendation(
            title=f"Review voluntary routing alternatives near {risk.port_id}",
            rationale="Congestion and disruption signals exceed normal planning thresholds; alternatives should be reviewed by operators.",
            confidence=max(risk.congestion_probability, risk.weather_disruption_probability, risk.customs_friction_probability),
            affected_constraints=[
                ConstraintImpact("port_congestion", "maritime", risk.congestion_probability, -0.15, "Lower berth pressure if voluntary alternatives are approved."),
                ConstraintImpact("customs_friction", "trade", risk.customs_friction_probability, -0.05, "Adjust documentation sequencing where legally permitted."),
            ],
            projected_tradeoffs=["Possible longer transit distance.", "Requires carrier and port authority approval."],
            scope=scope,
            audit=AuditMetadata(actor_id="maritime-engine"),
        )
        recommendation.validate_advisory_only()
        return recommendation
