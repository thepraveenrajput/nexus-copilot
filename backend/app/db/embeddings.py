from sentence_transformers import SentenceTransformer

from app.core.logging import get_logger


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

logger = get_logger(__name__)

logger.info(
    "Loading embedding model: %s",
    MODEL_NAME,
)

model = SentenceTransformer(MODEL_NAME)

logger.info(
    "Embedding model loaded successfully: %s",
    MODEL_NAME,
)


def generate_embedding(text: str):
    if not text or not text.strip():
        raise ValueError(
            "Cannot generate embedding for empty text."
        )

    try:
        return model.encode(
            text,
            convert_to_numpy=True,
        ).tolist()

    except Exception:
        logger.exception(
            "Embedding generation failed."
        )
        raise