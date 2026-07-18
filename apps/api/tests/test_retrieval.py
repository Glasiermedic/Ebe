from unittest.mock import MagicMock
from uuid import uuid4

import pytest
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


def test_retrieve_raises_for_multiple_entities() -> None:
    db = MagicMock(spec=Session)

    person = Person(
        id=uuid4(),
        display_name="Laura",
    )
    place = Place(
        id=uuid4(),
        display_name="Hillsboro",
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

    with pytest.raises(
        NotImplementedError,
        match="Multi-entity retrieval has not been implemented yet",
    ):
        RetrievalService().retrieve(
            request=request,
            db=db,
        )

    db.query.assert_not_called()