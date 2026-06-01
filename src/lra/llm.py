from typing import Any
import anthropic
from anthropic.types import MessageParam, ToolParam
from pydantic import BaseModel
from src.lra.config import max_tokens as max_tokens_config

class LLMClient:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def call(self, messages: list[MessageParam], tools: list[ToolParam], max_tokens: int = max_tokens_config) -> anthropic.types.Message:
        return self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
            tools=tools
        )

    def final(self, messages: list[MessageParam], output_model: type[BaseModel], max_tokens: int = max_tokens_config) -> tuple[BaseModel, int, int]:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
        )

        for block in resp.content:
            if block.type == "text":
                formatted = block.text.replace("```json","").replace("```","")
                return (output_model.model_validate_json(formatted), resp.usage.input_tokens, resp.usage.output_tokens)
        raise ValueError("No text block in final response")