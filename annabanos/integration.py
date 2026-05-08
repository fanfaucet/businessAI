"""AnnabanAI automation bridge for AnnabanOS/AetherOS emulation."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from annabanai import AnnabanRuntime, RuntimeConfig
from annabanai.models.runtime import SentimentResult
from annabanai.sentiment.engine import SentimentEngine
from core.contracts import JurisdictionScope


class NeutralSentimentEngine(SentimentEngine):
    """Fast deterministic sentiment engine for local API emulation."""

    def analyze(self, text: str) -> SentimentResult:
        return SentimentResult(label="neutral", score=0.0, confidence=1.0, rolling_average=0.0, volatility=0.0)


class AnnabanAIAutomationBridge:
    """Run AnnabanAI automation in fallback mode and return advisory output."""

    def __init__(self, runtime: AnnabanRuntime | None = None) -> None:
        emulator_dir = Path(gettempdir()) / "annabanai_aetheros_emulator"
        emulator_dir.mkdir(parents=True, exist_ok=True)
        self.runtime = runtime or AnnabanRuntime(
            RuntimeConfig(
                db_path=str(emulator_dir / "state.db"),
                audit_path=str(emulator_dir / "audit.jsonl"),
                preferred_provider="fallback",
                fallback_provider="fallback",
            ),
            sentiment_engine=NeutralSentimentEngine(),
        )

    def process_payload(self, payload: dict[str, Any], scope: JurisdictionScope) -> dict[str, Any]:
        prompt = payload.get("prompt") or payload.get("description") or "Generate an advisory automation summary."
        result = self.runtime.process_input(
            prompt,
            user_id=payload.get("user_id", "aetheros-emulator"),
            provider_name="fallback",
            metadata={
                "surface": "aetheros-api-emulator",
                "jurisdiction_id": scope.jurisdiction_id,
                "visibility": scope.visibility.value,
                "advisory_only": True,
            },
        )
        return {
            "correlation_id": result.correlation_id,
            "response": result.response,
            "sentiment": asdict(result.sentiment),
            "provider": asdict(result.provider_response),
            "advisory_only": True,
            "dry_run": True,
        }
