from .base import BaseRunner, ModelResponse


class GeminiRunner(BaseRunner):
    def __init__(self):
        super().__init__("gemini")

    async def chat(self, prompt: str) -> ModelResponse:
        return ModelResponse(content=f"[gemini simulated] {prompt}", latency_ms=1, cost=0.0015, usage={"simulated": True})
