import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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

    created_at: datetime
    updated_at: datetime
