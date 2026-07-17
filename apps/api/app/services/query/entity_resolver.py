from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Event, Person, PersonAlias, Place
from app.services.query.models import ResolvedEntity


def resolve_person(
    name: str,
    db: Session,
) -> ResolvedEntity | None:
    normalized_name = name.strip().lower()

    person = (
        db.query(Person)
        .filter(func.lower(Person.display_name) == normalized_name)
        .first()
    )

    if person is not None:
        return ResolvedEntity(
            entity_type="person",
            entity=person,
            matched_by="canonical_name",
            matched_value=person.display_name,
        )

    aliases = (
        db.query(PersonAlias)
        .filter(func.lower(PersonAlias.alias) == normalized_name)
        .all()
    )

    if not aliases:
        return None

    unique_people = {alias.person_id: alias.person for alias in aliases}

    if len(unique_people) > 1:
        matches = sorted(
            unique_people.values(),
            key=lambda matched_person: matched_person.display_name.lower(),
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Alias matches more than one person",
                "alias": name,
                "matches": [
                    {
                        "id": str(matched_person.id),
                        "display_name": (matched_person.display_name),
                    }
                    for matched_person in matches
                ],
            },
        )

    alias = aliases[0]

    return ResolvedEntity(
        entity_type="person",
        entity=alias.person,
        matched_by="alias",
        matched_value=alias.alias,
    )


def resolve_place(
    name: str,
    db: Session,
) -> ResolvedEntity | None:
    normalized_name = name.strip().lower()

    place = (
        db.query(Place)
        .filter(func.lower(Place.display_name) == normalized_name)
        .first()
    )

    if place is None:
        return None

    return ResolvedEntity(
        entity_type="place",
        entity=place,
        matched_by="canonical_name",
        matched_value=place.display_name,
    )


def resolve_event(
    name: str,
    db: Session,
) -> ResolvedEntity | None:
    normalized_name = name.strip().lower()

    event = (
        db.query(Event)
        .filter(func.lower(Event.display_name) == normalized_name)
        .first()
    )

    if event is None:
        return None

    return ResolvedEntity(
        entity_type="event",
        entity=event,
        matched_by="canonical_name",
        matched_value=event.display_name,
    )


def resolve_single_entity(
    name: str,
    db: Session,
) -> ResolvedEntity | None:
    resolvers = (
        resolve_person,
        resolve_place,
        resolve_event,
    )

    for resolver in resolvers:
        result = resolver(
            name=name,
            db=db,
        )

        if result is not None:
            return result

    return None
