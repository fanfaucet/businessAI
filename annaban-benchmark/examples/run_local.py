import asyncio
from annaban_benchmark.harness import BenchmarkHarness

print(asyncio.run(BenchmarkHarness().run_benchmark()))
