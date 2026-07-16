from typing import Any

from fastapi import APIRouter, status

from app.dependencies import (
    DatabaseSession,
    EmbeddingService,
    ExtractionService,
)
from app.schemas import (
    RememberCreate,
    RememberRead,
    RememberResolutionCreate,
    RememberResolutionRead,
)
from app.services.memory_creation import create_memory_from_text
from app.services.review_resolution import resolve_memory_review

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
@router.post(
    "/remember/resolve",
    response_model=RememberResolutionRead,
)
def resolve_remember_review(
    resolution_data: RememberResolutionCreate,
    db: DatabaseSession,
    extraction_provider: ExtractionService,
    embedding_provider: EmbeddingService,
) -> dict[str, Any]:
    return resolve_memory_review(
        text=resolution_data.text,
        action=resolution_data.action,
        existing_stone_id=(
            resolution_data.existing_stone_id
        ),
        db=db,
        extraction_provider=extraction_provider,
        embedding_provider=embedding_provider,
    )