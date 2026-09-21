from pathlib import Path
from uuid import uuid5, NAMESPACE_URL

from qdrant_client.models import PointStruct

from app.db.qdrant import qdrant_client
from app.db.embeddings import generate_embedding
from app.services.document_loader import load_document
from app.services.text_chunker import chunk_text


COLLECTION_NAME = "nexus_documents"


def ingest_document(
    file_path: str,
    document_id: int,
    user_id: int,
):
    """
    Load a PDF/DOCX document, split it into page-aware chunks,
    generate embeddings, and store the chunks in Qdrant.

    Each Qdrant chunk is associated with the user,
    document, page, and chunk that it came from.
    """

    # 1. LOAD DOCUMENT

    pages = load_document(file_path)

    if not pages:
        raise ValueError(
            "The document does not contain readable text."
        )

    # 2. DOCUMENT METADATA

    path = Path(file_path)
    filename = path.name

    # 3. CREATE QDRANT POINTS

    points = []
    global_chunk_index = 0

    for page in pages:
        page_number = page["page_number"]
        page_text = page["text"]

        chunks = chunk_text(page_text)

        for chunk in chunks:
            vector = generate_embedding(chunk)

            point_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{document_id}:{global_chunk_index}",
                )
            )

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "document_id": document_id,
                        "user_id": user_id,
                        "filename": filename,
                        "file_path": str(path),
                        "page_number": page_number,
                        "chunk_index": global_chunk_index,
                        "text": chunk,
                    },
                )
            )

            global_chunk_index += 1

    if not points:
        raise ValueError(
            "No text chunks were generated from the document."
        )

    # 4. UPSERT INTO QDRANT

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    # 5. RETURN RESULT

    return len(points)