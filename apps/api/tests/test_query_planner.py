import pytest

from app.services.query.planner import create_query_plan


@pytest.mark.parametrize(
    ("query_text", "expected_phrase"),
    [
        ("Laura", "Laura"),
        ("Art Museum", "Art Museum"),
        ("Robert", "Robert"),
    ],
)
def test_create_query_plan_for_single_entity(
    query_text: str,
    expected_phrase: str,
) -> None:
    plan = create_query_plan(query_text)

    assert plan.intent == "single_entity"
    assert plan.query_text == query_text
    assert plan.candidate_phrases == (expected_phrase,)


@pytest.mark.parametrize(
    ("query_text", "expected_phrases"),
    [
        (
            "Laura and Robert",
            ("Laura", "Robert"),
        ),
        (
            "Laura, Robert",
            ("Laura", "Robert"),
        ),
        (
            "Laura with Robert",
            ("Laura", "Robert"),
        ),
        (
            "Laura, Robert, and Art Museum",
            ("Laura", "Robert", "Art Museum"),
        ),
    ],
)
def test_create_query_plan_for_multiple_entities(
    query_text: str,
    expected_phrases: tuple[str, ...],
) -> None:
    plan = create_query_plan(query_text)

    assert plan.intent == "multi_entity"
    assert plan.query_text == query_text
    assert plan.candidate_phrases == expected_phrases


def test_create_query_plan_for_empty_query() -> None:
    plan = create_query_plan("   ")

    assert plan.intent == "unknown"
    assert plan.query_text == ""
    assert plan.candidate_phrases == ()
