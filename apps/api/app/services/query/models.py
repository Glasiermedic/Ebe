from dataclasses import dataclass
from typing import Literal

from app.models import Event, Person, Place

EntityType = Literal["person", "place", "event"]
MatchType = Literal["canonical_name", "alias"]


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
