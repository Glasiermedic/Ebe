from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Event, Person, Place
from app.services.graph_recall import (
    get_event_memories,
    get_person_memories,
    get_place_memories,
)
from app.services.query.entity_resolver import (
    resolve_single_entity,
)
from app.services.query.normalizer import normalize_query


def _retrieve_entity_memories(
    *,
    entity_type: str,
    entity: Person | Place | Event,
    db: Session,
) -> list[dict]:
    if entity_type == "person":
        return get_person_memories(
            person_id=entity.id,
            db=db,
        )

    if entity_type == "place":
        return get_place_memories(
            place_id=entity.id,
            db=db,
        )

    if entity_type == "event":
        return get_event_memories(
            event_id=entity.id,
            db=db,
        )

    raise ValueError(f"Unsupported entity type: {entity_type}")


def answer_query(
    query: str,
    db: Session,
) -> dict:
    normalized_query = normalize_query(query)

    if not normalized_query.normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=("Query must contain a person, place, or event name"),
        )

    resolved_entity = resolve_single_entity(
        name=normalized_query.normalized,
        db=db,
    )

    if resolved_entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("No matching person, place, or event found"),
        )

    memories = _retrieve_entity_memories(
        entity_type=resolved_entity.entity_type,
        entity=resolved_entity.entity,
        db=db,
    )

    return {
        "query": normalized_query.original,
        "normalized_query": normalized_query.normalized,
        "entity_type": resolved_entity.entity_type,
        "matched_by": resolved_entity.matched_by,
        "matched_value": resolved_entity.matched_value,
        "entity": resolved_entity.entity,
        "memories": memories,
    }
