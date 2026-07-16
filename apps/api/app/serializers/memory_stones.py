from typing import Any

from sqlalchemy import select
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


def serialize_memory_stone(
    stone: MemoryStone,
    db: Session,
) -> dict[str, Any]:
    person_rows = db.execute(
        select(
            memory_stone_people.c.relationship_type,
            Person,
        )
        .join(
            Person,
            Person.id == memory_stone_people.c.person_id,
        )
        .where(
            memory_stone_people.c.memory_stone_id == stone.id,
        )
        .order_by(Person.display_name)
    ).all()

    place_rows = db.execute(
        select(
            memory_stone_places.c.relationship_type,
            Place,
        )
        .join(
            Place,
            Place.id == memory_stone_places.c.place_id,
        )
        .where(
            memory_stone_places.c.memory_stone_id == stone.id,
        )
        .order_by(Place.display_name)
    ).all()

    event_rows = db.execute(
        select(
            memory_stone_events.c.relationship_type,
            Event,
        )
        .join(
            Event,
            Event.id == memory_stone_events.c.event_id,
        )
        .where(
            memory_stone_events.c.memory_stone_id == stone.id,
        )
        .order_by(Event.started_at.desc().nullslast())
    ).all()

    return {
        "id": stone.id,
        "title": stone.title,
        "content": stone.content,
        "stone_type": stone.stone_type,
        "source_type": stone.source_type,
        "source_reference": stone.source_reference,
        "remembered_at": stone.remembered_at,
        "confidence": stone.confidence,
        "is_inferred": stone.is_inferred,
        "people": [
            {
                "relationship_type": relationship_type,
                "person": person,
            }
            for relationship_type, person in person_rows
        ],
        "places": [
            {
                "relationship_type": relationship_type,
                "place": place,
            }
            for relationship_type, place in place_rows
        ],
        "events": [
            {
                "relationship_type": relationship_type,
                "event": event,
            }
            for relationship_type, event in event_rows
        ],
        "created_at": stone.created_at,
        "updated_at": stone.updated_at,
    }