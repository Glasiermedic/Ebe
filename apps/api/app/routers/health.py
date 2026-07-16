from fastapi import APIRouter


router = APIRouter(
    tags=["health"],
)


@router.get("/")
async def root() -> dict[str, str]:
    return {
        "name": "Ebe",
        "status": "awake",
        "message": "The first stone has been placed.",
    }


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
