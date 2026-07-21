from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Event, MemoryStone, Person, Place
from app.services.query.models import (
    QueryPlan,
    ResolvedEntity,
    RetrievalRequest,
)
from app.services.query.retrieval import RetrievalService


def make_request(
    *resolved_entities: ResolvedEntity,
) -> RetrievalRequest:
    plan = MagicMock(spec=QueryPlan)

    return RetrievalRequest(
        plan=plan,
        resolved_entities=tuple(resolved_entities),
    )


def configure_memory_stone_query(
    db: MagicMock,
    memory_stones: list[MemoryStone],
) -> MagicMock:
    query = db.query.return_value
    query.join.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.all.return_value = memory_stones

    return query


def test_retrieve_person_memory_stones() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )
    memory_stone = MemoryStone()

    configure_memory_stone_query(
        db=db,
        memory_stones=[memory_stone],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value="Laura",
        )
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (memory_stone,)
    db.query.assert_called_once_with(MemoryStone)


def test_retrieve_place_memory_stones() -> None:
    db = MagicMock(spec=Session)

    place = Place(
        id=uuid4(),
        display_name="Hillsboro",
    )
    memory_stone = MemoryStone()

    configure_memory_stone_query(
        db=db,
        memory_stones=[memory_stone],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="place",
            entity=place,
            matched_by="canonical_name",
            matched_value="Hillsboro",
        )
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (memory_stone,)
    db.query.assert_called_once_with(MemoryStone)


def test_retrieve_event_memory_stones() -> None:
    db = MagicMock(spec=Session)

    event = Event(
        id=uuid4(),
        display_name="House Fire",
    )
    memory_stone = MemoryStone()

    configure_memory_stone_query(
        db=db,
        memory_stones=[memory_stone],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="event",
            entity=event,
            matched_by="canonical_name",
            matched_value="House Fire",
        )
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (memory_stone,)
    db.query.assert_called_once_with(MemoryStone)


def test_retrieve_returns_empty_tuple_when_no_stones_match() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )

    configure_memory_stone_query(
        db=db,
        memory_stones=[],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value="Laura",
        )
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == ()


def test_retrieve_returns_empty_tuple_when_no_entities_are_provided() -> None:
    db = MagicMock(spec=Session)
    request = make_request()

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == ()
    db.query.assert_not_called()


def configure_memory_stone_queries(
    db: MagicMock,
    query_results: list[list[MemoryStone]],
) -> list[MagicMock]:
    queries = []

    for memory_stones in query_results:
        query = MagicMock()
        query.join.return_value = query
        query.filter.return_value = query
        query.order_by.return_value = query
        query.all.return_value = memory_stones
        queries.append(query)

    db.query.side_effect = queries

    return queries


def test_retrieve_union_for_two_people() -> None:
    db = MagicMock(spec=Session)

    laura = Person(
        id=uuid4(),
        display_name="Laura",
    )
    robert = Person(
        id=uuid4(),
        display_name="Robert",
    )

    laura_stone = MemoryStone(id=uuid4())
    shared_stone = MemoryStone(id=uuid4())
    robert_stone = MemoryStone(id=uuid4())

    configure_memory_stone_queries(
        db=db,
        query_results=[
            [laura_stone, shared_stone],
            [shared_stone, robert_stone],
        ],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=laura,
            matched_by="canonical_name",
            matched_value="Laura",
        ),
        ResolvedEntity(
            entity_type="person",
            entity=robert,
            matched_by="canonical_name",
            matched_value="Robert",
        ),
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (
        laura_stone,
        shared_stone,
        robert_stone,
    )
    assert db.query.call_count == 2


def test_retrieve_union_for_person_and_place() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )
    place = Place(
        id=uuid4(),
        display_name="Hillsboro",
    )

    person_stone = MemoryStone(id=uuid4())
    place_stone = MemoryStone(id=uuid4())

    configure_memory_stone_queries(
        db=db,
        query_results=[
            [person_stone],
            [place_stone],
        ],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value="Laura",
        ),
        ResolvedEntity(
            entity_type="place",
            entity=place,
            matched_by="canonical_name",
            matched_value="Hillsboro",
        ),
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (
        person_stone,
        place_stone,
    )
    assert db.query.call_count == 2


def test_retrieve_union_for_mixed_entity_types() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )
    place = Place(
        id=uuid4(),
        display_name="Hillsboro",
    )
    event = Event(
        id=uuid4(),
        display_name="House Fire",
    )

    person_stone = MemoryStone(id=uuid4())
    shared_stone = MemoryStone(id=uuid4())
    place_stone = MemoryStone(id=uuid4())
    event_stone = MemoryStone(id=uuid4())

    configure_memory_stone_queries(
        db=db,
        query_results=[
            [person_stone, shared_stone],
            [shared_stone, place_stone],
            [shared_stone, event_stone],
        ],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value="Laura",
        ),
        ResolvedEntity(
            entity_type="place",
            entity=place,
            matched_by="canonical_name",
            matched_value="Hillsboro",
        ),
        ResolvedEntity(
            entity_type="event",
            entity=event,
            matched_by="canonical_name",
            matched_value="House Fire",
        ),
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (
        person_stone,
        shared_stone,
        place_stone,
        event_stone,
    )
    assert db.query.call_count == 3


def test_retrieve_union_removes_duplicate_memory_stones() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )
    event = Event(
        id=uuid4(),
        display_name="House Fire",
    )

    shared_id = uuid4()

    person_version = MemoryStone(id=shared_id)
    event_version = MemoryStone(id=shared_id)

    configure_memory_stone_queries(
        db=db,
        query_results=[
            [person_version],
            [event_version],
        ],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value="Laura",
        ),
        ResolvedEntity(
            entity_type="event",
            entity=event,
            matched_by="canonical_name",
            matched_value="House Fire",
        ),
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (person_version,)
    assert len(result.memory_stones) == 1


def test_retrieve_union_handles_entity_with_no_matches() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )
    place = Place(
        id=uuid4(),
        display_name="Unknown Place",
    )

    memory_stone = MemoryStone(id=uuid4())

    configure_memory_stone_queries(
        db=db,
        query_results=[
            [memory_stone],
            [],
        ],
    )

    request = make_request(
        ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value="Laura",
        ),
        ResolvedEntity(
            entity_type="place",
            entity=place,
            matched_by="canonical_name",
            matched_value="Unknown Place",
        ),
    )

    result = RetrievalService().retrieve(
        request=request,
        db=db,
    )

    assert result.memory_stones == (memory_stone,)
    assert db.query.call_count == 2
