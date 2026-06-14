from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.agent.memory import InMemorySessionStore
from app.core.telemetry import InMemoryTraceStore
from app.llm import FakeLLMClient
from app.main import create_app


class AppTest(unittest.TestCase):
    def test_chat_endpoint_returns_metrics_and_review(self) -> None:
        app = create_app(
            memory=InMemorySessionStore(),
            llm_client=FakeLLMClient(),
            trace_store=InMemoryTraceStore(),
        )
        client = TestClient(app)

        response = client.post(
            "/chat",
            json={
                "user_id": "u001",
                "session_id": "api-test-session",
                "message": "帮我复盘 Day14 小项目",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["session_id"], "api-test-session")
        self.assertEqual(data["model"], "fake-llm")
        self.assertTrue(data["metrics"]["validation_ok"])
        self.assertIn("summary", data["review"])

    def test_prompts_endpoint(self) -> None:
        app = create_app(llm_client=FakeLLMClient())
        client = TestClient(app)

        response = client.get("/prompts")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 1)


if __name__ == "__main__":
    unittest.main()
