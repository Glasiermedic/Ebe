import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import MemoryStone
from app.services.embeddings import (
    EmbeddingProvider,
    build_memory_stone_embedding_text,
    calculate_embedding_source_hash,
    embedding_is_current,
)


def get_memory_stone_or_404(
    stone_id: uuid.UUID,
    db: Session,
) -> MemoryStone:
    stone = db.get(MemoryStone, stone_id)

    if stone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Stone not found",
        )

    return stone


def generate_memory_stone_embedding(
    *,
    stone: MemoryStone,
    embedding_provider: EmbeddingProvider,
) -> str:
    if embedding_is_current(
        stone,
        provider_model_name=embedding_provider.model_name,
    ):
        return "current"

    embedding_text = build_memory_stone_embedding_text(stone)
    embedding = embedding_provider.embed(embedding_text)

    if len(embedding) != 1536:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Embedding provider returned an unexpected "
                "vector dimension"
            ),
        )

    stone.embedding = embedding
    stone.embedding_model = embedding_provider.model_name
    stone.embedding_source_hash = (
        calculate_embedding_source_hash(embedding_text)
    )
    stone.embedded_at = datetime.now(UTC)

    return "generated"