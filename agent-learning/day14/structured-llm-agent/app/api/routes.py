from __future__ import annotations

from fastapi import APIRouter

from app.agent.service import StructuredChatAgent
from app.core.telemetry import GenerationTrace
from app.prompts import PromptTemplate
from app.schemas import ChatMessage, ChatRequest, ChatResponse


def build_router(agent: StructuredChatAgent) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest) -> ChatResponse:
        return await agent.chat(req)

    @router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
    def list_messages(session_id: str) -> list[ChatMessage]:
        return agent.list_messages(session_id)

    @router.delete("/sessions/{session_id}")
    def clear_session(session_id: str) -> dict[str, str]:
        agent.clear_session(session_id)
        return {"status": "cleared", "session_id": session_id}

    @router.get("/prompts", response_model=list[PromptTemplate])
    def list_prompts() -> list[PromptTemplate]:
        return agent.prompt_registry.list_templates()

    @router.get("/traces", response_model=list[GenerationTrace])
    def list_traces(limit: int = 50) -> list[GenerationTrace]:
        return agent.trace_store.list_events(limit=limit)

    return router
