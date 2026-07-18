from sqlalchemy.orm import Session

from app.models import Event, MemoryStone, Person, Place
from app.services.query.models import (
    ResolvedEntity,
    RetrievalRequest,
    RetrievalResult,
)


class RetrievalService:
    def retrieve(
        self,
        request: RetrievalRequest,
        db: Session,
    ) -> RetrievalResult:
        if not request.resolved_entities:
            return RetrievalResult(memory_stones=())

        memory_stones_by_id: dict[object, MemoryStone] = {}

        for resolved_entity in request.resolved_entities:
            memory_stones = self._retrieve_single_entity(
                resolved_entity=resolved_entity,
                db=db,
            )

            for memory_stone in memory_stones:
                memory_stones_by_id.setdefault(
                    memory_stone.id,
                    memory_stone,
                )

        return RetrievalResult(
            memory_stones=tuple(memory_stones_by_id.values()),
        )

    def _retrieve_single_entity(
        self,
        *,
        resolved_entity: ResolvedEntity,
        db: Session,
    ) -> list[MemoryStone]:
        entity = resolved_entity.entity

        if resolved_entity.entity_type == "person":
            return (
                db.query(MemoryStone)
                .join(MemoryStone.people)
                .filter(Person.id == entity.id)
                .all()
            )

        if resolved_entity.entity_type == "place":
            return (
                db.query(MemoryStone)
                .join(MemoryStone.places)
                .filter(Place.id == entity.id)
                .all()
            )

        if resolved_entity.entity_type == "event":
            return (
                db.query(MemoryStone)
                .join(MemoryStone.events)
                .filter(Event.id == entity.id)
                .all()
            )

        raise ValueError(f"Unsupported entity type: {resolved_entity.entity_type}")
