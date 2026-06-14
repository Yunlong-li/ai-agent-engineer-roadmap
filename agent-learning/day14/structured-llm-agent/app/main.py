from __future__ import annotations

import logging

from fastapi import FastAPI

from app.agent.memory import InMemorySessionStore
from app.agent.service import StructuredChatAgent
from app.api.routes import build_router
from app.core.config import get_settings
from app.core.telemetry import InMemoryTraceStore
from app.llm import LLMClient, build_llm_client
from app.prompts import PromptRegistry, build_prompt_registry


def create_app(
    memory: InMemorySessionStore | None = None,
    llm_client: LLMClient | None = None,
    prompt_registry: PromptRegistry | None = None,
    trace_store: InMemoryTraceStore | None = None,
) -> FastAPI:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    session_store = memory or InMemorySessionStore(
        max_messages=settings.max_history_messages,
        max_sessions=settings.max_in_memory_sessions,
        ttl_seconds=settings.session_ttl_seconds,
    )
    registry = prompt_registry or build_prompt_registry()
    traces = trace_store or InMemoryTraceStore(max_events=settings.trace_buffer_size)
    agent = StructuredChatAgent(
        settings=settings,
        memory=session_store,
        llm_client=llm_client or build_llm_client(settings),
        prompt_registry=registry,
        trace_store=traces,
    )

    app = FastAPI(title="Day 14 Structured LLM Agent")
    app.include_router(build_router(agent))
    return app


app = create_app()
