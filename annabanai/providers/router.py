"""Provider abstraction and retry-aware routing for AnnabanAI."""

from __future__ import annotations

import importlib
import os
from abc import ABC, abstractmethod
from time import perf_counter, sleep

from annabanai.models.runtime import ProviderRequest, ProviderResponse, RuntimeConfig
from annabanai.telemetry.metrics import Telemetry


class BaseProvider(ABC):
    """Inference provider contract."""

    name = "base"
    model = "unknown"

    @abstractmethod
    def infer(self, request: ProviderRequest, timeout_seconds: float) -> ProviderResponse:
        """Return a normalized provider response."""


class FallbackProvider(BaseProvider):
    """Deterministic local provider used for graceful degradation and tests."""

    name = "fallback"
    model = "local-deterministic-fallback"

    def infer(self, request: ProviderRequest, timeout_seconds: float) -> ProviderResponse:
        started = perf_counter()
        text = (
            "AnnabanAI local fallback response: "
            f"received {len(request.prompt.split())} words. "
            "Provider routing is degraded but the runtime remains available."
        )
        latency_ms = (perf_counter() - started) * 1000
        return ProviderResponse(
            text=text,
            provider=self.name,
            model=self.model,
            latency_ms=latency_ms,
            input_tokens=len(request.prompt.split()),
            output_tokens=len(text.split()),
            total_tokens=len(request.prompt.split()) + len(text.split()),
            degraded=True,
        )


class OpenAICompatibleProvider(BaseProvider):
    """OpenAI SDK based provider that also supports xAI's OpenAI-compatible API."""

    def __init__(self, *, name: str, api_key_env: str, base_url: str | None, model: str) -> None:
        self.name = name
        self.api_key_env = api_key_env
        self.base_url = base_url
        self.model = model

    def infer(self, request: ProviderRequest, timeout_seconds: float) -> ProviderResponse:
        started = perf_counter()
        openai_module = importlib.import_module("openai")
        client_kwargs = {"api_key": os.getenv(self.api_key_env), "timeout": timeout_seconds}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = openai_module.OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        usage = response.usage.to_dict() if getattr(response, "usage", None) else {}
        latency_ms = (perf_counter() - started) * 1000
        return ProviderResponse(
            text=response.choices[0].message.content or "",
            provider=self.name,
            model=response.model or self.model,
            latency_ms=latency_ms,
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
            metadata={"response_id": getattr(response, "id", None)},
        )


class ProviderRouter:
    """Route requests across OpenAI, xAI, and deterministic fallback providers."""

    def __init__(self, config: RuntimeConfig, telemetry: Telemetry | None = None) -> None:
        self.config = config
        self.telemetry = telemetry or Telemetry()
        self.providers: dict[str, BaseProvider] = {
            "fallback": FallbackProvider(),
            "openai": OpenAICompatibleProvider(
                name="openai",
                api_key_env="OPENAI_API_KEY",
                base_url=None,
                model=os.getenv("ANNABANAI_OPENAI_MODEL", "gpt-4o-mini"),
            ),
            "xai": OpenAICompatibleProvider(
                name="xai",
                api_key_env="XAI_API_KEY",
                base_url="https://api.x.ai/v1",
                model=os.getenv("ANNABANAI_XAI_MODEL", "grok-3"),
            ),
        }

    def infer(self, request: ProviderRequest, provider_name: str | None = None) -> ProviderResponse:
        requested_provider = provider_name or self.config.preferred_provider
        ordered_providers = [requested_provider]
        if self.config.fallback_provider not in ordered_providers:
            ordered_providers.append(self.config.fallback_provider)
        if "fallback" not in ordered_providers:
            ordered_providers.append("fallback")

        last_error: str | None = None
        for candidate in ordered_providers:
            provider = self.providers.get(candidate, self.providers["fallback"])
            attempts = 1 if provider.name == "fallback" else max(1, self.config.max_retries + 1)
            for attempt in range(attempts):
                started = perf_counter()
                try:
                    response = provider.infer(request, self.config.request_timeout_seconds)
                    self.telemetry.increment(f"provider.{provider.name}.success")
                    self.telemetry.observe_latency(f"provider.{provider.name}.latency_ms", response.latency_ms)
                    self.telemetry.set_provider_health(provider.name, healthy=True, latency_ms=response.latency_ms)
                    if last_error and response.error is None:
                        response = ProviderResponse(**{**response.__dict__, "metadata": {**response.metadata, "previous_error": last_error}})
                    return response
                except Exception as exc:  # Provider isolation boundary: keep orchestration alive.
                    latency_ms = (perf_counter() - started) * 1000
                    last_error = f"{provider.name}: {exc}"
                    self.telemetry.increment(f"provider.{provider.name}.failure")
                    self.telemetry.record_error("provider_failure")
                    self.telemetry.set_provider_health(provider.name, healthy=False, latency_ms=latency_ms, error=str(exc))
                    if attempt < attempts - 1:
                        sleep(min(0.25 * (attempt + 1), 1.0))

        fallback = self.providers["fallback"].infer(request, self.config.request_timeout_seconds)
        return ProviderResponse(**{**fallback.__dict__, "error": last_error, "degraded": True})
