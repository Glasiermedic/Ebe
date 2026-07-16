import uuid
from typing import Any

from fastapi import APIRouter

from app.dependencies import DatabaseSession
from app.models import (
    Event,
    Person,
    Place,
    memory_stone_events,
    memory_stone_people,
    memory_stone_places,
)
from app.schemas import (
    MemoryStoneEventLinkCreate,
    MemoryStonePersonLinkCreate,
    MemoryStonePlaceLinkCreate,
    MemoryStoneRead,
)
from app.services.relationships import create_relationship


router = APIRouter(
    prefix="/stones/{stone_id}",
    tags=["relationships"],
)


@router.post(
    "/people",
    response_model=MemoryStoneRead,
)
def link_person_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStonePersonLinkCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    return create_relationship(
        stone_id=stone_id,
        related_id=link_data.person_id,
        related_model=Person,
        association_table=memory_stone_people,
        related_column_name="person_id",
        relationship_type=link_data.relationship_type,
        missing_detail="Person not found",
        db=db,
    )


@router.post(
    "/places",
    response_model=MemoryStoneRead,
)
def link_place_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStonePlaceLinkCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    return create_relationship(
        stone_id=stone_id,
        related_id=link_data.place_id,
        related_model=Place,
        association_table=memory_stone_places,
        related_column_name="place_id",
        relationship_type=link_data.relationship_type,
        missing_detail="Place not found",
        db=db,
    )


@router.post(
    "/events",
    response_model=MemoryStoneRead,
)
def link_event_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStoneEventLinkCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    return create_relationship(
        stone_id=stone_id,
        related_id=link_data.event_id,
        related_model=Event,
        association_table=memory_stone_events,
        related_column_name="event_id",
        relationship_type=link_data.relationship_type,
        missing_detail="Event not found",
        db=db,
    )