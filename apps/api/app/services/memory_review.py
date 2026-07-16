from typing import Any

from sqlalchemy.orm import Session

from app.services.embeddings import EmbeddingProvider
from app.services.search import semantic_search_memory_stones


REVIEW_THRESHOLD = 0.93
REVIEW_LIMIT = 5


def review_memory(
    *,
    text: str,
    db: Session,
    embedding_provider: EmbeddingProvider,
) -> list[dict[str, Any]]:
    results = semantic_search_memory_stones(
        query=text,
        limit=REVIEW_LIMIT,
        db=db,
        embedding_provider=embedding_provider,
    )

    return [
        result
        for result in results
        if result["score"] >= REVIEW_THRESHOLD
    ]
