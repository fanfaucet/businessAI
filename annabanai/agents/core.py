"""Default AnnabanAI role agents."""

from __future__ import annotations

from annabanai.agents.base import AgentContext, AgentResult, BaseAgent


class PlannerAgent(BaseAgent):
    name = "planner"

    def run(self, context: AgentContext) -> AgentResult:
        priority = "support" if context.sentiment_label == "negative" else "build"
        return AgentResult(self.name, f"Plan priority: {priority}; preserve deterministic trace before expansion.")


class ReviewerAgent(BaseAgent):
    name = "reviewer"

    def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(self.name, "Review: check provider output, memory write, audit mirror, and user safety.")


class ExecutorAgent(BaseAgent):
    name = "executor"

    def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(self.name, "Execute: route prompt through ProviderRouter with fallback isolation.")


class AuditAgent(BaseAgent):
    name = "audit"

    def run(self, context: AgentContext) -> AgentResult:
        return AgentResult(self.name, f"Audit: correlation_id={context.correlation_id} requires SQLite + JSONL persistence.")


def default_registry():
    from annabanai.agents.base import SubagentRegistry

    registry = SubagentRegistry()
    registry.register(PlannerAgent())
    registry.register(ReviewerAgent())
    registry.register(ExecutorAgent())
    registry.register(AuditAgent())
    return registry
