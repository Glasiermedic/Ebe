from unittest.mock import Mock

from sqlalchemy.orm import Session

from app.services import memory_review


def test_review_returns_candidate(
    monkeypatch,
) -> None:
    candidate = {
    "score": 0.94,
    "semantic_score": 0.97,
    "importance": "0.800",
    "stone": {
        "id": "00000000-0000-0000-0000-000000000001",
        "title": "First Date",
    },
}

    search_mock = Mock(
        return_value=[
            candidate,
            {
                "score": 0.85,
                "semantic_score": 0.80,
                "importance": "1.000",
                "stone": {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "title": "Unrelated Memory",
                },
            },
        ]
    )

    monkeypatch.setattr(
        memory_review,
        "semantic_search_memory_stones",
        search_mock,
    )

    db = Mock(spec=Session)
    embedding_provider = Mock()

    results = memory_review.review_memory(
        text="Our first date lasted until closing.",
        db=db,
        embedding_provider=embedding_provider,
    )

    assert results == [candidate]

    search_mock.assert_called_once_with(
        query="Our first date lasted until closing.",
        limit=5,
        db=db,
        embedding_provider=embedding_provider,
    )


def test_review_returns_empty(
    monkeypatch,
) -> None:
    search_mock = Mock(
        return_value=[
            {
                "score": 0.90,
                "semantic_score": 0.89,
                "importance": "0.950",
                "stone": {
                        "id": "00000000-0000-0000-0000-000000000001",
                        "title": "Different Memory",
                },
}
        ]
    )

    monkeypatch.setattr(
        memory_review,
        "semantic_search_memory_stones",
        search_mock,
    )

    results = memory_review.review_memory(
        text="A genuinely new memory.",
        db=Mock(spec=Session),
        embedding_provider=Mock(),
    )

    assert results == []
