import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MemoryStone
from app.schemas import MemoryStoneCreate, MemoryStoneRead


app = FastAPI(
    title="Ebe API",
    description="The memory and context service for Ebe.",
    version="0.3.0",
)

DatabaseSession = Annotated[Session, Depends(get_db)]


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
) -> MemoryStone:
    stone = MemoryStone(**stone_data.model_dump())

    db.add(stone)
    db.commit()
    db.refresh(stone)

    return stone


@app.get("/stones", response_model=list[MemoryStoneRead])
def list_memory_stones(db: DatabaseSession) -> list[MemoryStone]:
    statement = select(MemoryStone).order_by(MemoryStone.created_at.desc())
    return list(db.scalars(statement).all())


@app.get("/stones/{stone_id}", response_model=MemoryStoneRead)
def get_memory_stone(
    stone_id: uuid.UUID,
    db: DatabaseSession,
) -> MemoryStone:
    stone = db.get(MemoryStone, stone_id)

    if stone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Stone not found",
        )

    return stone
