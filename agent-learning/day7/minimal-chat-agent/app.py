from __future__ import annotations

import logging

from fastapi import FastAPI

from config import get_settings
from llm_client import build_llm_client
from memory import InMemorySessionStore
from schemas import ChatMessage, ChatRequest, ChatResponse
from service import ChatService

"""The main application module for the minimal chat agent."""


def create_app(
    memory: InMemorySessionStore | None = None,
    llm_client: object | None = None,
) -> FastAPI:
    settings = get_settings()  # load_dotenv()

    # configure logging based on settings
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO)
    )

    session_store = memory or InMemorySessionStore(
        max_messages=settings.max_history_messages,
        max_sessions=settings.max_in_memory_sessions,
        ttl_seconds=settings.session_ttl_seconds,
    )
    model_client = llm_client or build_llm_client(settings)
    chat_service = ChatService(
        settings=settings,
        memory=session_store,
        llm_client=model_client,
    )

    app = FastAPI(title="Day 7 Minimal Chat Agent")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        return await chat_service.chat(req)

    @app.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
    def list_messages(session_id: str) -> list[ChatMessage]:
        return session_store.list_messages(session_id)

    @app.delete("/sessions/{session_id}")
    def clear_session(session_id: str) -> dict[str, str]:
        session_store.clear(session_id)
        return {"status": "cleared", "session_id": session_id}

    return app


"""The FastAPI application instance."""
app = create_app()
