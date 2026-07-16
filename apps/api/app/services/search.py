from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MemoryStone
from app.serializers.memory_stones import serialize_memory_stone
from app.services.embeddings import EmbeddingProvider


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

    statement = (
        select(MemoryStone, distance)
        .where(MemoryStone.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    )

    rows = db.execute(statement).all()

    return [
        {
            "score": max(
                0.0,
                min(1.0, 1.0 - float(cosine_distance)),
            ),
            "stone": serialize_memory_stone(stone, db),
        }
        for stone, cosine_distance in rows
    ]
