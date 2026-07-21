import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import MemoryStone
from app.services.memory_stone_transport import serialize_memory_stone
from app.services.embeddings import EmbeddingProvider
from app.services.extraction import MemoryExtractionProvider
from app.services.memory_creation import create_memory_from_text
from app.services.memory_stones import (
    generate_memory_stone_embedding,
)


def resolve_memory_review(
    *,
    text: str,
    action: str,
    existing_stone_id: uuid.UUID | None,
    db: Session,
    extraction_provider: MemoryExtractionProvider,
    embedding_provider: EmbeddingProvider,
) -> dict[str, Any]:
    if action == "use_existing":
        if existing_stone_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "existing_stone_id is required when "
                    "action is use_existing"
                ),
            )

        stone = db.get(MemoryStone, existing_stone_id)

        if stone is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Memory Stone not found",
            )

        embedding_status = generate_memory_stone_embedding(
            stone=stone,
            embedding_provider=embedding_provider,
        )

        if embedding_status == "generated":
            db.commit()
            db.refresh(stone)

        return {
            "resolution_status": "used_existing",
            "result": {
                "stone": serialize_memory_stone(stone, db),
                "created_people": 0,
                "reused_people": 0,
                "created_places": 0,
                "reused_places": 0,
                "created_events": 0,
                "reused_events": 0,
                "embedding_status": embedding_status,
                "memory_status": "duplicate",
                "candidate_matches": [],
            },
        }

    if action == "create_anyway":
        result = create_memory_from_text(
            text=text,
            db=db,
            extraction_provider=extraction_provider,
            embedding_provider=embedding_provider,
            skip_semantic_review=True,
        )

        resolution_status = (
            "duplicate"
            if result["memory_status"] == "duplicate"
            else "created"
        )

        return {
            "resolution_status": resolution_status,
            "result": result,
        }

    raise HTTPException(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Unsupported review resolution action",
    )
