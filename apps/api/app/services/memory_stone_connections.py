import uuid
from collections.abc import Sequence

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
from app.serializers.memory_stones import (
    EventConnection,
    MemoryStoneConnections,
    PersonConnection,
    PlaceConnection,
)


def load_memory_stone_connections(
    stones: Sequence[MemoryStone],
    db: Session,
) -> dict[uuid.UUID, MemoryStoneConnections]:
    stone_ids = tuple(
        dict.fromkeys(stone.id for stone in stones)
    )

    if not stone_ids:
        return {}

    people_by_stone_id: dict[
        uuid.UUID,
        list[PersonConnection],
    ] = {
        stone_id: []
        for stone_id in stone_ids
    }

    places_by_stone_id: dict[
        uuid.UUID,
        list[PlaceConnection],
    ] = {
        stone_id: []
        for stone_id in stone_ids
    }

    events_by_stone_id: dict[
        uuid.UUID,
        list[EventConnection],
    ] = {
        stone_id: []
        for stone_id in stone_ids
    }

    person_rows = db.execute(
        select(
            memory_stone_people.c.memory_stone_id,
            memory_stone_people.c.relationship_type,
            Person,
        )
        .join(
            Person,
            Person.id == memory_stone_people.c.person_id,
        )
        .where(
            memory_stone_people.c.memory_stone_id.in_(
                stone_ids
            )
        )
        .order_by(
            memory_stone_people.c.memory_stone_id,
            Person.display_name,
        )
    ).all()

    for stone_id, relationship_type, person in person_rows:
        people_by_stone_id[stone_id].append(
            PersonConnection(
                relationship_type=relationship_type,
                person=person,
            )
        )

    place_rows = db.execute(
        select(
            memory_stone_places.c.memory_stone_id,
            memory_stone_places.c.relationship_type,
            Place,
        )
        .join(
            Place,
            Place.id == memory_stone_places.c.place_id,
        )
        .where(
            memory_stone_places.c.memory_stone_id.in_(
                stone_ids
            )
        )
        .order_by(
            memory_stone_places.c.memory_stone_id,
            Place.display_name,
        )
    ).all()

    for stone_id, relationship_type, place in place_rows:
        places_by_stone_id[stone_id].append(
            PlaceConnection(
                relationship_type=relationship_type,
                place=place,
            )
        )

    event_rows = db.execute(
        select(
            memory_stone_events.c.memory_stone_id,
            memory_stone_events.c.relationship_type,
            Event,
        )
        .join(
            Event,
            Event.id == memory_stone_events.c.event_id,
        )
        .where(
            memory_stone_events.c.memory_stone_id.in_(
                stone_ids
            )
        )
        .order_by(
            memory_stone_events.c.memory_stone_id,
            Event.started_at.desc().nullslast(),
        )
    ).all()

    for stone_id, relationship_type, event in event_rows:
        events_by_stone_id[stone_id].append(
            EventConnection(
                relationship_type=relationship_type,
                event=event,
            )
        )

    return {
        stone_id: MemoryStoneConnections(
            people=tuple(people_by_stone_id[stone_id]),
            places=tuple(places_by_stone_id[stone_id]),
            events=tuple(events_by_stone_id[stone_id]),
        )
        for stone_id in stone_ids
    }
