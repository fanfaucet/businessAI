import os
from openai import AsyncOpenAI
from .base import BaseRunner, ModelResponse

class OpenAIRunner(BaseRunner):
    def __init__(self):
        super().__init__("gpt")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    async def chat(self, prompt: str) -> ModelResponse:
        resp = await self.client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
        return ModelResponse(content=resp.choices[0].message.content or "", latency_ms=0, cost=0.002, usage={"cost":0.002})
