from typing import TypedDict

from langgraph.graph import StateGraph, END
from qdrant_client.models import (
    Filter,
    FieldCondition,
    MatchValue,
)

from app.db.embeddings import generate_embedding
from app.db.qdrant import qdrant_client
from app.services.llm import generate_answer


COLLECTION_NAME = "nexus_documents"

# RAG retrieval configuration
RETRIEVAL_TOP_K = 3
RETRIEVAL_SCORE_THRESHOLD = 0.50


class RAGState(TypedDict):
    question: str
    user_id: int
    context: str
    answer: str
    sources: list


# Retrieve documents
def retrieve_documents(state: RAGState):
    question = state["question"]
    user_id = state["user_id"]

    query_vector = generate_embedding(question)

    user_filter = Filter(
        must=[
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id),
            )
        ]
    )

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=user_filter,
        limit=RETRIEVAL_TOP_K,
        with_payload=True,
    )

    sources = []
    context_parts = []

    for point in results.points:
        if point.score < RETRIEVAL_SCORE_THRESHOLD:
            continue

        payload = point.payload or {}

        document_id = payload.get("document_id")
        filename = payload.get("filename")
        page_number = payload.get("page_number")
        chunk_index = payload.get("chunk_index")
        text = payload.get("text", "")

        source = {
            "document_id": document_id,
            "filename": filename,
            "page_number": page_number,
            "chunk_index": chunk_index,
            "score": round(float(point.score), 4),
            "text": text,
        }

        sources.append(source)

        context_parts.append(
            f"""
SOURCE {len(sources)}
Document: {filename}
Document ID: {document_id}
Page: {page_number}
Chunk: {chunk_index}
Similarity: {point.score:.4f}

Content:
{text}
""".strip()
        )

    context = "\n\n".join(context_parts)

    return {
        "context": context,
        "sources": sources,
    }


# Generate RAG answer
def generate_rag_answer(state: RAGState):
    question = state["question"]
    context = state["context"]

    if not context:
        return {
            "answer": (
                "I don't have enough information in the "
                "provided documents."
            )
        }

    grounded_context = f"""
You are answering a question using enterprise documents.

Use ONLY the information provided in the sources below.

Rules:
1. Do not invent information.
2. Do not use outside knowledge.
3. If the documents do not contain the answer, say that the information is not available.
4. Give a concise and direct answer.
5. Use the source content as evidence.

Sources:
{context}
"""

    answer = generate_answer(
        question,
        grounded_context,
    )

    return {
        "answer": answer,
    }


# LangGraph
graph = StateGraph(RAGState)

graph.add_node(
    "retrieve_documents",
    retrieve_documents,
)

graph.add_node(
    "generate_answer",
    generate_rag_answer,
)

graph.set_entry_point(
    "retrieve_documents"
)

graph.add_edge(
    "retrieve_documents",
    "generate_answer",
)

graph.add_edge(
    "generate_answer",
    END,
)


rag_agent = graph.compile()