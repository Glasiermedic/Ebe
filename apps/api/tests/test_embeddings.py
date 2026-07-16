from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.embeddings import get_embedding_provider


class FakeEmbeddingProvider:
    model_name = "fake-test-embedding"
    call_count = 0

    def embed(self, text: str) -> list[float]:
        type(self).call_count += 1

        vector = [0.0] * 1536
        normalized_text = text.lower()

        if any(
            phrase in normalized_text
            for phrase in ("family", "laura", "first date")
        ):
            vector[0] = 1.0
        elif any(
            phrase in normalized_text
            for phrase in ("weather", "storm", "rain")
        ):
            vector[1] = 1.0
        else:
            vector[2] = 1.0

        return vector


@pytest.fixture(autouse=True)
def fake_embedding_provider() -> Generator[None, None, None]:
    FakeEmbeddingProvider.call_count = 0

    app.dependency_overrides[get_embedding_provider] = (
        FakeEmbeddingProvider
    )

    yield

    app.dependency_overrides.pop(
        get_embedding_provider,
        None,
    )


def test_embed_memory_stone(client: TestClient) -> None:
    stone_response = client.post(
        "/stones",
        json={
            "title": "A family memory",
            "content": "A meaningful memory involving Laura.",
        },
    )

    stone_id = stone_response.json()["id"]

    response = client.post(f"/stones/{stone_id}/embed")

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == stone_id
    assert body["embedding_model"] == "fake-test-embedding"
    assert body["status"] == "generated"
    assert FakeEmbeddingProvider.call_count == 1


def test_unchanged_embedding_is_not_regenerated(
    client: TestClient,
) -> None:
    stone_response = client.post(
        "/stones",
        json={
            "title": "A stable memory",
            "content": "This content remains unchanged.",
        },
    )

    stone_id = stone_response.json()["id"]

    first_response = client.post(
        f"/stones/{stone_id}/embed"
    )
    second_response = client.post(
        f"/stones/{stone_id}/embed"
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "generated"

    assert second_response.status_code == 200
    assert second_response.json()["status"] == "current"

    assert FakeEmbeddingProvider.call_count == 1


def test_updating_content_invalidates_embedding(
    client: TestClient,
) -> None:
    stone_response = client.post(
        "/stones",
        json={
            "title": "Original title",
            "content": "Original content.",
        },
    )

    stone_id = stone_response.json()["id"]

    assert client.post(
        f"/stones/{stone_id}/embed"
    ).status_code == 200

    update_response = client.patch(
        f"/stones/{stone_id}",
        json={
            "content": "Updated semantic content.",
        },
    )

    assert update_response.status_code == 200

    embed_response = client.post(
        f"/stones/{stone_id}/embed"
    )

    assert embed_response.status_code == 200
    assert embed_response.json()["status"] == "generated"
    assert FakeEmbeddingProvider.call_count == 2


def test_semantic_search(client: TestClient) -> None:
    family_response = client.post(
        "/stones",
        json={
            "title": "First date",
            "content": "A meaningful evening with Laura.",
        },
    )

    weather_response = client.post(
        "/stones",
        json={
            "title": "Large storm",
            "content": "Heavy rain and strong wind.",
        },
    )

    family_id = family_response.json()["id"]
    weather_id = weather_response.json()["id"]

    assert client.post(
        f"/stones/{family_id}/embed"
    ).status_code == 200

    assert client.post(
        f"/stones/{weather_id}/embed"
    ).status_code == 200

    response = client.post(
        "/search/semantic",
        json={
            "query": "memories about Laura and family",
            "limit": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2

    assert "score" in body[0]
    assert "semantic_score" in body[0]
    assert "importance" in body[0]

    assert 0.0 <= body[0]["score"] <= 1.0
    assert 0.0 <= body[0]["semantic_score"] <= 1.0

    assert body[0]["stone"]["id"] == family_id
    assert body[0]["score"] > body[1]["score"]


def test_batch_embeds_pending_stones(
    client: TestClient,
) -> None:
    client.post(
        "/stones",
        json={
            "title": "First pending stone",
            "content": "Pending content one.",
        },
    )

    client.post(
        "/stones",
        json={
            "title": "Second pending stone",
            "content": "Pending content two.",
        },
    )

    response = client.post(
        "/stones/embed-pending",
        json={"limit": 10},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["scanned"] == 2
    assert body["embedded"] == 2
    assert body["skipped_current"] == 0
    assert len(body["stone_ids"]) == 2