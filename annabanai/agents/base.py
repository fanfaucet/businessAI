"""Subagent contracts and deterministic registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentContext:
    """Context passed to orchestration subagents."""

    correlation_id: str
    user_input: str
    sentiment_label: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    """Normalized output from a subagent."""

    agent_name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base contract for all role-oriented agents."""

    name = "base"

    @abstractmethod
    def run(self, context: AgentContext) -> AgentResult:
        """Execute deterministic local agent logic."""


class SubagentRegistry:
    """Register and route deterministic local subagents."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent:
        return self._agents[name]

    def values(self) -> list[BaseAgent]:
        return [agent for _, agent in sorted(self._agents.items())]

    def run_all(self, context: AgentContext) -> list[AgentResult]:
        return [agent.run(context) for agent in self.values()]

    def names(self) -> list[str]:
        return sorted(self._agents)
