from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]

"""A chat message in the conversation."""


class ChatMessage(BaseModel):
    role: Role
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


"""The request body for a chat interaction."""


class ChatRequest(BaseModel):
    user_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=4000)


"""The response body for a chat interaction."""


class ChatResponse(BaseModel):
    request_id: str
    session_id: str
    answer: str
    model: str
    history_count: int


"""The response body for a model generation."""


class ModelResponse(BaseModel):
    content: str
    model: str


"""The response body for an error."""


class ErrorResponse(BaseModel):
    request_id: str
    error_code: str
    message: str
