from __future__ import annotations

import unittest

from agent.orchestrator import BusinessAnalysisAgent
from agent.schemas import ChatRequest


class BusinessAnalysisAgentTest(unittest.TestCase):
    def test_agent_returns_findings_evidence_and_trace(self) -> None:
        agent = BusinessAnalysisAgent()
        answer = agent.answer(ChatRequest(question="最近 30 天 GMV 为什么下滑？"))

        self.assertGreaterEqual(len(answer.findings), 3)
        self.assertGreaterEqual(len(answer.recommendations), 3)
        self.assertTrue(any(item.type == "sql" for item in answer.evidence))
        self.assertTrue(any(item.type == "doc" for item in answer.evidence))
        self.assertGreaterEqual(len(answer.trace), 5)


if __name__ == "__main__":
    unittest.main()
