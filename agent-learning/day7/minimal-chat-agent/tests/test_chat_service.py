from __future__ import annotations

import asyncio
import unittest

from config import Settings
from llm_client import FakeLLMClient
from memory import InMemorySessionStore
from schemas import ChatRequest
from service import ChatService


class ChatServiceTest(unittest.TestCase):
    def test_chat_uses_fake_llm_and_saves_history(self) -> None:
        settings = Settings(
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
        )
        memory = InMemorySessionStore(
            max_messages=settings.max_history_messages,
            max_sessions=settings.max_in_memory_sessions,
            ttl_seconds=settings.session_ttl_seconds,
        )
        service = ChatService(settings=settings, memory=memory, llm_client=FakeLLMClient())

        response = asyncio.run(
            service.chat(
                ChatRequest(
                    user_id="u001",
                    session_id="s001",
                    message="我今天学了 FastAPI",
                )
            )
        )

        self.assertEqual(response.model, "fake-llm")
        self.assertEqual(response.history_count, 2)
        self.assertIn("FastAPI", response.answer)
        self.assertEqual(len(memory.list_messages("s001")), 2)

    def test_memory_limits_each_session_history(self) -> None:
        memory = InMemorySessionStore(max_messages=2)

        memory.append("s001", "user", "first")
        memory.append("s001", "assistant", "second")
        memory.append("s001", "user", "third")

        messages = memory.list_messages("s001")
        self.assertEqual([msg.content for msg in messages], ["second", "third"])

    def test_memory_evicts_oldest_session_when_full(self) -> None:
        memory = InMemorySessionStore(max_sessions=2)

        memory.append("s001", "user", "first")
        memory.append("s002", "user", "second")
        memory.append("s003", "user", "third")

        self.assertEqual(memory.list_messages("s001"), [])
        self.assertEqual(len(memory.list_messages("s002")), 1)
        self.assertEqual(len(memory.list_messages("s003")), 1)


if __name__ == "__main__":
    unittest.main()
