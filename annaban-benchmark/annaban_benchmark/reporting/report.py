from __future__ import annotations


def build_markdown_report(result: dict) -> str:
    return "\n".join(
        [
            "# Annaban Benchmark Report",
            f"- Agreement Stability: {result.get('agreement_stability')}",
            f"- Failure Rate: {result.get('failure_rate')}",
            f"- Cost Per Task: {result.get('cost_per_task')}",
            f"- Governance Score: {result.get('annaban_governance_score')}",
        ]
    )
