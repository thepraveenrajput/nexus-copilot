from qdrant_client.models import Filter, FieldCondition, MatchValue


COLLECTION_NAME = "nexus_documents"


def delete_document_chunks(
    qdrant_client,
    document_id: int,
):
    qdrant_client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=document_id
                    ),
                )
            ]
        ),
    )