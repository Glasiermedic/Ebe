from fastapi.testclient import TestClient


def test_query_finds_person_by_canonical_name(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={
            "display_name": "Laura",
            "description": "A person stored in Ebe.",
        },
    )

    assert person_response.status_code == 201

    response = client.post(
        "/query",
        json={"query": "Tell me about Laura"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "Tell me about Laura"
    assert body["normalized_query"] == "Laura"
    assert body["entity_type"] == "person"
    assert body["matched_by"] == "canonical_name"
    assert body["matched_value"] == "Laura"
    assert body["entity"]["display_name"] == "Laura"


def test_query_finds_person_by_alias(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={
            "display_name": "Laura",
            "description": "A person stored in Ebe.",
        },
    )

    assert person_response.status_code == 201

    person_id = person_response.json()["id"]

    alias_response = client.post(
        f"/people/{person_id}/aliases",
        json={"alias": "Laurie"},
    )

    assert alias_response.status_code == 201

    response = client.post(
        "/query",
        json={"query": "Who is Laurie?"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == "Who is Laurie?"
    assert body["normalized_query"] == "Laurie"
    assert body["entity_type"] == "person"
    assert body["matched_by"] == "alias"
    assert body["matched_value"] == "Laurie"
    assert body["entity"]["id"] == person_id
    assert body["entity"]["display_name"] == "Laura"


def test_query_returns_404_for_unknown_entity(
    client: TestClient,
) -> None:
    response = client.post(
        "/query",
        json={"query": "Tell me about Nobody"},
    )

    assert response.status_code == 404


def test_query_returns_multi_entity_union(
    client: TestClient,
) -> None:
    laura_response = client.post(
        "/people",
        json={"display_name": "Laura Multi"},
    )

    robert_response = client.post(
        "/people",
        json={"display_name": "Robert Multi"},
    )

    assert laura_response.status_code == 201
    assert robert_response.status_code == 201

    laura_id = laura_response.json()["id"]
    robert_id = robert_response.json()["id"]

    shared_response = client.post(
        "/stones",
        json={
            "title": "Shared memory",
            "content": "Laura and Robert share this memory.",
            "importance": 0.9,
        },
    )

    laura_only_response = client.post(
        "/stones",
        json={
            "title": "Laura-only memory",
            "content": "This memory is connected only to Laura.",
            "importance": 0.2,
        },
    )

    robert_only_response = client.post(
        "/stones",
        json={
            "title": "Robert-only memory",
            "content": "This memory is connected only to Robert.",
            "importance": 0.6,
        },
    )

    assert shared_response.status_code == 201
    assert laura_only_response.status_code == 201
    assert robert_only_response.status_code == 201

    shared_id = shared_response.json()["id"]
    laura_only_id = laura_only_response.json()["id"]
    robert_only_id = robert_only_response.json()["id"]

    for stone_id in (shared_id, laura_only_id):
        response = client.post(
            f"/stones/{stone_id}/people",
            json={
                "person_id": laura_id,
                "relationship_type": "subject",
            },
        )

        assert response.status_code == 200

    for stone_id in (shared_id, robert_only_id):
        response = client.post(
            f"/stones/{stone_id}/people",
            json={
                "person_id": robert_id,
                "relationship_type": "subject",
            },
        )

        assert response.status_code == 200

    response = client.post(
        "/query",
        json={
            "query": (
                "Tell me about Laura Multi "
                "and Robert Multi"
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["query"] == (
        "Tell me about Laura Multi and Robert Multi"
    )

    assert body["normalized_query"] == (
        "Laura Multi and Robert Multi"
    )

    assert body["intent"] == "multi_entity"
    assert body["retrieval_strategy"] == "entity_union"

    assert [
        entity["entity"]["id"]
        for entity in body["entities"]
    ] == [
        laura_id,
        robert_id,
    ]

    assert [
        entity["matched_value"]
        for entity in body["entities"]
    ] == [
        "Laura Multi",
        "Robert Multi",
    ]

    assert [
        memory["id"]
        for memory in body["memories"]
    ] == [
        shared_id,
        laura_only_id,
        robert_only_id,
    ]


def test_multi_entity_query_preserves_alias_provenance(
    client: TestClient,
) -> None:
    laura_response = client.post(
        "/people",
        json={"display_name": "Laura Alias Multi"},
    )

    robert_response = client.post(
        "/people",
        json={"display_name": "Robert Alias Multi"},
    )

    assert laura_response.status_code == 201
    assert robert_response.status_code == 201

    laura_id = laura_response.json()["id"]

    alias_response = client.post(
        f"/people/{laura_id}/aliases",
        json={"alias": "Laurie Multi"},
    )

    assert alias_response.status_code == 201

    response = client.post(
        "/query",
        json={
            "query": (
                "Laurie Multi and Robert Alias Multi"
            ),
        },
    )

    assert response.status_code == 200

    entities = response.json()["entities"]

    assert entities[0]["matched_by"] == "alias"
    assert entities[0]["matched_value"] == "Laurie Multi"
    assert entities[0]["entity"]["id"] == laura_id

    assert entities[1]["matched_by"] == "canonical_name"
    assert entities[1]["matched_value"] == (
        "Robert Alias Multi"
    )


def test_multi_entity_query_rejects_unresolved_phrase(
    client: TestClient,
) -> None:
    laura_response = client.post(
        "/people",
        json={"display_name": "Laura Strict Multi"},
    )

    assert laura_response.status_code == 201

    response = client.post(
        "/query",
        json={
            "query": (
                "Laura Strict Multi and Missing Person"
            ),
        },
    )

    assert response.status_code == 404

    assert response.json() == {
        "detail": {
            "message": (
                "No matching person, place, or event found"
            ),
            "candidate_phrase": "Missing Person",
        }
    }


def test_multi_entity_query_supports_mixed_entity_types(
    client: TestClient,
) -> None:
    person_response = client.post(
        "/people",
        json={"display_name": "Laura Mixed Query"},
    )

    place_response = client.post(
        "/places",
        json={"display_name": "Art Museum Mixed Query"},
    )

    assert person_response.status_code == 201
    assert place_response.status_code == 201

    response = client.post(
        "/query",
        json={
            "query": (
                "Laura Mixed Query and "
                "Art Museum Mixed Query"
            ),
        },
    )

    assert response.status_code == 200

    entities = response.json()["entities"]

    assert [
        entity["entity_type"]
        for entity in entities
    ] == [
        "person",
        "place",
    ]

    assert [
        entity["entity"]["display_name"]
        for entity in entities
    ] == [
        "Laura Mixed Query",
        "Art Museum Mixed Query",
    ]
