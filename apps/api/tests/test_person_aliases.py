from fastapi.testclient import TestClient


def test_create_and_list_person_alias(
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

    alias_body = alias_response.json()

    assert alias_body["person_id"] == person_id
    assert alias_body["alias"] == "Laura"
    assert alias_body["normalized_alias"] == "laura"

    list_response = client.get(
        f"/people/{person_id}/aliases"
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["alias"] == "Laura"


def test_person_alias_is_case_insensitive(
    client: TestClient,
) -> None:
    first_person = client.post(
        "/people",
        json={"display_name": "Laura Rolfson"},
    ).json()

    second_person = client.post(
        "/people",
        json={"display_name": "Another Laura"},
    ).json()

    first_alias_response = client.post(
        f"/people/{first_person['id']}/aliases",
        json={"alias": "Laura"},
    )

    assert first_alias_response.status_code == 201

    duplicate_alias_response = client.post(
        f"/people/{second_person['id']}/aliases",
        json={"alias": "  LAURA  "},
    )

    assert duplicate_alias_response.status_code == 409


def test_reject_alias_matching_another_canonical_name(
    client: TestClient,
) -> None:
    laura_response = client.post(
        "/people",
        json={"display_name": "Laura Rolfson"},
    )

    wes_response = client.post(
        "/people",
        json={"display_name": "Wesley Rolfson"},
    )

    assert laura_response.status_code == 201
    assert wes_response.status_code == 201

    wes = wes_response.json()

    response = client.post(
        f"/people/{wes['id']}/aliases",
        json={"alias": "Laura Rolfson"},
    )

    assert response.status_code == 409
    