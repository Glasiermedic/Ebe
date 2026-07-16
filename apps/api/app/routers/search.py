from typing import Any

from fastapi import APIRouter

from app.dependencies import DatabaseSession, EmbeddingService
from app.schemas import (
    SemanticSearchCreate,
    SemanticSearchResultRead,
)
from app.services.search import semantic_search_memory_stones


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


@router.post(
    "/semantic",
    response_model=list[SemanticSearchResultRead],
)
def semantic_search(
    search_data: SemanticSearchCreate,
    db: DatabaseSession,
    embedding_provider: EmbeddingService,
) -> list[dict[str, Any]]:
    return semantic_search_memory_stones(
        query=search_data.query,
        limit=search_data.limit,
        db=db,
        embedding_provider=embedding_provider,
    )
