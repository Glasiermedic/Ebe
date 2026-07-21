from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services.memory_stone_transport import (
    serialize_memory_stones,
)
from app.services.query.entity_resolver import (
    resolve_entities,
    resolve_single_entity,
)
from app.services.query.models import (
    ResolvedEntity,
    RetrievalRequest,
)
from app.services.query.normalizer import normalize_query
from app.services.query.planner import create_query_plan
from app.services.query.retrieval import RetrievalService


def _build_entity_payload(
    resolved_entity: ResolvedEntity,
) -> dict[str, Any]:
    return {
        "entity_type": resolved_entity.entity_type,
        "matched_by": resolved_entity.matched_by,
        "matched_value": resolved_entity.matched_value,
        "entity": resolved_entity.entity,
    }


def answer_query(
    query: str,
    db: Session,
) -> dict[str, Any]:
    normalized_query = normalize_query(query)

    if not normalized_query.normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Query must contain a person, place, "
                "or event name"
            ),
        )

    plan = create_query_plan(
        normalized_query.normalized,
    )

    if plan.intent == "single_entity":
        resolved_entity = resolve_single_entity(
            name=plan.candidate_phrases[0],
            db=db,
        )

        if resolved_entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "No matching person, place, "
                    "or event found"
                ),
            )

        retrieval_result = RetrievalService().retrieve(
            request=RetrievalRequest(
                plan=plan,
                resolved_entities=(resolved_entity,),
            ),
            db=db,
        )

        memories = serialize_memory_stones(
            retrieval_result.memory_stones,
            db,
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

    if plan.intent == "multi_entity":
        resolved_entities = resolve_entities(
            names=plan.candidate_phrases,
            db=db,
        )

        retrieval_result = RetrievalService().retrieve(
            request=RetrievalRequest(
                plan=plan,
                resolved_entities=resolved_entities,
            ),
            db=db,
        )

        memories = serialize_memory_stones(
            retrieval_result.memory_stones,
            db,
        )

        return {
            "query": normalized_query.original,
            "normalized_query": normalized_query.normalized,
            "intent": "multi_entity",
            "entities": [
                _build_entity_payload(resolved_entity)
                for resolved_entity in resolved_entities
            ],
            "retrieval_strategy": "entity_union",
            "memories": memories,
        }

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Unable to determine query intent",
    )
