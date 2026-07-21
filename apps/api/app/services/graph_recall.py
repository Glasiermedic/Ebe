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
from app.services.memory_stone_transport import serialize_memory_stones


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

    return serialize_memory_stones(stones, db)


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
def get_person_timeline(
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
            MemoryStone.remembered_at.asc().nullslast(),
            MemoryStone.created_at.asc(),
        )
    )

    stones = db.scalars(statement).all()

    return serialize_memory_stones(stones, db)

def _get_related_people(
    memories: list[dict[str, Any]],
    root_person_id: uuid.UUID,
) -> list[Person]:
    people: dict[uuid.UUID, Person] = {}

    for memory in memories:
        for connection in memory["people"]:
            person = connection["person"]

            if person.id == root_person_id:
                continue

            people[person.id] = person

    return sorted(
        people.values(),
        key=lambda person: person.display_name.lower(),
    )


def _get_related_places(
    memories: list[dict[str, Any]],
) -> list[Place]:
    places: dict[uuid.UUID, Place] = {}

    for memory in memories:
        for connection in memory["places"]:
            place = connection["place"]
            places[place.id] = place

    return sorted(
        places.values(),
        key=lambda place: place.display_name.lower(),
    )


def _get_related_events(
    memories: list[dict[str, Any]],
) -> list[Event]:
    events: dict[uuid.UUID, Event] = {}

    for memory in memories:
        for connection in memory["events"]:
            event = connection["event"]
            events[event.id] = event

    return sorted(
        events.values(),
        key=lambda event: event.display_name.lower(),
    )

def get_person_context(
    *,
    person_id: uuid.UUID,
    db: Session,
) -> dict[str, Any]:
    person = db.get(Person, person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    memories = get_person_memories(
        person_id=person_id,
        db=db,
    )

    return {
        "person": person,
        "aliases": person.aliases,
        "memories": memories,
        "related_people": _get_related_people(
            memories,
            person_id,
        ),
        "related_places": _get_related_places(memories),
        "related_events": _get_related_events(memories),
    }