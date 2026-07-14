import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import MemoryStone, Person, memory_stone_people
from app.schemas import (
    MemoryStoneCreate,
    MemoryStonePersonLinkCreate,
    MemoryStoneRead,
    PersonCreate,
    PersonRead,
)


app = FastAPI(
    title="Ebe API",
    description="The memory and context service for Ebe.",
    version="0.4.0",
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

    created_stone = db.scalar(
        select(MemoryStone)
        .options(selectinload(MemoryStone.people))
        .where(MemoryStone.id == stone.id)
    )

    if created_stone is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Stone could not be retrieved after creation",
        )

    return created_stone


@app.get("/stones", response_model=list[MemoryStoneRead])
def list_memory_stones(db: DatabaseSession) -> list[MemoryStone]:
    statement = (
        select(MemoryStone)
        .options(selectinload(MemoryStone.people))
        .order_by(MemoryStone.created_at.desc())
    )

    return list(db.scalars(statement).all())


@app.get("/stones/{stone_id}", response_model=MemoryStoneRead)
def get_memory_stone(
    stone_id: uuid.UUID,
    db: DatabaseSession,
) -> MemoryStone:
    stone = db.scalar(
        select(MemoryStone)
        .options(selectinload(MemoryStone.people))
        .where(MemoryStone.id == stone_id)
    )

    if stone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Stone not found",
        )

    return stone


@app.post(
    "/people",
    response_model=PersonRead,
    status_code=status.HTTP_201_CREATED,
)
def create_person(
    person_data: PersonCreate,
    db: DatabaseSession,
) -> Person:
    person = Person(**person_data.model_dump())

    db.add(person)
    db.commit()
    db.refresh(person)

    return person


@app.get("/people", response_model=list[PersonRead])
def list_people(db: DatabaseSession) -> list[Person]:
    statement = select(Person).order_by(Person.display_name)

    return list(db.scalars(statement).all())


@app.post(
    "/stones/{stone_id}/people",
    response_model=MemoryStoneRead,
)
def link_person_to_memory_stone(
    stone_id: uuid.UUID,
    link_data: MemoryStonePersonLinkCreate,
    db: DatabaseSession,
) -> MemoryStone:
    stone = db.get(MemoryStone, stone_id)

    if stone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Stone not found",
        )

    person = db.get(Person, link_data.person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    existing_link = db.execute(
        select(memory_stone_people).where(
            memory_stone_people.c.memory_stone_id == stone_id,
            memory_stone_people.c.person_id == link_data.person_id,
        )
    ).first()

    if existing_link is None:
        db.execute(
            memory_stone_people.insert().values(
                memory_stone_id=stone_id,
                person_id=link_data.person_id,
                relationship_type=link_data.relationship_type,
            )
        )
        db.commit()

    linked_stone = db.scalar(
        select(MemoryStone)
        .options(selectinload(MemoryStone.people))
        .where(MemoryStone.id == stone_id)
    )

    if linked_stone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Stone not found",
        )

    return linked_stone