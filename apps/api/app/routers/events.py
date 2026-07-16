from fastapi import APIRouter, status
from sqlalchemy import select

from app.dependencies import DatabaseSession
from app.models import Event
from app.schemas import EventCreate, EventRead


router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.post(
    "",
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


@router.get(
    "",
    response_model=list[EventRead],
)
def list_events(
    db: DatabaseSession,
) -> list[Event]:
    statement = select(Event).order_by(
        Event.started_at.desc().nullslast(),
        Event.display_name,
    )

    return list(db.scalars(statement).all())