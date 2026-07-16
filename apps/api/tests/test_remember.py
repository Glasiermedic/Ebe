from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import (
    ExtractedMemory,
    ExtractedPerson,
    ExtractedPlace,
)
from app.services.extraction import get_memory_extraction_provider

from app.services.embeddings import get_embedding_provider

from app.services import memory_creation

class FakeEmbeddingProvider:
    model_name = "fake-test-embedding"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * 1536
        vector[0] = 1.0
        return vector



class FakeMemoryExtractionProvider:
    person_name = "Laura Rolfson"
    def extract(self, text: str) -> ExtractedMemory:
        return ExtractedMemory(
            title="First Date",
            content=text,
            remembered_at=date(2010, 6, 12),
            people=[
                ExtractedPerson(
                    display_name=self.person_name,
                    relationship_type="subject",
                )
            ],
            places=[
                ExtractedPlace(
                    display_name=(
                        "Washington Square Cheesecake Factory"
                    ),
                    relationship_type="location",
                )
            ],
        )


@pytest.fixture(autouse=True)
def fake_providers() -> Generator[None, None, None]:
    app.dependency_overrides[
        get_memory_extraction_provider
    ] = FakeMemoryExtractionProvider

    app.dependency_overrides[
        get_embedding_provider
    ] = FakeEmbeddingProvider

    yield

    app.dependency_overrides.pop(
        get_memory_extraction_provider,
        None,
    )

    app.dependency_overrides.pop(
        get_embedding_provider,
        None,
    )

def test_remember_creates_connected_memory(
    client: TestClient,
) -> None:
    response = client.post(
        "/remember",
        json={
            "text": (
                "Met Laura at the Cheesecake Factory "
                "on our first date."
            )
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["stone"]["title"] == "First Date"
    assert body["stone"]["remembered_at"] == "2010-06-12"

    assert body["created_people"] == 1
    assert body["reused_people"] == 0
    assert body["created_places"] == 1
    assert body["reused_places"] == 0
    assert body["embedding_status"] == "generated"

    assert (
        body["stone"]["people"][0]["relationship_type"]
        == "subject"
    )

    assert (
        body["stone"]["people"][0]["person"]["display_name"]
        == "Laura Rolfson"
    )

    assert (
        body["stone"]["places"][0]["relationship_type"]
        == "location"
    )

def test_remember_reuses_existing_entities(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        memory_creation,
        "review_memory",
        lambda **kwargs: [],
    )

    first_payload = {
        "text": (
            "Met Laura at the Cheesecake Factory "
            "on our first date."
        )
    }

    second_payload = {
        "text": (
            "Laura and I stayed at the Cheesecake Factory "
            "talking late into the evening."
        )
    }

    first_response = client.post(
        "/remember",
        json=first_payload,
    )

    second_response = client.post(
        "/remember",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    second_body = second_response.json()

    assert second_body["memory_status"] == "created"
    assert second_body["created_people"] == 0
    assert second_body["reused_people"] == 1
    assert second_body["created_places"] == 0
    assert second_body["reused_places"] == 1


def test_remember_resolves_person_alias(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={
            "display_name": "Laura Rolfson",
            "description": "Wesley's wife",
        },
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    alias_response = client.post(
        f"/people/{person_id}/aliases",
        json={"alias": "Laura"},
    )

    assert alias_response.status_code == 201

    FakeMemoryExtractionProvider.person_name = "Laura"

    try:
        response = client.post(
            "/remember",
            json={
                "text": (
                    "Met Laura at the Cheesecake Factory "
                    "on our first date."
                )
            },
        )
    finally:
        FakeMemoryExtractionProvider.person_name = "Laura Rolfson"

    assert response.status_code == 201

    body = response.json()

    assert body["created_people"] == 0
    assert body["reused_people"] == 1

    connected_person = body["stone"]["people"][0]["person"]

    assert connected_person["id"] == person_id
    assert connected_person["display_name"] == "Laura Rolfson"
