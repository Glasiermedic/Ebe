from fastapi.testclient import TestClient


def test_create_memory_stone(client: TestClient) -> None:
    response = client.post(
        "/stones",
        json={
            "title": "A test memory",
            "content": "This memory exists only inside the test database.",
            "stone_type": "test",
            "source_type": "conversation",
            "source_reference": "A direct conversation with the user",
            "remembered_at": "2026-07-14",
            "confidence": 0.875,
            "is_inferred": False,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == "A test memory"
    assert body["content"] == (
        "This memory exists only inside the test database."
    )
    assert body["stone_type"] == "test"
    assert body["source_type"] == "conversation"
    assert body["source_reference"] == (
        "A direct conversation with the user"
    )
    assert body["remembered_at"] == "2026-07-14"
    assert body["confidence"] == "0.875"
    assert body["is_inferred"] is False
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_memory_stone_with_defaults(
    client: TestClient,
) -> None:
    response = client.post(
        "/stones",
        json={
            "title": "Default provenance",
            "content": "This stone uses provenance defaults.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["stone_type"] == "memory"
    assert body["source_type"] == "user_entry"
    assert body["source_reference"] is None
    assert body["remembered_at"] is None
    assert body["confidence"] == "1.000"
    assert body["is_inferred"] is False


def test_list_memory_stones(client: TestClient) -> None:
    client.post(
        "/stones",
        json={
            "title": "First test stone",
            "content": "First test content",
            "stone_type": "test",
        },
    )

    client.post(
        "/stones",
        json={
            "title": "Second test stone",
            "content": "Second test content",
            "stone_type": "test",
        },
    )

    response = client.get("/stones")

    assert response.status_code == 200

    stones = response.json()

    assert len(stones) == 2
    assert {stone["title"] for stone in stones} == {
        "First test stone",
        "Second test stone",
    }


def test_get_memory_stone(client: TestClient) -> None:
    create_response = client.post(
        "/stones",
        json={
            "title": "Retrievable stone",
            "content": "This stone should be retrievable by ID.",
            "stone_type": "test",
        },
    )

    stone_id = create_response.json()["id"]

    response = client.get(f"/stones/{stone_id}")

    assert response.status_code == 200
    assert response.json()["id"] == stone_id
    assert response.json()["title"] == "Retrievable stone"


def test_get_missing_memory_stone(client: TestClient) -> None:
    response = client.get(
        "/stones/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Memory Stone not found"}


def test_reject_empty_memory_stone(client: TestClient) -> None:
    response = client.post(
        "/stones",
        json={
            "title": "",
            "content": "",
            "stone_type": "test",
        },
    )

    assert response.status_code == 422


def test_reject_invalid_confidence(client: TestClient) -> None:
    response = client.post(
        "/stones",
        json={
            "title": "Invalid confidence",
            "content": "Confidence cannot exceed one.",
            "confidence": 1.5,
        },
    )

    assert response.status_code == 422
