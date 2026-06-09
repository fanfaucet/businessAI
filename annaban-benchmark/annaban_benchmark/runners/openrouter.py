import os, httpx
from .base import BaseRunner, ModelResponse

class OpenRouterRunner(BaseRunner):
    def __init__(self, model="openai/gpt-4o-mini"):
        super().__init__("openrouter")
        self.api_key=os.getenv("OPENROUTER_API_KEY")
        self.model=model
    async def chat(self, prompt: str) -> ModelResponse:
        async with httpx.AsyncClient() as client:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization":f"Bearer {self.api_key}"}, json={"model":self.model,"messages":[{"role":"user","content":prompt}]})
        data=r.json()
        return ModelResponse(content=data["choices"][0]["message"]["content"], latency_ms=0, cost=float(data.get("usage",{}).get("cost",0.001)), usage=data.get("usage",{}))
