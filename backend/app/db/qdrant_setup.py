from qdrant_client.models import Distance, VectorParams
from app.db.qdrant import qdrant_client


COLLECTION_NAME = "nexus_documents"


def create_collection():
    existing_collections = qdrant_client.get_collections().collections

    if COLLECTION_NAME not in [c.name for c in existing_collections]:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


if __name__ == "__main__":
    create_collection()