from __future__ import annotations

import asyncio
import logging
import time
import uuid

import httpx

from config import Settings
from memory import InMemorySessionStore
from schemas import ChatMessage, ChatRequest, ChatResponse

SYSTEM_PROMPT = """你是一个 AI Agent 学习助手。
回答要简洁、准确、适合初学者。
如果用户在复盘学习内容，优先用条目总结：学了什么、还差什么、下一步做什么。
"""


class ChatService:
    def __init__(
        self, settings: Settings, memory: InMemorySessionStore, llm_client
    ) -> None:
        self.settings = settings
        self.memory = memory
        self.llm_client = llm_client
        self.logger = logging.getLogger("minimal_chat_agent")

    async def chat(self, req: ChatRequest) -> ChatResponse:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        self.logger.info(
            "chat_start request_id=%s user_id=%s session_id=%s",
            request_id,
            req.user_id,
            req.session_id,
        )

        self.memory.append(req.session_id, "user", req.message)
        messages = self._build_messages(req.session_id)

        try:
            model_response = await asyncio.wait_for(
                self.llm_client.generate(messages),
                timeout=self.settings.request_timeout_seconds,
            )
            answer = model_response.content
            model = model_response.model
        except asyncio.TimeoutError:
            answer = "模型响应超时，请稍后重试。"
            model = "timeout"
            self.logger.warning("chat_timeout request_id=%s", request_id)
        except httpx.HTTPStatusError as exc:
            answer = f"模型服务返回错误：HTTP {exc.response.status_code}"
            model = "deepseek-error"
            self.logger.exception("chat_http_error request_id=%s", request_id)
        except Exception:
            answer = "模型调用失败，请检查配置或稍后重试。"
            model = "unknown-error"
            self.logger.exception("chat_unknown_error request_id=%s", request_id)

        self.memory.append(req.session_id, "assistant", answer)

        latency_ms = int((time.perf_counter() - start) * 1000)  # record latency

        self.logger.info(
            "chat_done request_id=%s session_id=%s latency_ms=%s model=%s",
            request_id,
            req.session_id,
            latency_ms,
            model,
        )

        return ChatResponse(
            request_id=request_id,
            session_id=req.session_id,
            answer=answer,
            model=model,
            history_count=self.memory.count(req.session_id),
        )

    """Helper method to build the message list for the LLM, including system prompt and history."""

    def _build_messages(self, session_id: str):
        history = self.memory.list_messages(session_id)
        return [ChatMessage(role="system", content=SYSTEM_PROMPT)] + history
