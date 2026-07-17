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


def test_query_rejects_multi_entity_requests(
    client,
) -> None:
    response = client.post(
        "/query",
        json={
            "query": "Tell me about Laura and Robert",
        },
    )

    assert response.status_code == 501

    body = response.json()

    assert body["detail"]["message"] == ("Multi-entity queries are not implemented yet")
    assert body["detail"]["candidate_phrases"] == [
        "Laura",
        "Robert",
    ]
