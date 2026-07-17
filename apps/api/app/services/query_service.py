from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Event, Person, Place
from app.services.graph_recall import (
    get_event_memories,
    get_person_memories,
    get_place_memories,
)


def _normalize_query(query: str) -> str:
    normalized = query.strip()

    prefixes = (
        "tell me about ",
        "what do you know about ",
        "who is ",
        "what is ",
    )

    lowered = normalized.lower()

    for prefix in prefixes:
        if lowered.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
            break

    return normalized.rstrip("?.!").strip()


def _find_person(
    *,
    name: str,
    db: Session,
) -> Person | None:
    statement = select(Person).where(
        func.lower(Person.display_name) == name.lower()
    )

    return db.scalar(statement)


def _find_place(
    *,
    name: str,
    db: Session,
) -> Place | None:
    statement = select(Place).where(
        func.lower(Place.display_name) == name.lower()
    )

    return db.scalar(statement)


def _find_event(
    *,
    name: str,
    db: Session,
) -> Event | None:
    statement = select(Event).where(
        func.lower(Event.display_name) == name.lower()
    )

    return db.scalar(statement)


def answer_query(
    *,
    query: str,
    db: Session,
) -> dict[str, Any]:
    entity_name = _normalize_query(query)

    if not entity_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query must identify a person, place, or event",
        )

    person = _find_person(
        name=entity_name,
        db=db,
    )

    if person is not None:
        return {
            "query": query,
            "entity_type": "person",
            "entity": person,
            "memories": get_person_memories(
                person_id=person.id,
                db=db,
            ),
        }

    place = _find_place(
        name=entity_name,
        db=db,
    )

    if place is not None:
        return {
            "query": query,
            "entity_type": "place",
            "entity": place,
            "memories": get_place_memories(
                place_id=place.id,
                db=db,
            ),
        }

    event = _find_event(
        name=entity_name,
        db=db,
    )

    if event is not None:
        return {
            "query": query,
            "entity_type": "event",
            "entity": event,
            "memories": get_event_memories(
                event_id=event.id,
                db=db,
            ),
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No matching person, place, or event found",
    )
    