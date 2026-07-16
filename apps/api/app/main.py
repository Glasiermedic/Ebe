import uuid
from typing import Annotated, Any, TypeVar



from app.serializers.memory_stones import serialize_memory_stone

from app.routers.people import router as people_router

from app.routers.remember import router as remember_router

from app.routers.places import router as places_router

from app.routers.events import router as events_router

from app.routers.relationships import router as relationships_router

from app.routers.embeddings import router as embeddings_router

from app.routers.search import router as search_router

from app.services.memory_stones import (
    get_memory_stone_or_404,
)

from fastapi import Depends, FastAPI, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Event,
    MemoryStone,
    Person,
    Place,
)
from app.schemas import (
    MemoryStoneCreate,
    MemoryStoneRead,
    MemoryStoneUpdate,
)
from app.services.embeddings import (
    EmbeddingProvider,
    get_embedding_provider,
)
from app.services.extraction import (
    MemoryExtractionProvider,
    get_memory_extraction_provider,
)

app = FastAPI(
    title="Ebe API",
    description="The memory and context service for Ebe.",
    version="0.6.0",
)

app.include_router(people_router)
app.include_router(remember_router)
app.include_router(places_router)
app.include_router(events_router)
app.include_router(relationships_router)
app.include_router(embeddings_router)
app.include_router(search_router)


DatabaseSession = Annotated[Session, Depends(get_db)]
RelatedModel = TypeVar("RelatedModel", Person, Place, Event)
EmbeddingService = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]
ExtractionService = Annotated[
    MemoryExtractionProvider,
    Depends(get_memory_extraction_provider),
]


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Ebe",
        "status": "awake",
        "message": "The first stone has been placed.",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post(
    "/stones",
    response_model=MemoryStoneRead,
    status_code=status.HTTP_201_CREATED,
)
def create_memory_stone(
    stone_data: MemoryStoneCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    stone = MemoryStone(**stone_data.model_dump())

    db.add(stone)
    db.commit()
    db.refresh(stone)

    return serialize_memory_stone(stone, db)


@app.get("/stones", response_model=list[MemoryStoneRead])
def list_memory_stones(
    db: DatabaseSession,
) -> list[dict[str, Any]]:
    statement = select(MemoryStone).order_by(
        MemoryStone.created_at.desc()
    )

    stones = db.scalars(statement).all()

    return [
        serialize_memory_stone(stone, db)
        for stone in stones
    ]


@app.get("/stones/{stone_id}", response_model=MemoryStoneRead)
def get_memory_stone(
    stone_id: uuid.UUID,
    db: DatabaseSession,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)

    return serialize_memory_stone(stone, db)

@app.patch(
    "/stones/{stone_id}",
    response_model=MemoryStoneRead,
)
def update_memory_stone(
    stone_id: uuid.UUID,
    stone_data: MemoryStoneUpdate,
    db: DatabaseSession,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)

    update_values = stone_data.model_dump(
        exclude_unset=True
    )

    semantic_fields = {
        "title",
        "content",
        "stone_type",
        "source_type",
        "source_reference",
        "remembered_at",
    }

    semantic_content_changed = bool(
        semantic_fields.intersection(
            stone_data.model_fields_set
        )
    )

    for field_name, value in update_values.items():
        setattr(stone, field_name, value)

    if semantic_content_changed:
        stone.embedding = None
        stone.embedding_model = None
        stone.embedding_source_hash = None
        stone.embedded_at = None

    db.commit()
    db.refresh(stone)

    return serialize_memory_stone(stone, db)








