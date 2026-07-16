import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.dependencies import DatabaseSession, EmbeddingService
from app.models import MemoryStone
from app.schemas import (
    EmbeddingBatchCreate,
    EmbeddingBatchRead,
    MemoryStoneEmbeddingRead,
)
from app.services.memory_stones import (
    generate_memory_stone_embedding,
    get_memory_stone_or_404,
)


router = APIRouter(
    tags=["embeddings"],
)


@router.post(
    "/stones/{stone_id}/embed",
    response_model=MemoryStoneEmbeddingRead,
)
def embed_memory_stone(
    stone_id: uuid.UUID,
    db: DatabaseSession,
    embedding_provider: EmbeddingService,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)

    embedding_status = generate_memory_stone_embedding(
        stone=stone,
        embedding_provider=embedding_provider,
    )

    if embedding_status == "generated":
        db.commit()
        db.refresh(stone)

    if stone.embedding_model is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model metadata is missing",
        )

    if stone.embedded_at is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding timestamp is missing",
        )

    return {
        "id": stone.id,
        "embedding_model": stone.embedding_model,
        "embedded_at": stone.embedded_at,
        "status": embedding_status,
    }


@router.post(
    "/stones/embed-pending",
    response_model=EmbeddingBatchRead,
)
def embed_pending_memory_stones(
    batch_data: EmbeddingBatchCreate,
    db: DatabaseSession,
    embedding_provider: EmbeddingService,
) -> dict[str, Any]:
    statement = (
        select(MemoryStone)
        .order_by(MemoryStone.created_at)
        .limit(batch_data.limit)
    )

    stones = list(db.scalars(statement).all())

    embedded_ids: list[uuid.UUID] = []
    skipped_current = 0

    for stone in stones:
        embedding_status = generate_memory_stone_embedding(
            stone=stone,
            embedding_provider=embedding_provider,
        )

        if embedding_status == "current":
            skipped_current += 1
        else:
            embedded_ids.append(stone.id)

    if embedded_ids:
        db.commit()

    return {
        "scanned": len(stones),
        "embedded": len(embedded_ids),
        "skipped_current": skipped_current,
        "stone_ids": embedded_ids,
    }