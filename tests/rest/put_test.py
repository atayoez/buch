"""Integrationstests für PUT /rest/{id} mit Validierung und If-Match."""

from typing import Any

import pytest
from fastapi import status
lazy from fastapi.testclient import TestClient

REST = "/rest"
ID_UPDATE = 50
"""Epsilon: wird in diesen Tests geändert, die GET-Tests hängen nicht davon ab."""
ID_NICHT_VORHANDEN = 999_999
ISBN_ANDERES_BUCH = "978-3-16-148410-0"
"""ISBN von Alpha (ID 1)."""


def _aktuell(
    client: TestClient, buch_id: int = ID_UPDATE
) -> tuple[dict[str, Any], str]:
    """Aktuellen Datensatz und ETag lesen."""
    response = client.get(f"{REST}/{buch_id}")
    assert response.status_code == status.HTTP_200_OK
    return response.json(), response.headers["ETag"]


def _body(buch: dict[str, Any], **aenderungen: Any) -> dict[str, Any]:
    """Request-Body aus einem gelesenen Buch bauen, nur änderbare Attribute."""
    felder = (
        "titel", "isbn", "rating", "art", "preis", "rabatt", "lieferbar",
        "erscheinungsdatum", "homepage", "schlagwoerter",
    )  # fmt: skip
    return {feld: buch[feld] for feld in felder} | aenderungen


class TestPut:
    """PUT /rest/{id}."""

    def test_put(self, client: TestClient) -> None:
        """Gültige Daten mit aktuellem If-Match: 204, neue Version im ETag."""
        buch, etag = _aktuell(client)
        neuer_titel = f"{buch['titel']}-geaendert"

        response = client.put(
            f"{REST}/{ID_UPDATE}",
            json=_body(buch, titel=neuer_titel, rating=4, lieferbar=True),
            headers={"If-Match": etag},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.headers["ETag"] == f'"{buch["version"] + 1}"'
        danach, etag_danach = _aktuell(client)
        assert danach["titel"] == neuer_titel
        assert danach["rating"] == 4
        assert danach["lieferbar"] is True
        assert etag_danach == response.headers["ETag"]
        assert danach["verlag"] == buch["verlag"]

    def test_put_veraltete_version(self, client: TestClient) -> None:
        """If-Match mit alter Version: 412, nichts geändert (Lost Update vermieden)."""
        buch, etag = _aktuell(client)
        alte_version = f'"{buch["version"] - 1}"'

        response = client.put(
            f"{REST}/{ID_UPDATE}",
            json=_body(buch, titel="Lost Update"),
            headers={"If-Match": alte_version},
        )

        assert response.status_code == status.HTTP_412_PRECONDITION_FAILED
        assert "veraltet" in response.json()["detail"]
        danach, etag_danach = _aktuell(client)
        assert danach["titel"] == buch["titel"]
        assert etag_danach == etag

    def test_put_ohne_if_match(self, client: TestClient) -> None:
        """Header If-Match fehlt: 428."""
        buch, _ = _aktuell(client)

        response = client.put(f"{REST}/{ID_UPDATE}", json=_body(buch))

        assert response.status_code == status.HTTP_428_PRECONDITION_REQUIRED

    @pytest.mark.parametrize("if_match", ["0", '"abc"', '"', ""])
    def test_put_ungueltiges_if_match(self, client: TestClient, if_match: str) -> None:
        """If-Match nicht in der Form "<zahl>": 412."""
        buch, _ = _aktuell(client)

        response = client.put(
            f"{REST}/{ID_UPDATE}", json=_body(buch), headers={"If-Match": if_match}
        )

        assert response.status_code == status.HTTP_412_PRECONDITION_FAILED

    def test_put_nicht_vorhanden(self, client: TestClient) -> None:
        """Unbekannte ID: 404."""
        buch, _ = _aktuell(client)

        response = client.put(
            f"{REST}/{ID_NICHT_VORHANDEN}",
            json=_body(buch),
            headers={"If-Match": '"0"'},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "aenderung",
        [
            {"titel": ""},
            {"isbn": "123"},
            {"rating": 6},
            {"art": "COMIC"},
            {"preis": -1},
            {"rabatt": 1},
            {"unbekannt": "x"},
        ],
    )
    def test_put_ungueltige_daten(
        self, client: TestClient, aenderung: dict[str, Any]
    ) -> None:
        """Validierung durch Pydantic: 422 mit Fehlerliste, nichts geändert."""
        buch, etag = _aktuell(client)

        response = client.put(
            f"{REST}/{ID_UPDATE}",
            json=_body(buch, **aenderung),
            headers={"If-Match": etag},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json()["detail"]
        assert _aktuell(client)[1] == etag

    def test_put_isbn_vorhanden(self, client: TestClient) -> None:
        """ISBN eines anderen Buches: 422."""
        buch, etag = _aktuell(client)

        response = client.put(
            f"{REST}/{ID_UPDATE}",
            json=_body(buch, isbn=ISBN_ANDERES_BUCH),
            headers={"If-Match": etag},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert ISBN_ANDERES_BUCH in response.json()["detail"]
