from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid

import httpx
from pydantic import ValidationError

from app.agent.memory import InMemorySessionStore
from app.core.config import Settings
from app.core.telemetry import (
    GenerationTrace,
    InMemoryTraceStore,
    RequestMetrics,
    TokenUsage,
    estimate_cost,
)
from app.llm import LLMClient
from app.prompts import PromptRegistry
from app.schemas import ChatMessage, ChatRequest, ChatResponse, ReviewResult


class StructuredChatAgent:
    def __init__(
        self,
        settings: Settings,
        memory: InMemorySessionStore,
        llm_client: LLMClient,
        prompt_registry: PromptRegistry,
        trace_store: InMemoryTraceStore,
    ) -> None:
        self.settings = settings
        self.memory = memory
        self.llm_client = llm_client
        self.prompt_registry = prompt_registry
        self.trace_store = trace_store
        self.logger = logging.getLogger("structured_llm_agent")

    async def chat(self, req: ChatRequest) -> ChatResponse:
        request_id = str(uuid.uuid4())  # create a unique request id
        start = time.perf_counter()
        self.logger.info(
            "chat_start request_id=%s user_id=%s session_id=%s prompt_template=%s",
            request_id,
            req.user_id,
            req.session_id,
            req.prompt_template,
        )

        try:
            system_prompt = self.prompt_registry.render(req.prompt_template)
        except KeyError as exc:
            system_prompt = self.prompt_registry.render("weekly_review")
            self.logger.warning(
                "unknown_prompt_template request_id=%s error=%s", request_id, exc
            )

        self.memory.append(req.session_id, "user", req.message)
        messages = [
            ChatMessage(role="system", content=system_prompt)
        ] + self.memory.list_messages(req.session_id)

        review: ReviewResult | None = None  # create a variable to store the review
        validation_error: str | None = (
            None  # create a variable to store the validation error
        )
        usage = TokenUsage()  # create a variable to store the token usage

        try:
            model_response = await asyncio.wait_for(
                self.llm_client.generate(messages),
                timeout=self.settings.request_timeout_seconds,
            )
            model = model_response.model
            usage = model_response.usage
            review, validation_error = self._validate_json_output(
                model_response.content
            )
            answer = review.summary if review else model_response.content
        except asyncio.TimeoutError:
            model = "timeout"
            answer = "模型响应超时，请稍后重试。"
            validation_error = "timeout"
            self.logger.warning("chat_timeout request_id=%s", request_id)
        except httpx.HTTPStatusError as exc:
            model = "deepseek-error"
            answer = f"模型服务返回错误：HTTP {exc.response.status_code}"
            validation_error = answer
            self.logger.exception("chat_http_error request_id=%s", request_id)
        except Exception as exc:
            model = "unknown-error"
            answer = "模型调用失败，请检查配置或稍后重试。"
            validation_error = str(exc)
            self.logger.exception("chat_unknown_error request_id=%s", request_id)

        self.memory.append(req.session_id, "assistant", answer)
        latency_ms = int((time.perf_counter() - start) * 1000)
        metrics = RequestMetrics(  # create a variable to store the metrics
            latency_ms=latency_ms,
            usage=usage,
            cost=estimate_cost(
                usage,
                self.settings.input_token_price_per_1m,
                self.settings.output_token_price_per_1m,
            ),
            validation_ok=validation_error is None,
            validation_error=validation_error,
        )
        self.trace_store.append(
            GenerationTrace(
                request_id=request_id,
                session_id=req.session_id,
                model=model,
                prompt_template=req.prompt_template,
                metrics=metrics,
            )
        )

        self.logger.info(
            "chat_done request_id=%s session_id=%s latency_ms=%s model=%s tokens=%s cost=%s validation_ok=%s",
            request_id,
            req.session_id,
            latency_ms,
            model,
            usage.total_tokens,
            metrics.cost.total_cost,
            metrics.validation_ok,
        )

        return ChatResponse(
            request_id=request_id,
            session_id=req.session_id,
            answer=answer,
            model=model,
            history_count=self.memory.count(req.session_id),
            review=review,
            metrics=metrics,
        )

    def _validate_json_output(
        self, content: str
    ) -> tuple[ReviewResult | None, str | None]:
        """Validate the JSON output of the model"""
        try:
            data = json.loads(self._extract_json_object(content))
            return (
                ReviewResult.model_validate(data),
                None,
            )  # return the review and no error
        except (
            json.JSONDecodeError,
            ValidationError,
            ValueError,
        ) as exc:  # catch JSON parsing errors, validation errors, and value errors from extraction
            return None, str(exc)

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        return self.memory.list_messages(session_id)

    def clear_session(self, session_id: str) -> None:
        self.memory.clear(session_id)

    @staticmethod  # you can make this a static method since it does not depend on the instance state
    def _extract_json_object(content: str) -> str:
        """Extract the JSON object from the model output"""
        stripped = content.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("model output does not contain a JSON object")
        return stripped[start : end + 1]
