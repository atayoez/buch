"""Erster Test: GET-Request auf "/" mit dem TestClient von FastAPI."""

from fastapi import status
lazy from fastapi.testclient import TestClient


def test_hello(client: TestClient) -> None:
    """GET / liefert 200 und "Hello World"."""
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}
