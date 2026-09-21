from uuid import uuid4

from app.events.schemas import ChatEvent


def create_chat_event(
    user_id: int,
    conversation_id: int,
    question: str,
    route: str | None,
    agent: str | None,
    success: bool,
    duration_ms: int | None,
):
    return ChatEvent(
        event_id=str(uuid4()),
        user_id=user_id,
        conversation_id=conversation_id,
        question=question,
        route=route,
        agent=agent,
        success=success,
        duration_ms=duration_ms,
    )