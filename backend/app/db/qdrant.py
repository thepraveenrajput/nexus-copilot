from qdrant_client import QdrantClient

from app.core.config import QDRANT_URL
from app.core.logging import get_logger


logger = get_logger(__name__)


qdrant_client = QdrantClient(
    url=QDRANT_URL,
)


def check_qdrant():
    try:
        result = qdrant_client.get_collections()

        logger.info("Qdrant connection healthy")

        return result

    except Exception:
        logger.exception("Qdrant health check failed")
        raise