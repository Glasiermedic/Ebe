from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import (
    MemoryStone,
    Person,
    memory_stone_people,
)
from app.services.query.models import (
    QueryPlan,
    ResolvedEntity,
    RetrievalRequest,
)
from app.services.query.retrieval import RetrievalService


def test_retrieval_service_uses_established_memory_order(
    db_session: Session,
) -> None:
    person = Person(
        display_name="Retrieval Ordering Person",
    )

    lower_stone = MemoryStone(
        title="Lower importance",
        content="This should be second.",
        importance=Decimal("0.200"),
    )

    higher_stone = MemoryStone(
        title="Higher importance",
        content="This should be first.",
        importance=Decimal("0.900"),
    )

    db_session.add_all(
        [
            person,
            lower_stone,
            higher_stone,
        ]
    )
    db_session.flush()

    db_session.execute(
        memory_stone_people.insert(),
        [
            {
                "memory_stone_id": lower_stone.id,
                "person_id": person.id,
                "relationship_type": "subject",
            },
            {
                "memory_stone_id": higher_stone.id,
                "person_id": person.id,
                "relationship_type": "subject",
            },
        ],
    )

    db_session.commit()

    plan = QueryPlan(
        intent="single_entity",
        query_text=person.display_name,
        candidate_phrases=(person.display_name,),
    )

    resolved_entity = ResolvedEntity(
        entity_type="person",
        entity=person,
        matched_by="canonical_name",
        matched_value=person.display_name,
    )

    result = RetrievalService().retrieve(
        request=RetrievalRequest(
            plan=plan,
            resolved_entities=(resolved_entity,),
        ),
        db=db_session,
    )

    assert [
        stone.id
        for stone in result.memory_stones
    ] == [
        higher_stone.id,
        lower_stone.id,
    ]
