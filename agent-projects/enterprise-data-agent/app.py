from __future__ import annotations

from fastapi import FastAPI

from agent.orchestrator import BusinessAnalysisAgent
from agent.schemas import AgentAnswer, ChatRequest

app = FastAPI(title="Enterprise Data Analysis Agent")
agent = BusinessAnalysisAgent()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sample-questions")
def sample_questions() -> list[str]:
    return [
        "最近 30 天 GMV 为什么下滑？",
        "按渠道拆解最近 30 天 GMV 变化",
        "活动规则和退款口径会影响 GMV 分析吗？",
    ]


@app.post("/chat", response_model=AgentAnswer)
def chat(req: ChatRequest) -> AgentAnswer:
    return agent.answer(req)
