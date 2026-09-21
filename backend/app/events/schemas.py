from datetime import datetime
from pydantic import BaseModel, Field


class ChatEvent(BaseModel):
    event_type: str = "CHAT_QUERY"
    event_id: str
    user_id: int
    conversation_id: int

    question: str

    route: str | None = None
    agent: str | None = None

    success: bool = True
    duration_ms: int | None = None

    timestamp: datetime = Field(
        default_factory=datetime.utcnow
    )