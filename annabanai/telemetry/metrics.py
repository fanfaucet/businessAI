"""Thread-safe in-process telemetry for AnnabanAI."""

from __future__ import annotations

from collections import defaultdict
from threading import Lock
from time import perf_counter
from typing import Any


class Telemetry:
    """Collect runtime counters, latencies, and provider health snapshots."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._latencies: dict[str, list[float]] = defaultdict(list)
        self._errors: dict[str, int] = defaultdict(int)
        self._provider_health: dict[str, dict[str, Any]] = {}

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe_latency(self, name: str, latency_ms: float) -> None:
        with self._lock:
            self._latencies[name].append(latency_ms)

    def record_error(self, category: str) -> None:
        with self._lock:
            self._errors[category] += 1

    def set_provider_health(self, provider: str, *, healthy: bool, latency_ms: float, error: str | None = None) -> None:
        with self._lock:
            self._provider_health[provider] = {
                "healthy": healthy,
                "latency_ms": round(latency_ms, 3),
                "error": error,
            }

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            latency_summary = {}
            for name, values in self._latencies.items():
                latency_summary[name] = {
                    "count": len(values),
                    "avg_ms": round(sum(values) / len(values), 3) if values else 0.0,
                    "max_ms": round(max(values), 3) if values else 0.0,
                }
            return {
                "counters": dict(self._counters),
                "latencies": latency_summary,
                "errors": dict(self._errors),
                "provider_health": dict(self._provider_health),
            }

    def prometheus_text(self) -> str:
        snapshot = self.snapshot()
        lines = []
        for key, value in snapshot["counters"].items():
            lines.append(f'annabanai_counter{{name="{key}"}} {value}')
        for key, value in snapshot["errors"].items():
            lines.append(f'annabanai_errors{{category="{key}"}} {value}')
        for key, summary in snapshot["latencies"].items():
            lines.append(f'annabanai_latency_avg_ms{{name="{key}"}} {summary["avg_ms"]}')
        return "\n".join(lines)


class Timer:
    """Context manager for measuring execution timing."""

    def __enter__(self) -> "Timer":
        self.started = perf_counter()
        self.elapsed_ms = 0.0
        return self

    def current_ms(self) -> float:
        return (perf_counter() - self.started) * 1000

    def __exit__(self, exc_type, exc, traceback) -> None:  # noqa: ANN001
        self.elapsed_ms = self.current_ms()
