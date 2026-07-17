from fastapi.testclient import TestClient


def test_get_person_memories_orders_by_importance(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={"display_name": "Laura Rolfson"},
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    lower_response = client.post(
        "/stones",
        json={
            "title": "Ordinary dinner",
            "content": "A normal dinner together.",
            "importance": 0.4,
        },
    )

    higher_response = client.post(
        "/stones",
        json={
            "title": "Wedding day",
            "content": "A defining family milestone.",
            "importance": 0.99,
        },
    )

    assert lower_response.status_code == 201
    assert higher_response.status_code == 201

    lower_id = lower_response.json()["id"]
    higher_id = higher_response.json()["id"]

    assert client.post(
        f"/stones/{lower_id}/people",
        json={
            "person_id": person_id,
            "relationship_type": "subject",
        },
    ).status_code == 200

    assert client.post(
        f"/stones/{higher_id}/people",
        json={
            "person_id": person_id,
            "relationship_type": "subject",
        },
    ).status_code == 200

    response = client.get(
        f"/people/{person_id}/memories"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["id"] == higher_id
    assert body[1]["id"] == lower_id


def test_get_person_memories_returns_empty_list(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={"display_name": "Robert"},
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    response = client.get(
        f"/people/{person_id}/memories"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_person_memories_rejects_missing_person(
    client: TestClient,
) -> None:
    response = client.get(
        "/people/00000000-0000-0000-0000-000000000000/memories"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Person not found"
    }
