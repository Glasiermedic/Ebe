import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import DatabaseSession
from app.models import Person, PersonAlias
from app.schemas import (
    PersonAliasCreate,
    PersonAliasRead,
    PersonCreate,
    PersonRead,
    MemoryStoneRead,
    PersonContextRead,
)
from app.services.identity import normalize_entity_name

from app.services.graph_recall import (
    get_person_context,
    get_person_memories,
    get_person_timeline,
)

router = APIRouter(
    prefix="/people",
    tags=["people"],
)


@router.post(
    "",
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


@router.get(
    "",
    response_model=list[PersonRead],
)
def list_people(
    db: DatabaseSession,
) -> list[Person]:
    statement = select(Person).order_by(Person.display_name)

    return list(db.scalars(statement).all())


@router.post(
    "/{person_id}/aliases",
    response_model=PersonAliasRead,
    status_code=status.HTTP_201_CREATED,
)
def create_person_alias(
    person_id: uuid.UUID,
    alias_data: PersonAliasCreate,
    db: DatabaseSession,
) -> PersonAlias:
    person = db.get(Person, person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    normalized_alias = normalize_entity_name(alias_data.alias)

    canonical_match = next(
        (
            existing_person
            for existing_person in db.scalars(select(Person)).all()
            if normalize_entity_name(existing_person.display_name)
            == normalized_alias
        ),
        None,
    )

    if canonical_match is not None:
        detail = (
            "Alias matches this person's canonical name"
            if canonical_match.id == person.id
            else "Alias matches another person's canonical name"
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    alias = PersonAlias(
        person_id=person.id,
        alias=alias_data.alias.strip(),
        normalized_alias=normalized_alias,
    )

    db.add(alias)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alias is already assigned to a person",
        ) from error

    db.refresh(alias)

    return alias


@router.get(
    "/{person_id}/aliases",
    response_model=list[PersonAliasRead],
)
def list_person_aliases(
    person_id: uuid.UUID,
    db: DatabaseSession,
) -> list[PersonAlias]:
    person = db.get(Person, person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    statement = (
        select(PersonAlias)
        .where(PersonAlias.person_id == person_id)
        .order_by(PersonAlias.alias)
    )

    return list(db.scalars(statement).all())

@router.get(
    "/{person_id}/memories",
    response_model=list[MemoryStoneRead],
)
def list_person_memories(
    person_id: uuid.UUID,
    db: DatabaseSession,
) -> list[dict[str, Any]]:
    return get_person_memories(
        person_id=person_id,
        db=db,
    )
@router.get(
    "/{person_id}/timeline",
    response_model=list[MemoryStoneRead],
)
def list_person_timeline(
    person_id: uuid.UUID,
    db: DatabaseSession,
) -> list[dict[str, Any]]:
    return get_person_timeline(
        person_id=person_id,
        db=db,
    )
@router.get(
    "/{person_id}/context",
    response_model=PersonContextRead,
)
def get_context(
    person_id: uuid.UUID,
    db: DatabaseSession,
) -> dict[str, Any]:
    return get_person_context(
        person_id=person_id,
        db=db,
    )