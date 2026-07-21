import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import event as sqlalchemy_event
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
    serialize_memory_stone,
    serialize_memory_stones,
)
from app.services.memory_stone_connections import (
    load_memory_stone_connections,
)


def _build_memory_stone(
    title: str,
) -> MemoryStone:
    now = datetime.now(timezone.utc)

    return MemoryStone(
        id=uuid.uuid4(),
        title=title,
        content=f"Content for {title}",
        stone_type="memory",
        source_type="user_entry",
        source_reference=None,
        remembered_at=None,
        confidence=Decimal("1.000"),
        importance=Decimal("0.500"),
        is_inferred=False,
        created_at=now,
        updated_at=now,
    )


def test_serialize_memory_stone_preserves_transport_shape(
) -> None:
    now = datetime.now(timezone.utc)
    stone = _build_memory_stone("Family memory")

    person = Person(
        id=uuid.uuid4(),
        display_name="Laura",
        description=None,
        created_at=now,
    )

    place = Place(
        id=uuid.uuid4(),
        display_name="Home",
        description=None,
        latitude=None,
        longitude=None,
        created_at=now,
    )

    event = Event(
        id=uuid.uuid4(),
        display_name="Wedding",
        description=None,
        started_at=None,
        ended_at=None,
        created_at=now,
    )

    connections = MemoryStoneConnections(
        people=(
            PersonConnection(
                relationship_type="subject",
                person=person,
            ),
        ),
        places=(
            PlaceConnection(
                relationship_type="location",
                place=place,
            ),
        ),
        events=(
            EventConnection(
                relationship_type="part_of",
                event=event,
            ),
        ),
    )

    result = serialize_memory_stone(
        stone,
        connections,
    )

    assert result["id"] == stone.id
    assert result["title"] == "Family memory"
    assert result["people"] == [
        {
            "relationship_type": "subject",
            "person": person,
        }
    ]
    assert result["places"] == [
        {
            "relationship_type": "location",
            "place": place,
        }
    ]
    assert result["events"] == [
        {
            "relationship_type": "part_of",
            "event": event,
        }
    ]


def test_serialize_memory_stones_preserves_input_order(
) -> None:
    first = _build_memory_stone("First")
    second = _build_memory_stone("Second")

    result = serialize_memory_stones(
        (second, first),
        {},
    )

    assert [
        stone["id"]
        for stone in result
    ] == [
        second.id,
        first.id,
    ]

    assert result[0]["people"] == []
    assert result[0]["places"] == []
    assert result[0]["events"] == []


def test_load_memory_stone_connections_uses_three_queries(
    db_session: Session,
) -> None:
    stone = MemoryStone(
        title="Connected memory",
        content="A memory with several connections.",
    )

    amy = Person(display_name="Amy")
    zed = Person(display_name="Zed")
    home = Place(display_name="Home")

    old_event = Event(
        display_name="Old Event",
        started_at=datetime(
            2020,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    new_event = Event(
        display_name="New Event",
        started_at=datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    unknown_event = Event(
        display_name="Unknown Event",
        started_at=None,
    )

    db_session.add_all(
        [
            stone,
            amy,
            zed,
            home,
            old_event,
            new_event,
            unknown_event,
        ]
    )
    db_session.flush()

    db_session.execute(
        memory_stone_people.insert(),
        [
            {
                "memory_stone_id": stone.id,
                "person_id": zed.id,
                "relationship_type": "witness",
            },
            {
                "memory_stone_id": stone.id,
                "person_id": amy.id,
                "relationship_type": "subject",
            },
        ],
    )

    db_session.execute(
        memory_stone_places.insert().values(
            memory_stone_id=stone.id,
            place_id=home.id,
            relationship_type="location",
        )
    )

    db_session.execute(
        memory_stone_events.insert(),
        [
            {
                "memory_stone_id": stone.id,
                "event_id": old_event.id,
                "relationship_type": "related",
            },
            {
                "memory_stone_id": stone.id,
                "event_id": new_event.id,
                "relationship_type": "part_of",
            },
            {
                "memory_stone_id": stone.id,
                "event_id": unknown_event.id,
                "relationship_type": "related",
            },
        ],
    )

    db_session.commit()

    query_count = 0

    def count_query(*_: object) -> None:
        nonlocal query_count
        query_count += 1

    bind = db_session.get_bind()

    sqlalchemy_event.listen(
        bind,
        "before_cursor_execute",
        count_query,
    )

    try:
        result = load_memory_stone_connections(
            (stone,),
            db_session,
        )
    finally:
        sqlalchemy_event.remove(
            bind,
            "before_cursor_execute",
            count_query,
        )

    connections = result[stone.id]

    assert query_count == 3

    assert [
        connection.person.display_name
        for connection in connections.people
    ] == [
        "Amy",
        "Zed",
    ]

    assert [
        connection.relationship_type
        for connection in connections.people
    ] == [
        "subject",
        "witness",
    ]

    assert [
        connection.place.display_name
        for connection in connections.places
    ] == [
        "Home",
    ]

    assert [
        connection.event.display_name
        for connection in connections.events
    ] == [
        "New Event",
        "Old Event",
        "Unknown Event",
    ]



def test_load_connections_for_multiple_stones_uses_three_queries(
    db_session: Session,
) -> None:
    first_stone = MemoryStone(
        title="First connected memory",
        content="The first memory in the batch.",
    )

    second_stone = MemoryStone(
        title="Second connected memory",
        content="The second memory in the batch.",
    )

    first_person = Person(display_name="Laura")
    second_person = Person(display_name="Robert")

    db_session.add_all(
        [
            first_stone,
            second_stone,
            first_person,
            second_person,
        ]
    )
    db_session.flush()

    db_session.execute(
        memory_stone_people.insert(),
        [
            {
                "memory_stone_id": first_stone.id,
                "person_id": first_person.id,
                "relationship_type": "subject",
            },
            {
                "memory_stone_id": second_stone.id,
                "person_id": second_person.id,
                "relationship_type": "subject",
            },
        ],
    )

    db_session.commit()

    query_count = 0

    def count_query(*_: object) -> None:
        nonlocal query_count
        query_count += 1

    bind = db_session.get_bind()

    sqlalchemy_event.listen(
        bind,
        "before_cursor_execute",
        count_query,
    )

    try:
        result = load_memory_stone_connections(
            (second_stone, first_stone),
            db_session,
        )
    finally:
        sqlalchemy_event.remove(
            bind,
            "before_cursor_execute",
            count_query,
        )

    assert query_count == 3

    assert [
        connection.person.display_name
        for connection in result[first_stone.id].people
    ] == ["Laura"]

    assert [
        connection.person.display_name
        for connection in result[second_stone.id].people
    ] == ["Robert"]
