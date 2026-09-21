from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.core.rbac import require_admin

from app.models.audit_log import AuditLog
from app.models.analytics_event import AnalyticsEvent


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# ---------------------------------------------------------
# AUDIT LOGS
# ---------------------------------------------------------

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "conversation_id": log.conversation_id,
            "action": log.action,
            "route": log.route,
            "agent": log.agent,
            "question": log.question,
            "success": log.success,
            "duration_ms": log.duration_ms,
            "created_at": log.created_at,
        }
        for log in logs
    ]


# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@router.get("/analytics")
def get_analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    total_queries = (
        db.query(func.count(AnalyticsEvent.id))
        .scalar()
        or 0
    )

    successful_queries = (
        db.query(func.count(AnalyticsEvent.id))
        .filter(
            AnalyticsEvent.success.is_(True)
        )
        .scalar()
        or 0
    )

    failed_queries = (
        db.query(func.count(AnalyticsEvent.id))
        .filter(
            AnalyticsEvent.success.is_(False)
        )
        .scalar()
        or 0
    )

    rag_queries = (
        db.query(func.count(AnalyticsEvent.id))
        .filter(
            AnalyticsEvent.route == "rag"
        )
        .scalar()
        or 0
    )

    sql_queries = (
        db.query(func.count(AnalyticsEvent.id))
        .filter(
            AnalyticsEvent.route == "sql"
        )
        .scalar()
        or 0
    )

    hybrid_queries = (
        db.query(func.count(AnalyticsEvent.id))
        .filter(
            AnalyticsEvent.route == "hybrid"
        )
        .scalar()
        or 0
    )

    average_response_time = (
        db.query(
            func.avg(
                AnalyticsEvent.duration_ms
            )
        )
        .scalar()
        or 0
    )

    return {
        "total_queries": total_queries,
        "successful_queries": successful_queries,
        "failed_queries": failed_queries,
        "rag_queries": rag_queries,
        "sql_queries": sql_queries,
        "hybrid_queries": hybrid_queries,
        "average_response_time_ms": round(
            float(average_response_time),
            2,
        ),
    }