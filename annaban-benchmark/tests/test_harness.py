import asyncio
from annaban_benchmark.harness import BenchmarkHarness


def test_harness_runs():
    result = asyncio.run(BenchmarkHarness().run_benchmark())
    assert result["tasks"] >= 1
    assert "annaban_governance_score" in result
