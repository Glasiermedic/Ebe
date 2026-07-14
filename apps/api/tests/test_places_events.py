from fastapi.testclient import TestClient


def test_create_place(client: TestClient) -> None:
    response = client.post(
        "/places",
        json={
            "display_name": "McMinnville, Oregon",
            "description": "A place represented in Ebe.",
            "latitude": 45.2101,
            "longitude": -123.1987,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["display_name"] == "McMinnville, Oregon"
    assert body["description"] == "A place represented in Ebe."
    assert body["latitude"] == "45.210100"
    assert body["longitude"] == "-123.198700"


def test_reject_invalid_place_coordinates(
    client: TestClient,
) -> None:
    response = client.post(
        "/places",
        json={
            "display_name": "Invalid place",
            "latitude": 100,
            "longitude": -200,
        },
    )

    assert response.status_code == 422


def test_create_event(client: TestClient) -> None:
    response = client.post(
        "/events",
        json={
            "display_name": "Ebe build day",
            "description": "The day the graph structure was expanded.",
            "started_at": "2026-07-14T13:00:00-07:00",
            "ended_at": "2026-07-14T17:00:00-07:00",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["display_name"] == "Ebe build day"
    assert body["started_at"] == "2026-07-14T20:00:00Z"
    assert body["ended_at"] == "2026-07-15T00:00:00Z"


def test_reject_event_with_invalid_date_order(
    client: TestClient,
) -> None:
    response = client.post(
        "/events",
        json={
            "display_name": "Invalid event",
            "started_at": "2026-07-14T17:00:00-07:00",
            "ended_at": "2026-07-14T13:00:00-07:00",
        },
    )

    assert response.status_code == 422


def test_link_place_to_memory_stone(
    client: TestClient,
) -> None:
    place_response = client.post(
        "/places",
        json={
            "display_name": "Saddle Mountain",
            "description": "A meaningful Oregon location.",
        },
    )

    stone_response = client.post(
        "/stones",
        json={
            "title": "A memory at Saddle Mountain",
            "content": "This memory occurred at Saddle Mountain.",
        },
    )

    place_id = place_response.json()["id"]
    stone_id = stone_response.json()["id"]

    response = client.post(
        f"/stones/{stone_id}/places",
        json={
            "place_id": place_id,
            "relationship_type": "location",
        },
    )

    assert response.status_code == 200

    assert response.status_code == 200

    body = response.json()

    assert len(body["places"]) == 1
    assert body["places"][0]["relationship_type"] == "location"
    assert body["places"][0]["place"]["id"] == place_id


def test_link_event_to_memory_stone(
    client: TestClient,
) -> None:
    event_response = client.post(
        "/events",
        json={
            "display_name": "Family memorial",
            "description": "A meaningful family event.",
            "started_at": "2026-08-20T10:00:00-07:00",
        },
    )

    stone_response = client.post(
        "/stones",
        json={
            "title": "A memorial memory",
            "content": "This memory is connected to the memorial.",
        },
    )

    event_id = event_response.json()["id"]
    stone_id = stone_response.json()["id"]

    response = client.post(
        f"/stones/{stone_id}/events",
        json={
            "event_id": event_id,
            "relationship_type": "occurred_during",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["events"]) == 1
    assert body["events"][0]["relationship_type"] == "occurred_during"
    assert body["events"][0]["event"]["id"] == event_id