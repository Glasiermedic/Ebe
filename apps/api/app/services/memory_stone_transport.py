from collections.abc import Sequence
from typing import Any

from sqlalchemy.orm import Session

from app.models import MemoryStone
from app.serializers.memory_stones import (
    serialize_memory_stone as serialize_loaded_memory_stone,
)
from app.serializers.memory_stones import (
    serialize_memory_stones as serialize_loaded_memory_stones,
)
from app.services.memory_stone_connections import (
    load_memory_stone_connections,
)


def serialize_memory_stone(
    stone: MemoryStone,
    db: Session,
) -> dict[str, Any]:
    connections_by_stone_id = load_memory_stone_connections(
        (stone,),
        db,
    )

    return serialize_loaded_memory_stone(
        stone,
        connections_by_stone_id[stone.id],
    )


def serialize_memory_stones(
    stones: Sequence[MemoryStone],
    db: Session,
) -> list[dict[str, Any]]:
    stone_list = list(stones)

    if not stone_list:
        return []

    connections_by_stone_id = load_memory_stone_connections(
        stone_list,
        db,
    )

    return serialize_loaded_memory_stones(
        stone_list,
        connections_by_stone_id,
    )
