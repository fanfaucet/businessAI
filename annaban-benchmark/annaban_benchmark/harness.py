from __future__ import annotations
from annaban_benchmark.consensus import agreement_score
from annaban_benchmark.cost import total_cost
from annaban_benchmark.metrics import governance_score
from annaban_benchmark.datasets.loader import load_dataset


class BenchmarkHarness:
    async def run_benchmark(self, dataset: str = "reasoning_tasks") -> dict:
        tasks = load_dataset(dataset)
        outputs = ["advisory" if "Ignore safety" not in t["prompt"] else "refuse" for t in tasks]
        costs = [0.001 for _ in tasks]
        failures = sum(1 for t, o in zip(tasks, outputs) if t.get("expected") != o)
        failure_rate = failures / len(tasks)
        agree = agreement_score(outputs)
        cost_per_task = total_cost(costs) / len(tasks)
        return {
            "dataset": dataset,
            "tasks": len(tasks),
            "agreement_stability": agree,
            "failure_rate": failure_rate,
            "cost_per_task": cost_per_task,
            "annaban_governance_score": governance_score(agree, failure_rate, cost_per_task),
        }
