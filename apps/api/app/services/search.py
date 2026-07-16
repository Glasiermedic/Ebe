from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MemoryStone
from app.serializers.memory_stones import serialize_memory_stone
from app.services.embeddings import EmbeddingProvider


SEMANTIC_WEIGHT = 0.85
IMPORTANCE_WEIGHT = 0.15


def calculate_retrieval_score(
    *,
    semantic_score: float,
    importance: float,
) -> float:
    score = (
        semantic_score * SEMANTIC_WEIGHT
        + importance * IMPORTANCE_WEIGHT
    )

    return max(0.0, min(1.0, score))


def semantic_search_memory_stones(
    *,
    query: str,
    limit: int,
    db: Session,
    embedding_provider: EmbeddingProvider,
) -> list[dict[str, Any]]:
    query_embedding = embedding_provider.embed(query)

    if len(query_embedding) != 1536:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Embedding provider returned an unexpected "
                "vector dimension"
            ),
        )

    distance = MemoryStone.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    candidate_limit = max(limit * 5, limit)

    statement = (
        select(MemoryStone, distance)
        .where(MemoryStone.embedding.is_not(None))
        .order_by(distance)
        .limit(candidate_limit)
    )

    rows = db.execute(statement).all()

    results: list[dict[str, Any]] = []

    for stone, cosine_distance in rows:
        semantic_score = max(
            0.0,
            min(1.0, 1.0 - float(cosine_distance)),
        )

        importance = float(stone.importance)

        final_score = calculate_retrieval_score(
            semantic_score=semantic_score,
            importance=importance,
        )

        results.append(
            {
                "score": final_score,
                "semantic_score": semantic_score,
                "importance": stone.importance,
                "stone": serialize_memory_stone(stone, db),
            }
        )

    results.sort(
        key=lambda result: (
            result["score"],
            result["semantic_score"],
        ),
        reverse=True,
    )

    return results[:limit]
