from __future__ import annotations
from annaban_benchmark.runners.openai import OpenAIRunner
from annaban_benchmark.runners.anthropic import AnthropicRunner
from annaban_benchmark.runners.gemini import GeminiRunner
from annaban_benchmark.runners.grok import GrokRunner
from annaban_benchmark.runners.openrouter import OpenRouterRunner


def select_runner(name: str):
    normalized = name.lower().strip()
    mapping = {
        "openai": OpenAIRunner,
        "gpt": OpenAIRunner,
        "anthropic": AnthropicRunner,
        "claude": AnthropicRunner,
        "gemini": GeminiRunner,
        "grok": GrokRunner,
        "openrouter": OpenRouterRunner,
    }
    if normalized not in mapping:
        raise ValueError(f"Unsupported runner: {name}")
    return mapping[normalized]()
