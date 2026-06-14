from __future__ import annotations

import json
from typing import Protocol

import httpx

from app.core.config import Settings
from app.core.telemetry import TokenUsage
from app.schemas import ChatMessage, LLMResult


class LLMClient(Protocol):
    async def generate(self, messages: list[ChatMessage]) -> LLMResult:
        ...


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def estimate_message_tokens(messages: list[ChatMessage]) -> int:
    return sum(estimate_tokens(message.content) for message in messages)


class FakeLLMClient:
    model = "fake-llm"

    async def generate(self, messages: list[ChatMessage]) -> LLMResult:
        last_user_message = next(
            (msg.content for msg in reversed(messages) if msg.role == "user"), ""
        )
        payload = {
            "summary": f"已收到你的复盘输入：{last_user_message}",
            "learned": ["统一 LLM 接口", "使用 prompt 模板", "校验 JSON 输出"],
            "gaps": ["真实模型成本需要按供应商价格配置"],
            "next_steps": ["接入真实模型后观察 token、成本和延迟指标"],
        }
        content = json.dumps(payload, ensure_ascii=False)
        usage = TokenUsage(
            prompt_tokens=estimate_message_tokens(messages),
            completion_tokens=estimate_tokens(content),
        )
        usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
        return LLMResult(content=content, model=self.model, usage=usage)


class DeepSeekClient:
    def __init__(self, settings: Settings) -> None:
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url.rstrip("/")
        self.chat_path = "/" + settings.deepseek_chat_path.strip("/")
        self.model = settings.deepseek_model
        self.timeout = settings.request_timeout_seconds

    async def generate(self, messages: list[ChatMessage]) -> LLMResult:
        payload = {
            "model": self.model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
                if msg.role in {"system", "user", "assistant"}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}{self.chat_path}",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        usage_data = data.get("usage") or {}
        prompt_tokens = int(usage_data.get("prompt_tokens") or 0)
        completion_tokens = int(usage_data.get("completion_tokens") or 0)
        total_tokens = int(
            usage_data.get("total_tokens") or prompt_tokens + completion_tokens
        )
        return LLMResult(
            content=content,
            model=self.model,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
        )


def build_llm_client(settings: Settings) -> LLMClient:
    if settings.llm_provider == "deepseek" and settings.deepseek_api_key:
        return DeepSeekClient(settings)
    return FakeLLMClient()
