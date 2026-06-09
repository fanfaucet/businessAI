from __future__ import annotations
from annaban_benchmark.kubernetes.templates import JOB_TEMPLATE


class K8sGenerator:
    def generate(self, result: dict) -> str:
        return JOB_TEMPLATE.format(annaban_governance_score=result.get("annaban_governance_score", 0))
