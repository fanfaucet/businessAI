from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResponse:
    content: str
    latency_ms: int
    cost: float
    usage: dict[str, Any] = field(default_factory=dict)


class BaseRunner:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    async def chat(self, prompt: str) -> ModelResponse:
        raise NotImplementedError
