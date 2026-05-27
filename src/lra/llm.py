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

    def final(self, messages, output_model, max_tokens=max_tokens_config):
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=messages,
        )

        for block in resp.content:
            if block.type == "text":
                formatted = block.text.replace("```json","").replace("```","")
                return output_model.model_validate_json(formatted)
        raise ValueError("No text block in final response")