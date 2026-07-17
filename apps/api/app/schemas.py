import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PersonCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    description: str | None
    created_at: datetime

class PersonAliasCreate(BaseModel):
    alias: str = Field(min_length=1, max_length=200)


class PersonAliasRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    person_id: uuid.UUID
    alias: str
    normalized_alias: str
    created_at: datetime

class PlaceCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class PlaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    description: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    created_at: datetime


class EventCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None

    @model_validator(mode="after")
    def validate_event_dates(self) -> "EventCreate":
        if (
            self.started_at is not None
            and self.ended_at is not None
            and self.ended_at < self.started_at
        ):
            raise ValueError("ended_at cannot be earlier than started_at")

        return self


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    description: str | None
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime

class PersonConnectionRead(BaseModel):
    relationship_type: str
    person: PersonRead


class PlaceConnectionRead(BaseModel):
    relationship_type: str
    place: PlaceRead


class EventConnectionRead(BaseModel):
    relationship_type: str
    event: EventRead

class MemoryStoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    stone_type: str = Field(default="memory", min_length=1, max_length=50)

    source_type: str = Field(
        default="user_entry",
        min_length=1,
        max_length=50,
    )

    source_reference: str | None = None
    remembered_at: date | None = None

    importance: Decimal = Field(
    default=Decimal("0.500"),
    ge=Decimal("0.000"),
    le=Decimal("1.000"),
    max_digits=4,
    decimal_places=3,
    )

    confidence: Decimal = Field(
        default=Decimal("1.000"),
        ge=Decimal("0.000"),
        le=Decimal("1.000"),
        max_digits=4,
        decimal_places=3,
    )

    is_inferred: bool = False


class MemoryStoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    stone_type: str
    source_type: str
    source_reference: str | None
    remembered_at: date | None
    confidence: Decimal
    is_inferred: bool

    people: list[PersonConnectionRead]
    places: list[PlaceConnectionRead]
    events: list[EventConnectionRead]

    created_at: datetime
    updated_at: datetime
    importance: Decimal

class PersonContextRead(BaseModel):
    person: PersonRead
    aliases: list[PersonAliasRead]
    memories: list[MemoryStoneRead]

    related_people: list[PersonRead]
    related_places: list[PlaceRead]
    related_events: list[EventRead]

class MemoryStonePersonLinkCreate(BaseModel):
    person_id: uuid.UUID
    relationship_type: str = Field(
        default="mentioned",
        min_length=1,
        max_length=50,
    )


class MemoryStonePlaceLinkCreate(BaseModel):
    place_id: uuid.UUID
    relationship_type: str = Field(
        default="location",
        min_length=1,
        max_length=50,
    )


class MemoryStoneEventLinkCreate(BaseModel):
    event_id: uuid.UUID
    relationship_type: str = Field(
        default="related",
        min_length=1,
        max_length=50,
    )
class MemoryStoneEmbeddingRead(BaseModel):
    id: uuid.UUID
    embedding_model: str
    embedded_at: datetime
    status: str

class QueryRequest(BaseModel):
    query: str


class QueryResultRead(BaseModel):
    query: str
    entity_type: str
    entity: PersonRead | PlaceRead | EventRead
    memories: list[MemoryStoneRead]

class SemanticSearchCreate(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class SemanticSearchResultRead(BaseModel):
    score: float
    semantic_score: float
    importance: Decimal
    stone: MemoryStoneRead

class MemoryStoneUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    content: str | None = Field(
        default=None,
        min_length=1,
    )
    stone_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    source_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    importance: Decimal | None = Field(
        default=None,
        ge=Decimal("0.000"),
        le=Decimal("1.000"),
        max_digits=4,
        decimal_places=3,
    )

    source_reference: str | None = None
    remembered_at: date | None = None
    confidence: Decimal | None = Field(
        default=None,
        ge=Decimal("0.000"),
        le=Decimal("1.000"),
        max_digits=4,
        decimal_places=3,
    )
    is_inferred: bool | None = None

class EmbeddingBatchCreate(BaseModel):
    limit: int = Field(default=25, ge=1, le=100)


class EmbeddingBatchRead(BaseModel):
    scanned: int
    embedded: int
    skipped_current: int
    stone_ids: list[uuid.UUID]

class ExtractedPerson(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    relationship_type: str = Field(
        default="mentioned",
        min_length=1,
        max_length=50,
    )


class ExtractedPlace(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    relationship_type: str = Field(
        default="location",
        min_length=1,
        max_length=50,
    )


class ExtractedEvent(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    relationship_type: str = Field(
        default="related",
        min_length=1,
        max_length=50,
    )


class ExtractedMemory(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    stone_type: str = Field(
        default="memory",
        min_length=1,
        max_length=50,
    )
    source_type: str = Field(
        default="user_entry",
        min_length=1,
        max_length=50,
    )

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    source_reference: str | None = None
    remembered_at: date | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    is_inferred: bool = False
    people: list[ExtractedPerson] = Field(default_factory=list)
    places: list[ExtractedPlace] = Field(default_factory=list)
    events: list[ExtractedEvent] = Field(default_factory=list)


class RememberCreate(BaseModel):
    text: str = Field(min_length=1, max_length=10000)

class CandidateMemoryMatch(BaseModel):
    score: float
    stone: MemoryStoneRead

class RememberRead(BaseModel):
    stone: MemoryStoneRead | None = None

    created_people: int = 0
    reused_people: int = 0
    created_places: int = 0
    reused_places: int = 0
    created_events: int = 0
    reused_events: int = 0

    embedding_status: str | None = None

    memory_status: Literal[
        "created",
        "duplicate",
        "review",
    ]

    candidate_matches: list[CandidateMemoryMatch] = Field(
        default_factory=list
    )
class CandidateMemoryMatch(BaseModel):
    score: float
    stone: MemoryStoneRead
class RememberResolutionCreate(BaseModel):
    text: str = Field(min_length=1, max_length=10000)

    action: Literal[
        "use_existing",
        "create_anyway",
    ]

    existing_stone_id: uuid.UUID | None = None


class RememberResolutionRead(BaseModel):
    resolution_status: Literal[
        "used_existing",
        "created",
        "duplicate",
    ]

    result: RememberRead