from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.embeddings import (
    EmbeddingProvider,
    get_embedding_provider,
)
from app.services.extraction import (
    MemoryExtractionProvider,
    get_memory_extraction_provider,
)


DatabaseSession = Annotated[Session, Depends(get_db)]

EmbeddingService = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]

ExtractionService = Annotated[
    MemoryExtractionProvider,
    Depends(get_memory_extraction_provider),
]