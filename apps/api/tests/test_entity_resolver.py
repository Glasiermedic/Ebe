from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.query import entity_resolver
from app.services.query.models import (
    EntityType,
    MatchType,
    ResolvedEntity,
)


def make_resolved_entity(
    display_name: str,
    entity_type: EntityType = "person",
    matched_by: MatchType = "canonical_name",
) -> ResolvedEntity:
    """Create a lightweight resolved entity for unit testing."""
    entity = SimpleNamespace(
        display_name=display_name,
    )

    return ResolvedEntity(
        entity_type=entity_type,
        entity=entity,
        matched_by=matched_by,
        matched_value=display_name,
    )


@pytest.mark.parametrize(
    ("names", "resolved_by_name"),
    [
        (
            ("Laura", "Robert"),
            {
                "Laura": make_resolved_entity("Laura"),
                "Robert": make_resolved_entity("Robert"),
            },
        ),
        (
            ("Laura", "Hillsboro", "House Fire"),
            {
                "Laura": make_resolved_entity(
                    "Laura",
                    entity_type="person",
                ),
                "Hillsboro": make_resolved_entity(
                    "Hillsboro",
                    entity_type="place",
                ),
                "House Fire": make_resolved_entity(
                    "House Fire",
                    entity_type="event",
                ),
            },
        ),
        (
            ("Mom", "Dad"),
            {
                "Mom": make_resolved_entity(
                    "Laura's Mother",
                    matched_by="alias",
                ),
                "Dad": make_resolved_entity(
                    "Laura's Father",
                    matched_by="alias",
                ),
            },
        ),
    ],
)
def test_resolve_entities_returns_all_matches(
    monkeypatch: pytest.MonkeyPatch,
    names: tuple[str, ...],
    resolved_by_name: dict[str, ResolvedEntity],
) -> None:
    db = MagicMock()

    def fake_resolve_single_entity(
        name: str,
        db: MagicMock,
    ) -> ResolvedEntity | None:
        return resolved_by_name.get(name)

    monkeypatch.setattr(
        entity_resolver,
        "resolve_single_entity",
        fake_resolve_single_entity,
    )

    result = entity_resolver.resolve_entities(
        names=names,
        db=db,
    )

    assert len(result) == len(names)

    assert tuple(
        resolved.entity.display_name
        for resolved in result
    ) == tuple(
        resolved_by_name[name].entity.display_name
        for name in names
    )


@pytest.mark.parametrize(
    ("names", "missing_name"),
    [
        (
            ("Missing Person", "Robert"),
            "Missing Person",
        ),
        (
            ("Laura", "Missing Place", "House Fire"),
            "Missing Place",
        ),
        (
            ("Laura", "Robert", "Missing Event"),
            "Missing Event",
        ),
    ],
)
def test_resolve_entities_raises_404_when_any_name_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    names: tuple[str, ...],
    missing_name: str,
) -> None:
    db = MagicMock()

    def fake_resolve_single_entity(
        name: str,
        db: MagicMock,
    ) -> ResolvedEntity | None:
        if name == missing_name:
            return None

        return make_resolved_entity(name)

    monkeypatch.setattr(
        entity_resolver,
        "resolve_single_entity",
        fake_resolve_single_entity,
    )

    with pytest.raises(HTTPException) as exception_info:
        entity_resolver.resolve_entities(
            names=names,
            db=db,
        )

    error = exception_info.value

    assert error.status_code == 404
    assert error.detail == {
        "message": "No matching person, place, or event found",
        "candidate_phrase": missing_name,
    }


@pytest.mark.parametrize(
    "names",
    [
        (
            "Laura",
            "Robert",
            "Hillsboro",
        ),
        (
            "House Fire",
            "Hillsboro",
            "Laura",
        ),
        (
            "Robert",
            "Laura",
            "House Fire",
        ),
    ],
)
def test_resolve_entities_preserves_input_order(
    monkeypatch: pytest.MonkeyPatch,
    names: tuple[str, ...],
) -> None:
    db = MagicMock()

    def fake_resolve_single_entity(
        name: str,
        db: MagicMock,
    ) -> ResolvedEntity:
        return make_resolved_entity(name)

    monkeypatch.setattr(
        entity_resolver,
        "resolve_single_entity",
        fake_resolve_single_entity,
    )

    result = entity_resolver.resolve_entities(
        names=names,
        db=db,
    )

    resolved_names = tuple(
        resolved.entity.display_name
        for resolved in result
    )

    assert resolved_names == names