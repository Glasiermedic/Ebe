from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Event,
    MemoryStone,
    Person,
    Place,
    memory_stone_events,
    memory_stone_people,
    memory_stone_places,
)
from app.services.memory_stone_transport import serialize_memory_stone
from app.services.embeddings import EmbeddingProvider
from app.services.extraction import MemoryExtractionProvider
from app.services.identity import find_person_by_name
from app.services.memory_duplicates import calculate_memory_input_hash
from app.services.memory_review import review_memory
from app.services.memory_stones import generate_memory_stone_embedding


def normalize_entity_name(value: str) -> str:
    return " ".join(value.casefold().split())


def find_place_by_name(
    display_name: str,
    db: Session,
) -> Place | None:
    normalized_name = normalize_entity_name(display_name)

    places = db.scalars(select(Place)).all()

    return next(
        (
            place
            for place in places
            if normalize_entity_name(place.display_name)
            == normalized_name
        ),
        None,
    )


def find_event_by_name(
    display_name: str,
    db: Session,
) -> Event | None:
    normalized_name = normalize_entity_name(display_name)

    events = db.scalars(select(Event)).all()

    return next(
        (
            event
            for event in events
            if normalize_entity_name(event.display_name)
            == normalized_name
        ),
        None,
    )


def create_memory_from_text(
    *,
    text: str,
    db: Session,
    extraction_provider: MemoryExtractionProvider,
    embedding_provider: EmbeddingProvider,
    skip_semantic_review: bool = False,
) -> dict[str, Any]:
    source_text_hash = calculate_memory_input_hash(text)

    existing_stone = db.scalar(
        select(MemoryStone).where(
            MemoryStone.source_text_hash == source_text_hash
        )
    )

    if existing_stone is not None:
        embedding_status = generate_memory_stone_embedding(
            stone=existing_stone,
            embedding_provider=embedding_provider,
        )

        if embedding_status == "generated":
            db.commit()
            db.refresh(existing_stone)

        return {
            "stone": serialize_memory_stone(existing_stone, db),
            "created_people": 0,
            "reused_people": 0,
            "created_places": 0,
            "reused_places": 0,
            "created_events": 0,
            "reused_events": 0,
            "embedding_status": embedding_status,
            "memory_status": "duplicate",
            "candidate_matches": [],
        }

    if not skip_semantic_review:
        candidate_matches = review_memory(
            text=text,
            db=db,
            embedding_provider=embedding_provider,
        )

        if candidate_matches:
            return {
                "stone": None,
                "created_people": 0,
                "reused_people": 0,
                "created_places": 0,
                "reused_places": 0,
                "created_events": 0,
                "reused_events": 0,
                "embedding_status": None,
                "memory_status": "review",
                "candidate_matches": candidate_matches,
            }

    extracted = extraction_provider.extract(text)

    stone = MemoryStone(
        title=extracted.title,
        content=extracted.content,
        stone_type=extracted.stone_type,
        source_type=extracted.source_type,
        source_reference=extracted.source_reference,
        source_text_hash=source_text_hash,
        remembered_at=extracted.remembered_at,
        confidence=extracted.confidence,
        is_inferred=extracted.is_inferred,
        importance=extracted.importance,
    )

    db.add(stone)
    db.flush()

    created_people = 0
    reused_people = 0
    created_places = 0
    reused_places = 0
    created_events = 0
    reused_events = 0

    for extracted_person in extracted.people:
        person = find_person_by_name(
            extracted_person.display_name,
            db,
        )

        if person is None:
            person = Person(
                display_name=extracted_person.display_name,
                description=extracted_person.description,
            )
            db.add(person)
            db.flush()
            created_people += 1
        else:
            reused_people += 1

        db.execute(
            memory_stone_people.insert().values(
                memory_stone_id=stone.id,
                person_id=person.id,
                relationship_type=(
                    extracted_person.relationship_type
                ),
            )
        )

    for extracted_place in extracted.places:
        place = find_place_by_name(
            extracted_place.display_name,
            db,
        )

        if place is None:
            place = Place(
                display_name=extracted_place.display_name,
                description=extracted_place.description,
                latitude=extracted_place.latitude,
                longitude=extracted_place.longitude,
            )
            db.add(place)
            db.flush()
            created_places += 1
        else:
            reused_places += 1

        db.execute(
            memory_stone_places.insert().values(
                memory_stone_id=stone.id,
                place_id=place.id,
                relationship_type=(
                    extracted_place.relationship_type
                ),
            )
        )

    for extracted_event in extracted.events:
        event = find_event_by_name(
            extracted_event.display_name,
            db,
        )

        if event is None:
            event = Event(
                display_name=extracted_event.display_name,
                description=extracted_event.description,
                started_at=extracted_event.started_at,
                ended_at=extracted_event.ended_at,
            )
            db.add(event)
            db.flush()
            created_events += 1
        else:
            reused_events += 1

        db.execute(
            memory_stone_events.insert().values(
                memory_stone_id=stone.id,
                event_id=event.id,
                relationship_type=(
                    extracted_event.relationship_type
                ),
            )
        )

    embedding_status = generate_memory_stone_embedding(
        stone=stone,
        embedding_provider=embedding_provider,
    )

    db.commit()
    db.refresh(stone)

    return {
        "stone": serialize_memory_stone(stone, db),
        "created_people": created_people,
        "reused_people": reused_people,
        "created_places": created_places,
        "reused_places": reused_places,
        "created_events": created_events,
        "reused_events": reused_events,
        "embedding_status": embedding_status,
        "memory_status": "created",
        "candidate_matches": [],
    }
