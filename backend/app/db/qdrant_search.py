from app.db.qdrant import qdrant_client


COLLECTION_NAME = "nexus_documents"

query_vector = [0.1] * 384

results = qdrant_client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=5,
    with_payload=True
)

for point in results.points:
    print("Score:", point.score)
    print("Payload:", point.payload)
    print("---")