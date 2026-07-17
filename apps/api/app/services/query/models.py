from dataclasses import dataclass
from typing import Literal

from app.models import Event, Person, Place

EntityType = Literal["person", "place", "event"]
MatchType = Literal["canonical_name", "alias"]

QueryIntent = Literal[
    "single_entity",
    "multi_entity",
    "unknown",
]


@dataclass(frozen=True)
class NormalizedQuery:
    original: str
    normalized: str


@dataclass(frozen=True)
class ResolvedEntity:
    entity_type: EntityType
    entity: Person | Place | Event
    matched_by: MatchType
    matched_value: str


@dataclass(frozen=True)
class QueryPlan:
    intent: QueryIntent
    query_text: str
    candidate_phrases: tuple[str, ...]
