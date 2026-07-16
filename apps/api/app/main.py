import uuid
from typing import Annotated, Any, TypeVar



from app.serializers.memory_stones import serialize_memory_stone

from app.routers.people import router as people_router

from app.routers.remember import router as remember_router

from app.routers.places import router as places_router

from app.services.memory_stones import (
    generate_memory_stone_embedding,
    get_memory_stone_or_404,
)

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Event,
    MemoryStone,
    Person,
    Place,
    memory_stone_events,
    memory_stone_people,
    memory_stone_places,
)
from app.schemas import (
    EmbeddingBatchCreate,
    EmbeddingBatchRead,
    EventCreate,
    EventRead,
    MemoryStoneCreate,
    MemoryStoneEmbeddingRead,
    MemoryStoneEventLinkCreate,
    MemoryStonePersonLinkCreate,
    MemoryStonePlaceLinkCreate,
    MemoryStoneRead,
    MemoryStoneUpdate,
    SemanticSearchCreate,
    SemanticSearchResultRead,
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



def create_relationship(
    *,
    stone_id: uuid.UUID,
    related_id: uuid.UUID,
    related_model: type[RelatedModel],
    association_table: Table,
    related_column_name: str,
    relationship_type: str,
    missing_detail: str,
    db: Session,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)
    related_object = db.get(related_model, related_id)

    if related_object is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=missing_detail,
        )

    related_column = association_table.c[related_column_name]

    existing_link = db.execute(
        select(association_table).where(
            association_table.c.memory_stone_id == stone_id,
            related_column == related_id,
        )
    ).first()

    if existing_link is None:
        db.execute(
            association_table.insert().values(
                memory_stone_id=stone_id,
                **{
                    related_column_name: related_id,
                    "relationship_type": relationship_type,
                },
            )
        )
    else:
        db.execute(
            association_table.update()
            .where(
                association_table.c.memory_stone_id == stone_id,
                related_column == related_id,
            )
            .values(relationship_type=relationship_type)
        )

    db.commit()

    return serialize_memory_stone(stone, db)


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


@app.post(
    "/events",
    response_model=EventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    db: DatabaseSession,
) -> Event:
    event = Event(**event_data.model_dump())

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@app.get("/events", response_model=list[EventRead])
def list_events(db: DatabaseSession) -> list[Event]:
    statement = select(Event).order_by(
        Event.started_at.desc().nullslast(),
        Event.display_name,
    )

    return list(db.scalars(statement).all())


@app.post(
    "/stones/{stone_id}/people",
    response_model=MemoryStoneRead,
)
def link_person_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStonePersonLinkCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    return create_relationship(
        stone_id=stone_id,
        related_id=link_data.person_id,
        related_model=Person,
        association_table=memory_stone_people,
        related_column_name="person_id",
        relationship_type=link_data.relationship_type,
        missing_detail="Person not found",
        db=db,
    )


@app.post(
    "/stones/{stone_id}/places",
    response_model=MemoryStoneRead,
)
def link_place_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStonePlaceLinkCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    return create_relationship(
        stone_id=stone_id,
        related_id=link_data.place_id,
        related_model=Place,
        association_table=memory_stone_places,
        related_column_name="place_id",
        relationship_type=link_data.relationship_type,
        missing_detail="Place not found",
        db=db,
    )


@app.post(
    "/stones/{stone_id}/events",
    response_model=MemoryStoneRead,
)
def link_event_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStoneEventLinkCreate,
    db: DatabaseSession,
) -> dict[str, Any]:
    return create_relationship(
        stone_id=stone_id,
        related_id=link_data.event_id,
        related_model=Event,
        association_table=memory_stone_events,
        related_column_name="event_id",
        relationship_type=link_data.relationship_type,
        missing_detail="Event not found",
        db=db,
    )
@app.post(
    "/stones/{stone_id}/embed",
    response_model=MemoryStoneEmbeddingRead,
)
def embed_memory_stone(
    stone_id: uuid.UUID,
    db: DatabaseSession,
    embedding_provider: EmbeddingService,
) -> dict[str, Any]:
    stone = get_memory_stone_or_404(stone_id, db)

    embedding_status = generate_memory_stone_embedding(
        stone=stone,
        embedding_provider=embedding_provider,
    )

    if embedding_status == "generated":
        db.commit()
        db.refresh(stone)

    if stone.embedding_model is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding model metadata is missing",
        )

    if stone.embedded_at is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding timestamp is missing",
        )

    return {
        "id": stone.id,
        "embedding_model": stone.embedding_model,
        "embedded_at": stone.embedded_at,
        "status": embedding_status,
    }


@app.post(
    "/search/semantic",
    response_model=list[SemanticSearchResultRead],
)
def semantic_search(
    search_data: SemanticSearchCreate,
    db: DatabaseSession,
    embedding_provider: EmbeddingService,
) -> list[dict[str, Any]]:
    query_embedding = embedding_provider.embed(search_data.query)

    if len(query_embedding) != 1536:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding provider returned an unexpected vector dimension",
        )

    distance = MemoryStone.embedding.cosine_distance(
        query_embedding
    ).label("distance")

    statement = (
        select(MemoryStone, distance)
        .where(MemoryStone.embedding.is_not(None))
        .order_by(distance)
        .limit(search_data.limit)
    )

    rows = db.execute(statement).all()

    return [
        {
            "score": max(
                0.0,
                min(1.0, 1.0 - float(cosine_distance)),
            ),
            "stone": serialize_memory_stone(stone, db),
        }
        for stone, cosine_distance in rows
    ]
@app.post(
    "/stones/embed-pending",
    response_model=EmbeddingBatchRead,
)
def embed_pending_memory_stones(
    batch_data: EmbeddingBatchCreate,
    db: DatabaseSession,
    embedding_provider: EmbeddingService,
) -> dict[str, Any]:
    statement = (
        select(MemoryStone)
        .order_by(MemoryStone.created_at)
        .limit(batch_data.limit)
    )

    stones = list(db.scalars(statement).all())

    embedded_ids: list[uuid.UUID] = []
    skipped_current = 0

    for stone in stones:
        embedding_status = generate_memory_stone_embedding(
            stone=stone,
            embedding_provider=embedding_provider,
        )

        if embedding_status == "current":
            skipped_current += 1
        else:
            embedded_ids.append(stone.id)

    if embedded_ids:
        db.commit()

    return {
        "scanned": len(stones),
        "embedded": len(embedded_ids),
        "skipped_current": skipped_current,
        "stone_ids": embedded_ids,
    }

