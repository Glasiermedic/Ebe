import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    MemoryStone,
    Person,
    memory_stone_people,
)
from app.serializers.memory_stones import serialize_memory_stone


def get_person_memories(
    *,
    person_id: uuid.UUID,
    db: Session,
) -> list[dict[str, Any]]:
    person = db.get(Person, person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    statement = (
        select(MemoryStone)
        .join(
            memory_stone_people,
            memory_stone_people.c.memory_stone_id
            == MemoryStone.id,
        )
        .where(
            memory_stone_people.c.person_id == person_id
        )
        .order_by(
            MemoryStone.importance.desc(),
            MemoryStone.remembered_at.desc().nullslast(),
            MemoryStone.created_at.desc(),
        )
    )

    stones = db.scalars(statement).all()

    return [
        serialize_memory_stone(stone, db)
        for stone in stones
    ]
