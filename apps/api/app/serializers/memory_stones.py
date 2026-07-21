import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from app.models import Event, MemoryStone, Person, Place


@dataclass(frozen=True)
class PersonConnection:
    relationship_type: str
    person: Person


@dataclass(frozen=True)
class PlaceConnection:
    relationship_type: str
    place: Place


@dataclass(frozen=True)
class EventConnection:
    relationship_type: str
    event: Event


@dataclass(frozen=True)
class MemoryStoneConnections:
    people: tuple[PersonConnection, ...]
    places: tuple[PlaceConnection, ...]
    events: tuple[EventConnection, ...]


EMPTY_MEMORY_STONE_CONNECTIONS = MemoryStoneConnections(
    people=(),
    places=(),
    events=(),
)


def serialize_memory_stone(
    stone: MemoryStone,
    connections: MemoryStoneConnections,
) -> dict[str, Any]:
    return {
        "id": stone.id,
        "title": stone.title,
        "content": stone.content,
        "stone_type": stone.stone_type,
        "source_type": stone.source_type,
        "source_reference": stone.source_reference,
        "remembered_at": stone.remembered_at,
        "confidence": stone.confidence,
        "importance": stone.importance,
        "is_inferred": stone.is_inferred,
        "people": [
            {
                "relationship_type": connection.relationship_type,
                "person": connection.person,
            }
            for connection in connections.people
        ],
        "places": [
            {
                "relationship_type": connection.relationship_type,
                "place": connection.place,
            }
            for connection in connections.places
        ],
        "events": [
            {
                "relationship_type": connection.relationship_type,
                "event": connection.event,
            }
            for connection in connections.events
        ],
        "created_at": stone.created_at,
        "updated_at": stone.updated_at,
    }


def serialize_memory_stones(
    stones: Sequence[MemoryStone],
    connections_by_stone_id: Mapping[
        uuid.UUID,
        MemoryStoneConnections,
    ],
) -> list[dict[str, Any]]:
    return [
        serialize_memory_stone(
            stone,
            connections_by_stone_id.get(
                stone.id,
                EMPTY_MEMORY_STONE_CONNECTIONS,
            ),
        )
        for stone in stones
    ]
