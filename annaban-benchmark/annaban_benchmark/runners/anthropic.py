import os
from anthropic import AsyncAnthropic
from .base import BaseRunner, ModelResponse

class AnthropicRunner(BaseRunner):
    def __init__(self):
        super().__init__("claude")
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    async def chat(self, prompt: str) -> ModelResponse:
        resp = await self.client.messages.create(model="claude-3-5-sonnet-latest", max_tokens=1024, messages=[{"role":"user","content":prompt}])
        return ModelResponse(content=resp.content[0].text, latency_ms=0, cost=0.004, usage={"cost":0.004})
