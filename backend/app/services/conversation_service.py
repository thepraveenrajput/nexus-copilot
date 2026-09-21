from sqlalchemy.orm import Session
from app.models.conversation import Conversation


def create_conversation(
    db: Session,
    user_id: int,
    title: str = "New Conversation",
):
    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_user_conversations(db: Session, user_id: int):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


def update_conversation_title(
    db: Session,
    conversation_id: int,
    title: str,
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        return None

    conversation.title = title[:80]

    db.commit()
    db.refresh(conversation)

    return conversation


def delete_conversation(
    db: Session,
    conversation_id: int,
):
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .first()
    )

    if not conversation:
        return None

    from app.models.message import Message

    db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).delete(
        synchronize_session=False
    )

    db.delete(conversation)
    db.commit()

    return conversation_id


def generate_conversation_title(
    db: Session,
    conversation_id: int,
    question: str,
):
    """
    Generate a short readable title from the first question.

    Example:
        What is the annual leave policy?
        -> Annual Leave Policy

    If the same title already exists:
        Annual Leave Policy
        Annual Leave Policy — 2
        Annual Leave Policy — 3
    """

    title = question.strip()

    # Remove common question prefixes.
    prefixes = [
        "what is ",
        "what are ",
        "where is ",
        "where are ",
        "where do ",
        "where does ",
        "where should ",
        "where can ",
        "how many ",
        "how much ",
        "how do ",
        "how does ",
        "why is ",
        "why are ",
        "when is ",
        "when are ",
        "can you ",
        "could you ",
        "please ",
        "tell me about ",
        "explain ",
    ]

    lowered = title.lower()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            title = title[len(prefix):]
            break

    # Remove trailing question punctuation.
    title = title.strip(" ?!.,:")

    # Keep titles reasonably short.
    words = title.split()

    if len(words) > 7:
        title = " ".join(words[:7]) + "..."

    # Convert to clean title case.
    title = title.title()

    if not title:
        title = "New Conversation"

    # Check existing titles.
    existing = (
        db.query(Conversation)
        .filter(
            Conversation.title.like(f"{title}%"),
            Conversation.id != conversation_id,
        )
        .all()
    )

    exact_count = sum(
        1
        for conversation in existing
        if conversation.title == title
        or conversation.title.startswith(f"{title} — ")
    )

    if exact_count > 0:
        title = f"{title} — {exact_count + 1}"

    return update_conversation_title(
        db=db,
        conversation_id=conversation_id,
        title=title,
    )