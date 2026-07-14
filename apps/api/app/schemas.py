import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoryStoneCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    stone_type: str = Field(default="memory", min_length=1, max_length=50)


class MemoryStoneRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content: str
    stone_type: str
    created_at: datetime
    updated_at: datetime
