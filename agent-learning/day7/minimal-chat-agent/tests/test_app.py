from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app import create_app
from llm_client import FakeLLMClient
from memory import InMemorySessionStore


class AppTest(unittest.TestCase):
    def test_chat_endpoint(self) -> None:
        app = create_app(
            memory=InMemorySessionStore(),
            llm_client=FakeLLMClient(),
        )
        client = TestClient(app)
        response = client.post(
            "/chat",
            json={
                "user_id": "u001",
                "session_id": "api-test-session",
                "message": "帮我复盘 Day7 小项目",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], "api-test-session")
        self.assertEqual(data["model"], "fake-llm")
        self.assertGreaterEqual(data["history_count"], 2)
        self.assertTrue(data["request_id"])


if __name__ == "__main__":
    unittest.main()
