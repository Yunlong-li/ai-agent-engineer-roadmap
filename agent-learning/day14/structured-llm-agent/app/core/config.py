from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    deepseek_api_key: str
    deepseek_base_url: str
    deepseek_chat_path: str
    deepseek_model: str
    request_timeout_seconds: float
    max_history_messages: int
    max_in_memory_sessions: int
    session_ttl_seconds: int
    log_level: str
    input_token_price_per_1m: float
    output_token_price_per_1m: float
    trace_buffer_size: int


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "deepseek"),
        deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_chat_path=os.getenv("DEEPSEEK_CHAT_PATH", "/v1/chat/completions"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash"),
        request_timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "15")),
        max_history_messages=int(os.getenv("MAX_HISTORY_MESSAGES", "12")),
        max_in_memory_sessions=int(os.getenv("MAX_IN_MEMORY_SESSIONS", "100")),
        session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", "3600")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        input_token_price_per_1m=float(os.getenv("INPUT_TOKEN_PRICE_PER_1M", "0")),
        output_token_price_per_1m=float(os.getenv("OUTPUT_TOKEN_PRICE_PER_1M", "0")),
        trace_buffer_size=int(os.getenv("TRACE_BUFFER_SIZE", "200")),
    )

