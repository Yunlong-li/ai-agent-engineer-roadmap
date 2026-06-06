from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from schemas import ChatMessage, Role

"""The in-memory session store for chat messages, with eviction policies."""


class InMemorySessionStore:
    def __init__(
        self,
        max_messages: int = 12,  # max number of messages per session
        max_sessions: int = 100,  # max number of sessions
        ttl_seconds: int = 3600,  # seconds before a session expires
    ) -> None:
        self.max_messages = max(1, max_messages)
        self.max_sessions = max(1, max_sessions)
        self.ttl_seconds = ttl_seconds
        self._messages: OrderedDict[str, list[ChatMessage]] = (
            OrderedDict()
        )  # session_id -> [ChatMessage] (underline means private variable, not for external use)
        self._last_seen: dict[str, datetime] = {}  # session_id -> last access time

    """Append a message to a session.
        the detailed process of appending a message to a session is:
        1. Evict expired sessions based on TTL.
        2. Ensure the session exists in the messages dictionary.
        3. Mark the session as recently used by moving it to the end of the OrderedDict.
        4. Append the new message to the session's message list.
        5. Trim the session's message list to keep only the last max_messages.
        6. Update the last seen time for the session.
        7. Evict sessions if the total number of sessions exceeds max_sessions.
    """

    def append(self, session_id: str, role: Role, content: str) -> None:
        self._evict()
        self._messages.setdefault(session_id, [])
        self._messages.move_to_end(
            session_id
        )  # move to end to mark as most recently used (LRU - least recently used)
        self._messages[session_id].append(ChatMessage(role=role, content=content))
        self._messages[session_id] = self._messages[session_id][
            -self.max_messages :
        ]  # keep only the last max_messages
        self._touch(session_id)  # update last seen time
        self._evict_overflow()  # evict if we exceed max_sessions

    """List messages in a session."""

    def list_messages(self, session_id: str) -> list[ChatMessage]:
        self._evict()
        if session_id in self._messages:
            self._messages.move_to_end(session_id)
            self._touch(session_id)

        # The purpose of "list()" here is to return a new list object
        # that is a copy of the original list of messages for the session.
        # This is done to prevent external code from modifying
        # the internal state of the session store.
        # By returning a copy, any changes made to the returned list
        # will not affect the original list stored in the session store,
        # ensuring data integrity and encapsulation.
        # “不要返回内部可变状态的直接引用，而是返回它的副本。”
        return list(self._messages.get(session_id, []))

    """Clear a session."""

    def clear(self, session_id: str) -> None:
        self._messages.pop(
            session_id, None
        )  # 'None' means don't raise an error if the key doesn't exist
        self._last_seen.pop(session_id, None)

    """Count the number of messages in a session."""

    def count(self, session_id: str) -> int:
        self._evict()
        return len(self._messages.get(session_id, []))

    """Update the last seen time for a session."""

    def _touch(self, session_id: str) -> None:
        self._last_seen[session_id] = datetime.now(timezone.utc)

    """Evict expired sessions."""

    def _evict(self) -> None:
        if self.ttl_seconds <= 0:
            return

        # Calculate expiration time
        expire_before = datetime.now(timezone.utc) - timedelta(seconds=self.ttl_seconds)
        # Find expired sessions
        expired = [
            session_id
            for session_id, last_seen in self._last_seen.items()
            if last_seen < expire_before
        ]
        # Evict expired sessions
        for session_id in expired:
            self.clear(session_id)

    def _evict_overflow(self) -> None:
        while len(self._messages) > self.max_sessions:
            session_id, _ = self._messages.popitem(
                last=False
            )  # remove the first item (last=False means remove the first item, if last=True, remove the last item)
            self._last_seen.pop(session_id, None)  # also remove from last_seen


# p = dict(a=1, b=2, c=3)
# print(p) # {'a': 1, 'b': 2, 'c': 3}
# print("a" in p) # True
