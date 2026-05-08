"""Central AnnabanAI orchestration runtime spine."""

from __future__ import annotations

import logging
from dataclasses import asdict
from threading import RLock
from typing import Any
from uuid import uuid4

from annabanai.agents.base import AgentContext, SubagentRegistry
from annabanai.agents.core import default_registry
from annabanai.audit.manager import AuditManager
from annabanai.memory.backends import MemoryBackend
from annabanai.memory.manager import MemoryManager
from annabanai.models.runtime import (
    EventType,
    InteractionRecord,
    ProviderRequest,
    RuntimeConfig,
    RuntimeEvent,
    RuntimeResult,
    utc_now_iso,
)
from annabanai.orchestration.tasks import TaskOrchestrator
from annabanai.providers.router import ProviderRouter
from annabanai.sentiment.engine import SentimentEngine
from annabanai.telemetry.metrics import Telemetry, Timer

LOGGER = logging.getLogger("annabanai.runtime")


SYSTEM_PROMPT = """
You are AnnabanAI Companion, an empathetic AI guided by the AnnabanAI Covenant.
Prioritize reliability, transparent reasoning summaries, user safety, and deterministic persistence.
""".strip()


class AnnabanRuntime:
    """Production-oriented runtime coordinating providers, memory, audit, sentiment, and agents."""

    def __init__(
        self,
        config: RuntimeConfig | None = None,
        *,
        provider_router: ProviderRouter | None = None,
        memory_manager: MemoryBackend | None = None,
        audit_manager: AuditManager | None = None,
        sentiment_engine: SentimentEngine | None = None,
        telemetry: Telemetry | None = None,
        agents: SubagentRegistry | None = None,
    ) -> None:
        self.config = config or RuntimeConfig()
        self.telemetry = telemetry or Telemetry()
        self.provider_router = provider_router or ProviderRouter(self.config, self.telemetry)
        self.memory_manager = memory_manager or MemoryManager(self.config)
        self.audit_manager = audit_manager or AuditManager(self.config.audit_path)
        self.sentiment_engine = sentiment_engine or SentimentEngine()
        self.agents = agents or default_registry()
        self.task_orchestrator = TaskOrchestrator()
        self._lock = RLock()
        self._sequence = 0

    def _next_sequence(self) -> int:
        self._sequence += 1
        return self._sequence

    def _event(self, correlation_id: str, event_type: EventType, payload: dict[str, Any] | None = None) -> RuntimeEvent:
        event = RuntimeEvent(
            sequence=self._next_sequence(),
            correlation_id=correlation_id,
            event_type=event_type,
            timestamp=utc_now_iso(),
            payload=payload or {},
        )
        LOGGER.info(
            "annabanai_event",
            extra={
                "correlation_id": correlation_id,
                "sequence": event.sequence,
                "event_type": event_type.value,
            },
        )
        return event

    def process_input(
        self,
        user_text: str,
        *,
        user_id: str = "default",
        provider_name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RuntimeResult:
        """Run the deterministic request lifecycle and persist every interaction."""
        correlation_id = str(uuid4())
        metadata = metadata or {}
        events: list[RuntimeEvent] = []

        with self._lock, Timer() as timer:
            try:
                self.telemetry.increment("runtime.requests")
                events.append(self._event(correlation_id, EventType.REQUEST_RECEIVED, {"user_id": user_id}))

                sentiment = self.sentiment_engine.analyze(user_text)
                events.append(self._event(correlation_id, EventType.SENTIMENT_ANALYZED, asdict(sentiment)))

                agent_context = AgentContext(correlation_id, user_text, sentiment.label, metadata)
                synthesis = self.task_orchestrator.run_sequential(self.agents.values(), agent_context)
                agent_results = synthesis.results
                events.append(
                    self._event(
                        correlation_id,
                        EventType.AGENTS_COMPLETED,
                        {"agents": [asdict(result) for result in agent_results]},
                    )
                )

                orchestration_context = "\n".join(result.content for result in agent_results)
                provider_request = ProviderRequest(
                    prompt=f"{user_text}\n\nOrchestration context:\n{orchestration_context}",
                    system_prompt=SYSTEM_PROMPT,
                    correlation_id=correlation_id,
                    metadata=metadata,
                )
                provider_response = self.provider_router.infer(provider_request, provider_name)
                events.append(self._event(correlation_id, EventType.PROVIDER_COMPLETED, asdict(provider_response)))

                audit_seed = {
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                    "user_input": user_text,
                    "ai_output": provider_response.text,
                    "sentiment": asdict(sentiment),
                    "provider": provider_response.provider,
                    "metadata": metadata,
                }
                audit_hash = self.audit_manager.compute_hash(audit_seed)
                record = InteractionRecord(
                    correlation_id=correlation_id,
                    timestamp=utc_now_iso(),
                    user_id=user_id,
                    user_input=user_text,
                    ai_output=provider_response.text,
                    sentiment=sentiment,
                    provider=provider_response.provider,
                    metadata={**metadata, "agent_results": [asdict(result) for result in agent_results]},
                    audit_hash=audit_hash,
                )
                events.append(self._event(correlation_id, EventType.MEMORY_COMMITTED, {"audit_hash": audit_hash}))
                self.memory_manager.store_interaction(record, events)
                events.append(self._event(correlation_id, EventType.AUDIT_MIRRORED, {"audit_path": self.config.audit_path}))
                self.audit_manager.mirror(record, events)
                self.telemetry.increment("runtime.success")
                self.telemetry.observe_latency("runtime.process_input_ms", timer.current_ms())
                return RuntimeResult(
                    correlation_id=correlation_id,
                    response=provider_response.text,
                    sentiment=sentiment,
                    provider_response=provider_response,
                    events=events,
                    telemetry=self.telemetry.snapshot(),
                )
            except Exception as exc:
                self.telemetry.increment("runtime.failure")
                self.telemetry.record_error(type(exc).__name__)
                events.append(self._event(correlation_id, EventType.REQUEST_FAILED, {"error": str(exc)}))
                LOGGER.exception("annabanai_runtime_failure", extra={"correlation_id": correlation_id})
                raise

    def health(self) -> dict[str, Any]:
        """Return runtime health, storage integrity, and telemetry snapshots."""
        return {
            "memory": self.memory_manager.verify_integrity(),
            "telemetry": self.telemetry.snapshot(),
            "audit_chain": self.audit_manager.verify_chain(),
            "agents": self.agents.names(),
        }
