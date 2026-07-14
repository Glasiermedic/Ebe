from fastapi.testclient import TestClient


def test_create_person(client: TestClient) -> None:
    response = client.post(
        "/people",
        json={
            "display_name": "Laura",
            "description": "A person represented in Ebe.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["display_name"] == "Laura"
    assert body["description"] == "A person represented in Ebe."
    assert body["id"]
    assert body["created_at"]


def test_link_person_to_memory_stone(client: TestClient) -> None:
    person_response = client.post(
        "/people",
        json={
            "display_name": "Robert",
            "description": "A person connected to a memory.",
        },
    )

    stone_response = client.post(
        "/stones",
        json={
            "title": "A connected memory",
            "content": "This memory concerns Robert.",
        },
    )

    person_id = person_response.json()["id"]
    stone_id = stone_response.json()["id"]

    response = client.post(
        f"/stones/{stone_id}/people",
        json={
            "person_id": person_id,
            "relationship_type": "subject",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["people"]) == 1
    assert body["people"][0]["id"] == person_id
    assert body["people"][0]["display_name"] == "Robert"


def test_reject_missing_person_link(client: TestClient) -> None:
    stone_response = client.post(
        "/stones",
        json={
            "title": "Missing person test",
            "content": "This link should fail.",
        },
    )

    stone_id = stone_response.json()["id"]

    response = client.post(
        f"/stones/{stone_id}/people",
        json={
            "person_id": "00000000-0000-0000-0000-000000000000",
            "relationship_type": "subject",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Person not found"}
