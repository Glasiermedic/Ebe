import uuid
from typing import Any

from fastapi import APIRouter, status
from sqlalchemy import select

from app.dependencies import DatabaseSession
from app.models import MemoryStone
from app.schemas import (
    MemoryStoneCreate,
    MemoryStoneRead,
    MemoryStoneUpdate,
)
from app.services.memory_stone_transport import (
    serialize_memory_stone,
    serialize_memory_stones,
)
from app.services.memory_stones import get_memory_stone_or_404


router = APIRouter(
    prefix="/stones",
    tags=["stones"],
)


@router.post(
    "",
    response_model=MemoryStoneRead,
    status_code=status.HTTP_201_CREATED,
)
def create_memory_stone(
    stone_data: MemoryStoneCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    stone = MemoryStone(**stone_data.model_dump())

    db.add(stone)
    db.commit()
    db.refresh(stone)

    return serialize_memory_stone(stone, db)


@router.get(
    "",
    response_model=list[MemoryStoneRead],
)
def list_memory_stones(
    db: DatabaseSession,
) -> list[dict[str, Any]]:
    statement = select(MemoryStone).order_by(
        MemoryStone.created_at.desc()
    )

    stones = db.scalars(statement).all()

    return serialize_memory_stones(stones, db)


@router.get(
    "/{stone_id}",
    response_model=MemoryStoneRead,
)
def get_memory_stone(
    stone_id: uuid.UUID,
    db: DatabaseSession,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)

    return serialize_memory_stone(stone, db)


@router.patch(
    "/{stone_id}",
    response_model=MemoryStoneRead,
)
def update_memory_stone(
    stone_id: uuid.UUID,
    stone_data: MemoryStoneUpdate,
    db: DatabaseSession,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)

    update_values = stone_data.model_dump(
        exclude_unset=True
    )

    semantic_fields = {
        "title",
        "content",
        "stone_type",
        "source_type",
        "source_reference",
        "remembered_at",
    }

    semantic_content_changed = bool(
        semantic_fields.intersection(
            stone_data.model_fields_set
        )
    )

    for field_name, value in update_values.items():
        setattr(stone, field_name, value)

    if semantic_content_changed:
        stone.embedding = None
        stone.embedding_model = None
        stone.embedding_source_hash = None
        stone.embedded_at = None

    db.commit()
    db.refresh(stone)

    return serialize_memory_stone(stone, db)
