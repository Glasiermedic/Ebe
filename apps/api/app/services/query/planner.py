import re

from app.services.query.models import QueryPlan

ENTITY_SEPARATOR_PATTERN = re.compile(
    r"\s*(?:,|\band\b|\bwith\b)\s*",
    flags=re.IGNORECASE,
)


def _split_candidate_phrases(query_text: str) -> tuple[str, ...]:
    parts = ENTITY_SEPARATOR_PATTERN.split(query_text)

    candidates = tuple(part.strip() for part in parts if part.strip())

    return candidates


def create_query_plan(query_text: str) -> QueryPlan:
    cleaned_query = query_text.strip()

    if not cleaned_query:
        return QueryPlan(
            intent="unknown",
            query_text="",
            candidate_phrases=(),
        )

    candidate_phrases = _split_candidate_phrases(cleaned_query)

    if len(candidate_phrases) > 1:
        intent = "multi_entity"
    else:
        intent = "single_entity"

    return QueryPlan(
        intent=intent,
        query_text=cleaned_query,
        candidate_phrases=candidate_phrases,
    )
