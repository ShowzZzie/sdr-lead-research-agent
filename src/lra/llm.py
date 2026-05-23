import anthropic
from src.lra.config import max_tokens as max_tokens_config

class LLMClient:
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def call(self, messages, tools, max_tokens=max_tokens_config):
        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools
        )