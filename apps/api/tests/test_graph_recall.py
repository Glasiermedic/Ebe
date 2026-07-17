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


def test_get_place_memories_orders_by_importance(
    client: TestClient,
) -> None:
    place_response = client.post(
        "/places",
        json={"display_name": "Home"},
    )

    assert place_response.status_code == 201

    place_id = place_response.json()["id"]

    lower_response = client.post(
        "/stones",
        json={
            "title": "Cleaning the garage",
            "content": "A routine afternoon at home.",
            "importance": 0.3,
        },
    )

    higher_response = client.post(
        "/stones",
        json={
            "title": "Bringing the baby home",
            "content": "The family arrived home together.",
            "importance": 0.95,
        },
    )

    assert lower_response.status_code == 201
    assert higher_response.status_code == 201

    lower_id = lower_response.json()["id"]
    higher_id = higher_response.json()["id"]

    assert client.post(
        f"/stones/{lower_id}/places",
        json={
            "place_id": place_id,
            "relationship_type": "location",
        },
    ).status_code == 200

    assert client.post(
        f"/stones/{higher_id}/places",
        json={
            "place_id": place_id,
            "relationship_type": "location",
        },
    ).status_code == 200

    response = client.get(
        f"/places/{place_id}/memories"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["id"] == higher_id
    assert body[1]["id"] == lower_id


def test_get_place_memories_rejects_missing_place(
    client: TestClient,
) -> None:
    response = client.get(
        "/places/00000000-0000-0000-0000-000000000000/memories"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Place not found"
    }


def test_get_event_memories_orders_by_importance(
    client: TestClient,
) -> None:
    event_response = client.post(
        "/events",
        json={"display_name": "Wedding"},
    )

    assert event_response.status_code == 201

    event_id = event_response.json()["id"]

    lower_response = client.post(
        "/stones",
        json={
            "title": "Choosing table linens",
            "content": "A small wedding-planning detail.",
            "importance": 0.25,
        },
    )

    higher_response = client.post(
        "/stones",
        json={
            "title": "Wedding vows",
            "content": "The vows spoken during the wedding.",
            "importance": 1.0,
        },
    )

    assert lower_response.status_code == 201
    assert higher_response.status_code == 201

    lower_id = lower_response.json()["id"]
    higher_id = higher_response.json()["id"]

    assert client.post(
        f"/stones/{lower_id}/events",
        json={
            "event_id": event_id,
            "relationship_type": "part_of",
        },
    ).status_code == 200

    assert client.post(
        f"/stones/{higher_id}/events",
        json={
            "event_id": event_id,
            "relationship_type": "part_of",
        },
    ).status_code == 200

    response = client.get(
        f"/events/{event_id}/memories"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["id"] == higher_id
    assert body[1]["id"] == lower_id


def test_get_event_memories_rejects_missing_event(
    client: TestClient,
) -> None:
    response = client.get(
        "/events/00000000-0000-0000-0000-000000000000/memories"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Event not found"
    }


def test_get_person_timeline_orders_by_remembered_date(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={"display_name": "Laura Timeline"},
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    later_response = client.post(
        "/stones",
        json={
            "title": "Later memory",
            "content": "This happened later.",
            "remembered_at": "2025-06-01",
            "importance": 1.0,
        },
    )

    earlier_response = client.post(
        "/stones",
        json={
            "title": "Earlier memory",
            "content": "This happened earlier.",
            "remembered_at": "2020-01-15",
            "importance": 0.2,
        },
    )

    undated_response = client.post(
        "/stones",
        json={
            "title": "Undated memory",
            "content": "The date is not known.",
            "importance": 0.9,
        },
    )

    assert later_response.status_code == 201
    assert earlier_response.status_code == 201
    assert undated_response.status_code == 201

    later_id = later_response.json()["id"]
    earlier_id = earlier_response.json()["id"]
    undated_id = undated_response.json()["id"]

    for stone_id in [
        later_id,
        earlier_id,
        undated_id,
    ]:
        relationship_response = client.post(
            f"/stones/{stone_id}/people",
            json={
                "person_id": person_id,
                "relationship_type": "subject",
            },
        )

        assert relationship_response.status_code == 200

    response = client.get(
        f"/people/{person_id}/timeline"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 3
    assert body[0]["id"] == earlier_id
    assert body[1]["id"] == later_id
    assert body[2]["id"] == undated_id


def test_get_person_timeline_returns_empty_list(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={"display_name": "Empty Timeline"},
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    response = client.get(
        f"/people/{person_id}/timeline"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_person_timeline_rejects_missing_person(
    client: TestClient,
) -> None:
    response = client.get(
        "/people/00000000-0000-0000-0000-000000000000/timeline"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Person not found"
    }
