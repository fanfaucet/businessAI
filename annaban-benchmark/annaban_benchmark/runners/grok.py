from .base import BaseRunner, ModelResponse


class GrokRunner(BaseRunner):
    def __init__(self):
        super().__init__("grok")

    async def chat(self, prompt: str) -> ModelResponse:
        return ModelResponse(content=f"[grok simulated] {prompt}", latency_ms=1, cost=0.0018, usage={"simulated": True})
