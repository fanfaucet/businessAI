def governance_score(agreement: float, failure_rate: float, cost_per_task: float) -> float:
    score = (agreement * 0.6) + ((1 - failure_rate) * 0.3) + (max(0.0, 1 - cost_per_task) * 0.1)
    return round(score, 4)
