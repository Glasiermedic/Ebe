import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    (
        "entity_type",
        "create_path",
        "link_segment",
        "display_name",
        "relationship_type",
    ),
    [
        (
            "person",
            "/people",
            "people",
            "Laura Query Integration",
            "subject",
        ),
        (
            "place",
            "/places",
            "places",
            "Art Museum Query Integration",
            "location",
        ),
        (
            "event",
            "/events",
            "events",
            "Wedding Query Integration",
            "part_of",
        ),
    ],
)
def test_query_retrieves_serialized_memories_for_each_entity_type(
    client: TestClient,
    entity_type: str,
    create_path: str,
    link_segment: str,
    display_name: str,
    relationship_type: str,
) -> None:
    entity_response = client.post(
        create_path,
        json={"display_name": display_name},
    )

    assert entity_response.status_code == 201

    entity_id = entity_response.json()["id"]

    stone_response = client.post(
        "/stones",
        json={
            "title": f"Memory about {display_name}",
            "content": (
                f"This memory is connected to {display_name}."
            ),
            "importance": 0.8,
        },
    )

    assert stone_response.status_code == 201

    stone_id = stone_response.json()["id"]

    link_response = client.post(
        f"/stones/{stone_id}/{link_segment}",
        json={
            f"{entity_type}_id": entity_id,
            "relationship_type": relationship_type,
        },
    )

    assert link_response.status_code == 200

    response = client.post(
        "/query",
        json={
            "query": f"Tell me about {display_name}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["entity_type"] == entity_type
    assert body["entity"]["id"] == entity_id
    assert len(body["memories"]) == 1

    memory = body["memories"][0]

    assert memory["id"] == stone_id

    connections = memory[link_segment]

    assert connections == [
        {
            "relationship_type": relationship_type,
            entity_type: {
                **connections[0][entity_type],
                "id": entity_id,
            },
        }
    ]


def test_query_preserves_established_memory_order(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={
            "display_name": "Laura Query Ordering",
        },
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    lower_response = client.post(
        "/stones",
        json={
            "title": "Lower importance query memory",
            "content": "This memory should appear second.",
            "importance": 0.2,
        },
    )

    higher_response = client.post(
        "/stones",
        json={
            "title": "Higher importance query memory",
            "content": "This memory should appear first.",
            "importance": 0.9,
        },
    )

    assert lower_response.status_code == 201
    assert higher_response.status_code == 201

    lower_id = lower_response.json()["id"]
    higher_id = higher_response.json()["id"]

    for stone_id in (lower_id, higher_id):
        link_response = client.post(
            f"/stones/{stone_id}/people",
            json={
                "person_id": person_id,
                "relationship_type": "subject",
            },
        )

        assert link_response.status_code == 200

    response = client.post(
        "/query",
        json={
            "query": "Laura Query Ordering",
        },
    )

    assert response.status_code == 200

    memories = response.json()["memories"]

    assert [
        memory["id"]
        for memory in memories
    ] == [
        higher_id,
        lower_id,
    ]
