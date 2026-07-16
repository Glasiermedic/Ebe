import uuid
from typing import Any, TypeVar

from fastapi import HTTPException, status
from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from app.models import Event, Person, Place
from app.serializers.memory_stones import serialize_memory_stone
from app.services.memory_stones import get_memory_stone_or_404


RelatedModel = TypeVar("RelatedModel", Person, Place, Event)


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