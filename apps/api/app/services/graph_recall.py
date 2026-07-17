import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import Column, Table, select
from sqlalchemy.orm import Session

from app.models import (
    Event,
    MemoryStone,
    Person,
    Place,
    memory_stone_events,
    memory_stone_people,
    memory_stone_places,
)
from app.serializers.memory_stones import serialize_memory_stone


def _get_related_memories(
    *,
    entity_id: uuid.UUID,
    entity_model: type[Person] | type[Place] | type[Event],
    relationship_table: Table,
    relationship_entity_column: Column[Any],
    entity_name: str,
    db: Session,
) -> list[dict[str, Any]]:
    entity = db.get(entity_model, entity_id)

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity_name} not found",
        )

    statement = (
        select(MemoryStone)
        .join(
            relationship_table,
            relationship_table.c.memory_stone_id
            == MemoryStone.id,
        )
        .where(relationship_entity_column == entity_id)
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


def get_person_memories(
    *,
    person_id: uuid.UUID,
    db: Session,
) -> list[dict[str, Any]]:
    return _get_related_memories(
        entity_id=person_id,
        entity_model=Person,
        relationship_table=memory_stone_people,
        relationship_entity_column=(
            memory_stone_people.c.person_id
        ),
        entity_name="Person",
        db=db,
    )


def get_place_memories(
    *,
    place_id: uuid.UUID,
    db: Session,
) -> list[dict[str, Any]]:
    return _get_related_memories(
        entity_id=place_id,
        entity_model=Place,
        relationship_table=memory_stone_places,
        relationship_entity_column=(
            memory_stone_places.c.place_id
        ),
        entity_name="Place",
        db=db,
    )


def get_event_memories(
    *,
    event_id: uuid.UUID,
    db: Session,
) -> list[dict[str, Any]]:
    return _get_related_memories(
        entity_id=event_id,
        entity_model=Event,
        relationship_table=memory_stone_events,
        relationship_entity_column=(
            memory_stone_events.c.event_id
        ),
        entity_name="Event",
        db=db,
    )
