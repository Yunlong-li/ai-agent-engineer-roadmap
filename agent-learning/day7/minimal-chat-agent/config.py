from __future__ import annotations

import os
from dataclasses import dataclass

"""Load environment variables from a .env file."""


def load_dotenv(path: str = ".env") -> None:
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)  # 把一行文本按 第一个等号 = 切成两段
            os.environ.setdefault(
                key.strip(), value.strip()
            )  # 不存在才设置，不覆盖已有的值


# 加上 frozen=True 后：
# 你可以创建这个 Settings 对象
# 你可以读取里面的所有配置
# 但是你不能修改任何字段
"""The configuration module for the minimal chat agent."""


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


"""Load settings from environment variables, with defaults."""


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
    )
