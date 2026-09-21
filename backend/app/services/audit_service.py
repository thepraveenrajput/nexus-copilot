from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    user_id: int | None,
    conversation_id: int | None,
    action: str,
    route: str | None = None,
    agent: str | None = None,
    question: str | None = None,
    success: bool = True,
    duration_ms: int | None = None,
):
    audit_log = AuditLog(
        user_id=user_id,
        conversation_id=conversation_id,
        action=action,
        route=route,
        agent=agent,
        question=question,
        success=success,
        duration_ms=duration_ms,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log