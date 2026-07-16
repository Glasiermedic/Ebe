from fastapi import APIRouter, status
from sqlalchemy import select

from app.dependencies import DatabaseSession
from app.models import Place
from app.schemas import PlaceCreate, PlaceRead


router = APIRouter(
    prefix="/places",
    tags=["places"],
)


@router.post(
    "",
    response_model=PlaceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_place(
    place_data: PlaceCreate,
    db: DatabaseSession,
) -> Place:
    place = Place(**place_data.model_dump())

    db.add(place)
    db.commit()
    db.refresh(place)

    return place


@router.get(
    "",
    response_model=list[PlaceRead],
)
def list_places(
    db: DatabaseSession,
) -> list[Place]:
    statement = select(Place).order_by(Place.display_name)

    return list(db.scalars(statement).all())