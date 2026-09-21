from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DATABASE_URL
from app.core.logging import get_logger


logger = get_logger(__name__)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


# Register models with SQLAlchemy
from app.models.audit_log import AuditLog
from app.models.analytics_event import AnalyticsEvent


def check_postgres():
    try:
        with engine.connect():
            logger.info("PostgreSQL connection healthy")
            return True

    except Exception:
        logger.exception(
            "PostgreSQL health check failed"
        )
        raise