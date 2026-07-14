import uuid
from datetime import date, datetime
from decimal import Decimal

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