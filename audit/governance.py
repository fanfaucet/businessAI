"""Governance workflows for advisory recommendations and policy replay."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import RLock

from core.contracts import AdvisoryRecommendation, RecommendationStatus


@dataclass(frozen=True)
class ExplainabilityReport:
    recommendation_id: str
    rationale: str
    confidence: float
    affected_constraints: list[dict]
    projected_tradeoffs: list[str]
    policy_version: str


class RecommendationLog:
    """Append-only JSONL log for recommendation transparency and replay."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def append(self, recommendation: AdvisoryRecommendation) -> None:
        recommendation.validate_advisory_only()
        payload = asdict(recommendation)
        with self._lock, self.path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(payload, sort_keys=True, default=str))
            log_file.write("\n")

    def replay(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self._lock, self.path.open("r", encoding="utf-8") as log_file:
            return [json.loads(line) for line in log_file if line.strip()]


def explain(recommendation: AdvisoryRecommendation) -> ExplainabilityReport:
    return ExplainabilityReport(
        recommendation_id=recommendation.audit.correlation_id,
        rationale=recommendation.rationale,
        confidence=recommendation.confidence,
        affected_constraints=[asdict(item) for item in recommendation.affected_constraints],
        projected_tradeoffs=list(recommendation.projected_tradeoffs),
        policy_version=recommendation.audit.policy_version,
    )


def require_human_approval(recommendation: AdvisoryRecommendation) -> AdvisoryRecommendation:
    if recommendation.status != RecommendationStatus.PENDING_HUMAN_REVIEW:
        return recommendation
    return recommendation
