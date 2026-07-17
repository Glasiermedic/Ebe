from typing import Annotated, TypeVar




from app.routers.people import router as people_router

from app.routers.remember import router as remember_router

from app.routers.places import router as places_router

from app.routers.events import router as events_router

from app.routers.relationships import router as relationships_router

from app.routers.embeddings import router as embeddings_router

from app.routers.search import router as search_router

from app.routers.stones import router as stones_router

from app.routers.query import router as query_router


from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Event,
    Person,
    Place,
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
app.include_router(stones_router)
app.include_router(query_router)

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











