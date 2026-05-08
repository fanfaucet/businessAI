"""Task orchestration utilities for subagent fanout and synthesis."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Iterable

from annabanai.agents.base import AgentContext, AgentResult, BaseAgent


@dataclass(frozen=True)
class TaskContract:
    """Explicit contract for a unit of orchestration work."""

    name: str
    role: str
    timeout_seconds: float = 10.0
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SynthesisResult:
    """Merged output from a fanout stage."""

    content: str
    results: list[AgentResult]


class ExecutionSandbox:
    """Lightweight boundary that constrains local task metadata before execution."""

    def validate(self, contract: TaskContract) -> None:
        if contract.timeout_seconds <= 0:
            raise ValueError("Task timeout must be positive")
        if not contract.name.strip():
            raise ValueError("Task name is required")


class TaskOrchestrator:
    """Run role agents sequentially or in parallel and synthesize their outputs."""

    def __init__(self, sandbox: ExecutionSandbox | None = None) -> None:
        self.sandbox = sandbox or ExecutionSandbox()

    def run_sequential(self, agents: Iterable[BaseAgent], context: AgentContext) -> SynthesisResult:
        results = [agent.run(context) for agent in agents]
        return self.synthesize(results)

    def run_parallel(self, agents: Iterable[BaseAgent], context: AgentContext, max_workers: int = 4) -> SynthesisResult:
        agent_list = list(agents)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(agent.run, context) for agent in agent_list]
            results = [future.result() for future in as_completed(futures)]
        return self.synthesize(sorted(results, key=lambda result: result.agent_name))

    def execute_contract(self, contract: TaskContract, fn: Callable[[], AgentResult]) -> AgentResult:
        self.sandbox.validate(contract)
        return fn()

    def synthesize(self, results: list[AgentResult]) -> SynthesisResult:
        content = "\n".join(f"[{result.agent_name}] {result.content}" for result in results)
        return SynthesisResult(content=content, results=results)
