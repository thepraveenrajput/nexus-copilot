import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.agents.router import router_agent

from app.services.message_service import (
    create_message,
    get_conversation_messages,
)

from app.services.conversation_service import (
    generate_conversation_title,
)

from app.services.audit_service import (
    create_audit_log,
)

from app.models.conversation import Conversation
from app.core.dependencies import get_current_user

from app.events.factory import create_chat_event
from app.events.producer import event_producer


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    question: str
    conversation_id: int


@router.post("")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    start_time = time.perf_counter()

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == request.conversation_id,
            Conversation.user_id == current_user.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    history = get_conversation_messages(
        db=db,
        conversation_id=request.conversation_id,
    )

    history_text = "\n".join(
        f"{message.role}: {message.content}"
        for message in history[-10:]
    )

    try:
        # -----------------------------------------
        # RUN AI ROUTER
        # -----------------------------------------

        result = router_agent.invoke(
            {
                "question": request.question,
                "user_id": current_user.id,
                "history": history_text,
                "route": "",
                "agent": "",
                "answer": "",
                "sources": [],
                "sql_answer": "",
                "rag_answer": "",
                "sql_question": "",
                "rag_question": "",
            }
        )

        answer = result["answer"]
        route = result["route"]
        agent = result["agent"]
        sources = result["sources"]

        # -----------------------------------------
        # SAVE USER MESSAGE
        # -----------------------------------------

        create_message(
            db=db,
            conversation_id=request.conversation_id,
            role="user",
            content=request.question,
        )

        # -----------------------------------------
        # GENERATE CONVERSATION TITLE
        # -----------------------------------------

        if conversation.title == "New Conversation":
            generate_conversation_title(
                db=db,
                conversation_id=request.conversation_id,
                question=request.question,
            )

        # -----------------------------------------
        # SAVE ASSISTANT MESSAGE
        # -----------------------------------------

        create_message(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=answer,
        )

        # -----------------------------------------
        # CALCULATE RESPONSE TIME
        # -----------------------------------------

        duration_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        # -----------------------------------------
        # CREATE AUDIT LOG
        # -----------------------------------------

        create_audit_log(
            db=db,
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            action="CHAT_QUERY",
            route=route,
            agent=agent,
            question=request.question,
            success=True,
            duration_ms=duration_ms,
        )

        # -----------------------------------------
        # CREATE KAFKA EVENT
        # -----------------------------------------

        chat_event = create_chat_event(
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            question=request.question,
            route=route,
            agent=agent,
            success=True,
            duration_ms=duration_ms,
        )

        # -----------------------------------------
        # PUBLISH EVENT TO KAFKA
        # -----------------------------------------

        event_producer.publish_chat_event(
            chat_event
        )

        # -----------------------------------------
        # RETURN RESPONSE
        # -----------------------------------------

        return {
            "question": request.question,
            "answer": answer,
            "route": route,
            "agent": agent,
            "sources": sources,
        }

    except Exception:
        # -----------------------------------------
        # FAILED REQUEST AUDIT LOG
        # -----------------------------------------

        duration_ms = int(
            (time.perf_counter() - start_time) * 1000
        )

        create_audit_log(
            db=db,
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            action="CHAT_QUERY",
            route=None,
            agent=None,
            question=request.question,
            success=False,
            duration_ms=duration_ms,
        )

        raise