from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Person, PersonAlias


def normalize_entity_name(value: str) -> str:
    return " ".join(value.casefold().split())


def find_person_by_name(
    display_name: str,
    db: Session,
) -> Person | None:
    normalized_name = normalize_entity_name(display_name)

    people = db.scalars(select(Person)).all()

    exact_person = next(
        (
            person
            for person in people
            if normalize_entity_name(person.display_name)
            == normalized_name
        ),
        None,
    )

    if exact_person is not None:
        return exact_person

    alias = db.scalar(
        select(PersonAlias).where(
            PersonAlias.normalized_alias == normalized_name
        )
    )

    if alias is None:
        return None

    return alias.person
