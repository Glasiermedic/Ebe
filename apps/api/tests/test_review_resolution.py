from fastapi.testclient import TestClient

from app.services import memory_creation


def test_resolution_uses_existing_memory(
    client: TestClient,
) -> None:
    stone_response = client.post(
        "/stones",
        json={
            "title": "First Date",
            "content": (
                "Laura and I talked until the "
                "restaurant closed."
            ),
        },
    )

    assert stone_response.status_code == 201

    stone = stone_response.json()

    response = client.post(
        "/remember/resolve",
        json={
            "text": (
                "Our first date lasted until "
                "the restaurant closed."
            ),
            "action": "use_existing",
            "existing_stone_id": stone["id"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["resolution_status"] == "used_existing"
    assert body["result"]["memory_status"] == "duplicate"
    assert body["result"]["stone"]["id"] == stone["id"]


def test_resolution_rejects_missing_existing_id(
    client: TestClient,
) -> None:
    response = client.post(
        "/remember/resolve",
        json={
            "text": "A possible duplicate memory.",
            "action": "use_existing",
            "existing_stone_id": None,
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "existing_stone_id is required when "
            "action is use_existing"
        )
    }


def test_resolution_creates_anyway(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        memory_creation,
        "review_memory",
        lambda **kwargs: [
            {
                "score": 0.99,
                "stone": {},
            }
        ],
    )

    response = client.post(
        "/remember/resolve",
        json={
            "text": (
                "Laura and I had another meaningful "
                "conversation over dinner."
            ),
            "action": "create_anyway",
            "existing_stone_id": None,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["resolution_status"] == "created"
    assert body["result"]["memory_status"] == "created"
    assert body["result"]["stone"] is not None
    assert body["result"]["candidate_matches"] == []


def test_resolution_rejects_missing_stone(
    client: TestClient,
) -> None:
    response = client.post(
        "/remember/resolve",
        json={
            "text": "A possible duplicate memory.",
            "action": "use_existing",
            "existing_stone_id": (
                "00000000-0000-0000-0000-000000000000"
            ),
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Memory Stone not found"
    }
