
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    MultiEntityQueryResultRead,
    QueryRequest,
    QueryResultRead,
)
from app.services.query_service import answer_query

router = APIRouter(
    prefix="/query",
    tags=["query"],
)


@router.post(
    "",
    response_model=(
        QueryResultRead | MultiEntityQueryResultRead
    ),
)
def query_memory(
    request: QueryRequest,
    db: Session = Depends(get_db),
) -> dict:
    return answer_query(
        query=request.query,
        db=db,
    )
    