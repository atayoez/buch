"""Integrationstests für POST /rest mit Validierung durch Pydantic."""

from secrets import randbelow
from typing import Any

import pytest
from fastapi import status
lazy from fastapi.testclient import TestClient

REST = "/rest"
ISBN_VORHANDEN = "978-3-16-148410-0"
"""ISBN von Alpha (ID 1)."""


def _neue_isbn() -> str:
    """Zufällige ISBN, damit die Tests mehrfach gegen dieselbe DB laufen können."""
    return f"978-3-{100 + randbelow(900)}-{10000 + randbelow(90000)}-{randbelow(10)}"


def _neues_buch(**aenderungen: Any) -> dict[str, Any]:
    """Gültiger Request-Body mit Verlag und zwei Rezensionen."""
    return {
        "titel": "Neues Buch",
        "isbn": _neue_isbn(),
        "rating": 3,
        "art": "EPUB",
        "preis": "19.99",
        "rabatt": "0.1",
        "lieferbar": True,
        "erscheinungsdatum": "2026-01-15",
        "homepage": "https://neu.example.com",
        "schlagwoerter": ["PYTHON", "FASTAPI"],
        "verlag": {"name": "Neuer Verlag", "ort": "Karlsruhe"},
        "rezensionen": [
            {"bewertung": 5, "kommentar": "Top"},
            {"bewertung": 2, "kommentar": None},
        ],
    } | aenderungen


class TestPost:
    """POST /rest."""

    def test_post(self, client: TestClient) -> None:
        """Gültige Daten: 201, Location und ETag; GET liefert Verlag und Rezensionen."""
        body = _neues_buch()

        response = client.post(REST, json=body)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.content == b""
        assert response.headers["ETag"] == '"0"'
        location = response.headers["Location"]
        neue_id = int(location.rsplit("/", 1)[-1])
        assert neue_id >= 1000  # IDENTITY startet bei 1000

        buch = client.get(f"{REST}/{neue_id}").json()
        assert buch["titel"] == body["titel"]
        assert buch["isbn"] == body["isbn"]
        assert buch["verlag"] == body["verlag"]
        assert [r["bewertung"] for r in buch["rezensionen"]] == [5, 2]

    def test_post_ohne_rezensionen(self, client: TestClient) -> None:
        """Rezensionen sind optional."""
        body = _neues_buch()
        del body["rezensionen"]

        response = client.post(REST, json=body)

        assert response.status_code == status.HTTP_201_CREATED
        neue_id = int(response.headers["Location"].rsplit("/", 1)[-1])
        assert client.get(f"{REST}/{neue_id}").json()["rezensionen"] == []

    def test_post_isbn_vorhanden(self, client: TestClient) -> None:
        """Bereits vorhandene ISBN: 422 mit Meldung."""
        response = client.post(REST, json=_neues_buch(isbn=ISBN_VORHANDEN))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert ISBN_VORHANDEN in response.json()["detail"]

    @pytest.mark.parametrize(
        "aenderung",
        [
            {"titel": ""},
            {"isbn": "123"},
            {"rating": 6},
            {"art": "COMIC"},
            {"preis": "-1"},
            {"rabatt": "1"},
            {"verlag": None},
            {"verlag": {"ort": "Karlsruhe"}},
            {"rezensionen": [{"bewertung": 0}]},
            {"unbekannt": "x"},
        ],
    )
    def test_post_ungueltige_daten(
        self, client: TestClient, aenderung: dict[str, Any]
    ) -> None:
        """Validierung durch Pydantic: 422 mit Fehlerliste."""
        response = client.post(REST, json=_neues_buch(**aenderung))

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"]

    def test_post_ohne_verlag(self, client: TestClient) -> None:
        """Verlag ist Pflicht (1:1): 422."""
        body = _neues_buch()
        del body["verlag"]

        response = client.post(REST, json=body)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
