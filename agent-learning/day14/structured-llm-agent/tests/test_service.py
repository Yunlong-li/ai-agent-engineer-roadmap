from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.memory import InMemorySessionStore
from app.agent.service import StructuredChatAgent
from app.core.config import Settings
from app.core.telemetry import InMemoryTraceStore
from app.llm import FakeLLMClient
from app.prompts import build_prompt_registry
from app.schemas import ChatRequest, ChatMessage, LLMResult


def build_test_settings() -> Settings:
    return Settings(
        llm_provider="deepseek",
        deepseek_api_key="",
        deepseek_base_url="https://api.deepseek.com",
        deepseek_chat_path="/v1/chat/completions",
        deepseek_model="deepseek-v4-flash",
        request_timeout_seconds=3,
        max_history_messages=12,
        max_in_memory_sessions=100,
        session_ttl_seconds=3600,
        log_level="INFO",
        input_token_price_per_1m=1.0,
        output_token_price_per_1m=2.0,
        trace_buffer_size=20,
    )


class InvalidJSONClient:
    async def generate(self, messages: list[ChatMessage]) -> LLMResult:
        return LLMResult(content="not json", model="invalid-json-model")


class StructuredChatAgentTest(unittest.TestCase):
    def test_chat_validates_json_and_records_trace(self) -> None:
        trace_store = InMemoryTraceStore()
        agent = StructuredChatAgent(
            settings=build_test_settings(),
            memory=InMemorySessionStore(),
            llm_client=FakeLLMClient(),
            prompt_registry=build_prompt_registry(),
            trace_store=trace_store,
        )

        response = asyncio.run(
            agent.chat(
                ChatRequest(
                    user_id="u001",
                    session_id="s001",
                    message="我完成了 Day14 结构化 LLM 服务",
                )
            )
        )

        self.assertEqual(response.model, "fake-llm")
        self.assertTrue(response.metrics.validation_ok)
        self.assertIsNotNone(response.review)
        self.assertEqual(response.history_count, 2)
        self.assertEqual(len(trace_store.list_events()), 1)

    def test_invalid_json_is_reported_in_metrics(self) -> None:
        agent = StructuredChatAgent(
            settings=build_test_settings(),
            memory=InMemorySessionStore(),
            llm_client=InvalidJSONClient(),
            prompt_registry=build_prompt_registry(),
            trace_store=InMemoryTraceStore(),
        )

        response = asyncio.run(
            agent.chat(
                ChatRequest(
                    user_id="u001",
                    session_id="s001",
                    message="返回非 JSON",
                )
            )
        )

        self.assertFalse(response.metrics.validation_ok)
        self.assertIsNone(response.review)
        self.assertEqual(response.answer, "not json")


if __name__ == "__main__":
    unittest.main()
