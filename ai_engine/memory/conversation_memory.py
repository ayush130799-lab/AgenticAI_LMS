"""Conversation history -> LangChain message conversion, with bounded context."""

from __future__ import annotations

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

_ROLE_MAP = {
    "user": HumanMessage,
    "human": HumanMessage,
    "student": HumanMessage,
    "assistant": AIMessage,
    "ai": AIMessage,
    "tutor": AIMessage,
    "system": SystemMessage,
}


def to_langchain_messages(history: list[dict], limit: int = 10) -> list[BaseMessage]:
    """Convert `[{"role","content"}, ...]` into LangChain message objects.

    Trims to the last `limit` entries (default 10) so context stays bounded
    even if the caller (backend) already trimmed upstream — this is a
    defensive second trim, per the tutor agent's contract.
    """

    if not history:
        return []

    trimmed = history[-limit:] if limit and len(history) > limit else list(history)

    messages: list[BaseMessage] = []
    for turn in trimmed:
        if not isinstance(turn, dict):
            continue
        content = turn.get("content")
        if not content:
            continue
        role = str(turn.get("role", "")).lower()
        message_cls = _ROLE_MAP.get(role, HumanMessage)
        messages.append(message_cls(content=str(content)))
    return messages
