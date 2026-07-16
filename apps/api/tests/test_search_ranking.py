import pytest

from app.services.search import calculate_retrieval_score


def test_retrieval_score_combines_semantics_and_importance() -> None:
    score = calculate_retrieval_score(
        semantic_score=0.80,
        importance=1.00,
    )

    assert score == pytest.approx(0.83)


def test_semantic_relevance_remains_primary() -> None:
    highly_relevant = calculate_retrieval_score(
        semantic_score=0.95,
        importance=0.50,
    )

    less_relevant_but_important = calculate_retrieval_score(
        semantic_score=0.80,
        importance=1.00,
    )

    assert highly_relevant > less_relevant_but_important


def test_retrieval_score_is_clamped() -> None:
    high_score = calculate_retrieval_score(
        semantic_score=2.0,
        importance=2.0,
    )

    low_score = calculate_retrieval_score(
        semantic_score=-1.0,
        importance=-1.0,
    )

    assert high_score == 1.0
    assert low_score == 0.0