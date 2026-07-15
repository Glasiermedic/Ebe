from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.embeddings import get_embedding_provider


class FakeEmbeddingProvider:
    model_name = "fake-test-embedding"

    def embed(self, text: str) -> list[float]:
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
    assert body["embedded_at"]


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

    results = response.json()

    assert len(results) == 2
    assert results[0]["stone"]["id"] == family_id
    assert results[0]["score"] > results[1]["score"]