from __future__ import annotations

import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.llm import FakeLLMClient
from app.schemas import ChatMessage


class FakeLLMTest(unittest.TestCase):
    def test_fake_llm_returns_structured_json_and_usage(self) -> None:
        result = asyncio.run(
            FakeLLMClient().generate([ChatMessage(role="user", content="复盘 Day14")])
        )

        payload = json.loads(result.content)
        self.assertEqual(result.model, "fake-llm")
        self.assertIn("summary", payload)
        self.assertGreater(result.usage.total_tokens, 0)


if __name__ == "__main__":
    unittest.main()
