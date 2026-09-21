from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db

from app.core.dependencies import get_current_user

from app.services.conversation_service import (
    create_conversation,
    get_user_conversations,
    delete_conversation,
)

from app.services.message_service import (
    get_conversation_messages,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


# --------------------------------------------------
# CREATE CONVERSATION
# --------------------------------------------------

@router.post("")
def create_new_conversation(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conversation = create_conversation(
        db=db,
        user_id=current_user.id,
    )

    return {
        "id": conversation.id,
        "title": conversation.title,
    }


# --------------------------------------------------
# LIST USER CONVERSATIONS
# --------------------------------------------------

@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    conversations = get_user_conversations(
        db=db,
        user_id=current_user.id,
    )

    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


# --------------------------------------------------
# GET CONVERSATION MESSAGES
# --------------------------------------------------

@router.get("/{conversation_id}/messages")
def list_conversation_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Make sure the conversation belongs to the
    # authenticated user.
    conversations = get_user_conversations(
        db=db,
        user_id=current_user.id,
    )

    allowed_ids = {
        conversation.id
        for conversation in conversations
    }

    if conversation_id not in allowed_ids:
        return {
            "message": "Conversation not found",
            "messages": [],
        }

    messages = get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
    )

    return [
        {
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]


# --------------------------------------------------
# DELETE CONVERSATION
# --------------------------------------------------

@router.delete("/{conversation_id}")
def remove_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Make sure the conversation belongs to
    # the authenticated user.
    conversations = get_user_conversations(
        db=db,
        user_id=current_user.id,
    )

    allowed_ids = {
        conversation.id
        for conversation in conversations
    }

    if conversation_id not in allowed_ids:
        return {
            "message": "Conversation not found",
            "conversation_id": conversation_id,
        }

    deleted_id = delete_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    if deleted_id is None:
        return {
            "message": "Conversation not found",
            "conversation_id": conversation_id,
        }

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": deleted_id,
    }