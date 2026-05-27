import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from fastapi import FastAPI
from pydantic import BaseModel, Field


@dataclass
class Message:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0


class LLMClient(Protocol):
    def generate(self, messages: list[Message]) -> LLMResponse:
        ...


class FakeLLM:
    def generate(self, messages: list[Message]) -> LLMResponse:
        last_user_message = next(
            (message.content for message in reversed(messages) if message.role == "user"),
            "",
        )
        return LLMResponse(
            content=f"FakeLLM 收到：{last_user_message}",
            model="fake-llm",
            input_tokens=len(last_user_message),
            output_tokens=20,
        )


class ChatRequest(BaseModel):
    session_id: str = Field(default="default")
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str
    model: str
    latency_ms: int


app = FastAPI(title="Minimal LLM Service")
llm: LLMClient = FakeLLM()
conn = sqlite3.connect("messages.db", check_same_thread=False)


def init_db() -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def save_message(session_id: str, role: str, content: str) -> None:
    conn.execute(
        "INSERT INTO messages(session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.utcnow().isoformat()),
    )
    conn.commit()


def list_messages(session_id: str, limit: int = 10) -> list[Message]:
    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (session_id, limit),
    ).fetchall()
    return [Message(role=row[0], content=row[1]) for row in reversed(rows)]


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    start = time.time()
    save_message(req.session_id, "user", req.message)

    history = list_messages(req.session_id)
    response = llm.generate(history)

    save_message(req.session_id, "assistant", response.content)
    latency_ms = int((time.time() - start) * 1000)
    return ChatResponse(
        answer=response.content,
        model=response.model,
        latency_ms=latency_ms,
    )

