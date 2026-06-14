from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from app.schemas import ChatMessage, Role


class InMemorySessionStore:
    def __init__(
        self,
        max_messages: int = 12,
        max_sessions: int = 100,
        ttl_seconds: int = 3600,
    ) -> None:
        self.max_messages = max(1, max_messages)
        self.max_sessions = max(1, max_sessions)
        self.ttl_seconds = ttl_seconds
        self._messages: OrderedDict[str, list[ChatMessage]] = OrderedDict()
        self._last_seen: dict[str, datetime] = {}

    def append(self, session_id: str, role: Role, content: str) -> None:
        self._evict_expired()
        self._messages.setdefault(session_id, [])
        self._messages.move_to_end(session_id)
        self._messages[session_id].append(ChatMessage(role=role, content=content))
        self._messages[session_id] = self._messages[session_id][-self.max_messages :]
        self._touch(session_id)
        self._evict_overflow()

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        self._evict_expired()
        if session_id in self._messages:
            self._messages.move_to_end(session_id)
            self._touch(session_id)
        return list(self._messages.get(session_id, []))

    def clear(self, session_id: str) -> None:
        self._messages.pop(session_id, None)
        self._last_seen.pop(session_id, None)

    def count(self, session_id: str) -> int:
        self._evict_expired()
        return len(self._messages.get(session_id, []))

    def _touch(self, session_id: str) -> None:
        self._last_seen[session_id] = datetime.now(timezone.utc)

    def _evict_expired(self) -> None:
        if self.ttl_seconds <= 0:
            return

        expire_before = datetime.now(timezone.utc) - timedelta(seconds=self.ttl_seconds)
        expired = [
            session_id
            for session_id, last_seen in self._last_seen.items()
            if last_seen < expire_before
        ]
        for session_id in expired:
            self.clear(session_id)

    def _evict_overflow(self) -> None:
        while len(self._messages) > self.max_sessions:
            session_id, _ = self._messages.popitem(last=False)
            self._last_seen.pop(session_id, None)
