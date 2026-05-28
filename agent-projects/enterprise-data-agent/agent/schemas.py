from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, examples=["最近 30 天 GMV 为什么下滑？"])
    user_id: str = "demo-user"


class PlanStep(BaseModel):
    name: str
    tool: str
    reason: str


class ToolResult(BaseModel):
    ok: bool
    tool: str
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: str | None = None
    message: str = ""


class Evidence(BaseModel):
    type: Literal["sql", "doc", "analysis"]
    source: str
    content: str


class TraceStep(BaseModel):
    step: str
    tool: str
    ok: bool
    summary: str


class AgentAnswer(BaseModel):
    question: str
    answer: str
    findings: list[str]
    recommendations: list[str]
    evidence: list[Evidence]
    trace: list[TraceStep]
