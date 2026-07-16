from typing import Any

from fastapi import APIRouter, status

from app.dependencies import (
    DatabaseSession,
    EmbeddingService,
    ExtractionService,
)
from app.schemas import RememberCreate, RememberRead
from app.services.memory_creation import create_memory_from_text


router = APIRouter(
    tags=["remember"],
)


@router.post(
    "/remember",
    response_model=RememberRead,
    status_code=status.HTTP_201_CREATED,
)
def remember(
    remember_data: RememberCreate,
    db: DatabaseSession,
    extraction_provider: ExtractionService,
    embedding_provider: EmbeddingService,
) -> dict[str, Any]:
    return create_memory_from_text(
        text=remember_data.text,
        db=db,
        extraction_provider=extraction_provider,
        embedding_provider=embedding_provider,
    )
