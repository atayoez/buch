"""Erster Test: GET-Request auf "/" mit dem TestClient von FastAPI."""

from fastapi import status
lazy from fastapi.testclient import TestClient


def test_hello(client: TestClient) -> None:
    """GET / liefert 200 und "Hello World"."""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}


def test_post_creates_buch(client: TestClient) -> None:
    response = client.post("/buecher", json=valid_buch())

    assert response.status_code == 201

    data = response.json()
    assert data["id"] > 0
    assert data["titel"] == "Python für Einsteiger"
    assert data["isbn"] == "9781234567890"
    assert data["preis"] == "29.90"
    assert data["version"] >= 1


def test_post_rejects_invalid_price(client: TestClient) -> None:
    payload = {**valid_buch(), "preis": "-10.00"}

    response = client.post("/buecher", json=payload)

    assert response.status_code == 422


def test_post_rejects_unknown_fields(client: TestClient) -> None:
    payload = {**valid_buch(), "unexpected": "value"}

    response = client.post("/buecher", json=payload)

    assert response.status_code == 422


def test_put_updates_buch(client: TestClient) -> None:
    created = client.post("/buecher", json=valid_buch())
    assert created.status_code == 201
    buch = created.json()

    payload = {
        **valid_buch(),
        "titel": "Python für Fortgeschrittene",
        "expected_version": buch["version"],
    }

    response = client.put(
        f"/buecher/{buch['id']}",
        json=payload,
    )

    assert response.status_code == 200
    updated = response.json()

    assert updated["titel"] == "Python für Fortgeschrittene"
    assert updated["version"] > buch["version"]


def test_put_rejects_stale_version(client: TestClient) -> None:
    created = client.post("/buecher", json=valid_buch())
    assert created.status_code == 201
    buch = created.json()

    first_update = {
        **valid_buch(),
        "titel": "Aktualisierte Ausgabe",
        "expected_version": buch["version"],
    }

    response = client.put(
        f"/buecher/{buch['id']}",
        json=first_update,
    )
    assert response.status_code == 200

    stale_update = {
        **valid_buch(),
        "titel": "Veralteter Titel",
        "expected_version": buch["version"],
    }

    response = client.put(
        f"/buecher/{buch['id']}",
        json=stale_update,
    )

    assert response.status_code == 409

    current = client.get(f"/buecher/{buch['id']}")
    assert current.status_code == 200
    assert current.json()["titel"] == "Aktualisierte Ausgabe"


def test_put_rejects_missing_buch(client: TestClient) -> None:
    payload = {
        **valid_buch(),
        "expected_version": 1,
    }

    response = client.put("/buecher/999999", json=payload)

    assert response.status_code == 404


def test_put_rejects_invalid_data(client: TestClient) -> None:
    created = client.post("/buecher", json=valid_buch())
    buch = created.json()

    payload = {
        **valid_buch(),
        "preis": "-1.00",
        "expected_version": buch["version"],
    }

    response = client.put(
        f"/buecher/{buch['id']}",
        json=payload,
    )

    assert response.status_code == 422
