"""
In-memory Vector Index with cosine similarity search.
Pre-seeded with disease knowledge documents.

# INTEGRATION POINT: Replace with a real FAISS index or vector DB
# (e.g., faiss, chromadb, pinecone) for production-scale search.
"""
import math
import logging
from typing import Optional

from app.models import VectorDocument, RetrievedContext, ContextMetadata
from app.services.embedding import generate_embedding
from app.data.disease_knowledge import DISEASE_KNOWLEDGE

logger = logging.getLogger("c-dit")

# In-memory vector document store
_vector_store: list[VectorDocument] = []
_is_initialized = False


async def initialize_vector_index() -> None:
    """Initialize the vector index by embedding all disease knowledge documents."""
    global _is_initialized
    if _is_initialized:
        return

    logger.info("Initializing vector index with disease knowledge...")

    for entry in DISEASE_KNOWLEDGE:
        parts = [
            f"Disease: {entry['diseaseName']}",
            f"Crop: {entry['cropAffected']}",
            f"Symptoms: {entry['symptoms']}",
            f"Causes: {entry['causes']}",
            f"Treatment: {entry['treatment']}",
            f"Prevention: {entry['prevention']}",
        ]
        if entry.get("additionalNotes"):
            parts.append(f"Notes: {entry['additionalNotes']}")

        content = "\n".join(parts)
        embedding = await generate_embedding(content)

        doc = VectorDocument(
            id=entry["id"],
            content=content,
            embedding=embedding,
            metadata=ContextMetadata(
                diseaseName=entry["diseaseName"],
                category=entry["cropAffected"],
                source="knowledge-base",
            ),
        )
        _vector_store.append(doc)

    _is_initialized = True
    logger.info(f"Vector index initialized with {len(_vector_store)} documents")


def search_similar(query_embedding: list[float], top_k: int = 5) -> list[RetrievedContext]:
    """Search for the most similar documents to a query vector."""
    if not _vector_store:
        logger.warning("Vector store is empty; returning no results")
        return []

    scored = []
    for doc in _vector_store:
        sim = _cosine_similarity(query_embedding, doc.embedding)
        scored.append((doc, sim))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        RetrievedContext(
            documentId=doc.id,
            content=doc.content,
            similarity=round(sim, 3),
            metadata=doc.metadata,
        )
        for doc, sim in scored[:top_k]
    ]


def get_document_count() -> int:
    return len(_vector_store)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    denom = mag_a * mag_b
    return dot_product / denom if denom > 0 else 0.0
