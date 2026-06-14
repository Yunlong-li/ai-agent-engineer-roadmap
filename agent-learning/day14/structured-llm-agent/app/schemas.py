from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from app.core.telemetry import RequestMetrics, TokenUsage

Role = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: Role
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)
    prompt_template: str = "weekly_review"


class ReviewResult(BaseModel):
    """Review result for a user's learning input, based on a specific prompt template."""

    summary: str = Field(
        min_length=1
    )  # a one-sentence summary of the user's learning input
    learned: list[str] = Field(
        default_factory=list
    )  # a list of things the user learned
    gaps: list[str] = Field(
        default_factory=list
    )  # a list of gaps or weaknesses in the user's understanding
    next_steps: list[str] = Field(
        default_factory=list
    )  # a list of next steps or action items for the user to improve their learning


class LLMResult(BaseModel):
    content: str
    model: str
    usage: TokenUsage = Field(default_factory=TokenUsage)


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    answer: str
    model: str
    history_count: int
    review: ReviewResult | None = None
    metrics: RequestMetrics


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str
