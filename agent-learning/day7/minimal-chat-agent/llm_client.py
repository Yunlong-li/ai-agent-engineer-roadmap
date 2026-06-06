from __future__ import annotations

import httpx

from config import Settings
from schemas import ChatMessage, ModelResponse

""""Define the fake LLM client if you don't have a real LLM provider"""


class FakeLLMClient:
    model = "fake-llm"

    async def generate(self, messages: list[ChatMessage]) -> ModelResponse:
        last_user_message = next(
            (msg.content for msg in reversed(messages) if msg.role == "user"), ""
        )
        return ModelResponse(
            model=self.model,
            content=(
                "这是 FakeLLM 回复：我已经收到你的消息。"
                f"你刚才说：{last_user_message}"
            ),
        )


"""Define the DeepSeek LLM client if you have a real LLM provider"""


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url.rstrip("/")
        self.chat_path = "/" + settings.deepseek_chat_path.strip("/")
        self.model = settings.deepseek_model
        self.timeout = settings.request_timeout_seconds

    async def generate(self, messages: list[ChatMessage]) -> ModelResponse:
        payload = {
            "model": self.model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
                if msg.role in {"system", "user", "assistant"}
            ],
            "temperature": 0.3,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Make the request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{self.chat_path}",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()  # Raise for any non-2xx status codes
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return ModelResponse(content=content, model=self.model)


"""Factory function to build the appropriate LLM client based on settings."""


def build_llm_client(settings: Settings):
    if settings.llm_provider == "deepseek" and settings.deepseek_api_key:
        return DeepSeekClient(settings)
    return FakeLLMClient()
