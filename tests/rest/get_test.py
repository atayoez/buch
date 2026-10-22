"""Integrationstests für die GET-Requests der REST-Schnittstelle."""

import pytest
from fastapi import status
lazy from fastapi.testclient import TestClient

ID_VORHANDEN = 1
ID_NICHT_VORHANDEN = 999_999
REST = "/rest"


class TestGetById:
    """GET /rest/{id} mit Pfadparameter und bedingtem GET."""

    def test_get_by_id(self, client: TestClient) -> None:
        """Vorhandene ID: 200, Buch mit Verlag und Rezensionen, Header ETag."""
        response = client.get(f"{REST}/{ID_VORHANDEN}")

        assert response.status_code == status.HTTP_200_OK
        buch = response.json()
        assert buch["id"] == ID_VORHANDEN
        assert buch["titel"] == "Alpha"
        assert buch["verlag"]["name"] == "dpunkt.verlag"
        assert len(buch["rezensionen"]) == 2
        assert response.headers["ETag"] == f'"{buch["version"]}"'

    def test_get_by_id_not_modified(self, client: TestClient) -> None:
        """If-None-Match mit aktueller Version: 304 ohne Body."""
        etag = client.get(f"{REST}/{ID_VORHANDEN}").headers["ETag"]

        response = client.get(f"{REST}/{ID_VORHANDEN}", headers={"If-None-Match": etag})

        assert response.status_code == status.HTTP_304_NOT_MODIFIED
        assert response.content == b""

    def test_get_by_id_veraltete_version(self, client: TestClient) -> None:
        """If-None-Match mit anderer Version: 200 mit Body."""
        response = client.get(
            f"{REST}/{ID_VORHANDEN}", headers={"If-None-Match": '"-1"'}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_get_by_id_nicht_vorhanden(self, client: TestClient) -> None:
        """Unbekannte ID: 404 mit Meldung."""
        response = client.get(f"{REST}/{ID_NICHT_VORHANDEN}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert str(ID_NICHT_VORHANDEN) in response.json()["detail"]

    def test_get_by_id_ungueltig(self, client: TestClient) -> None:
        """ID ist keine Zahl: 422 durch die Validierung von FastAPI."""
        response = client.get(f"{REST}/abc")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGet:
    """GET /rest mit Query-Parametern."""

    def test_get_alle(self, client: TestClient) -> None:
        """Ohne Query-Parameter: alle Bücher, jeweils mit Verlag."""
        response = client.get(REST)

        assert response.status_code == status.HTTP_200_OK
        buecher = response.json()
        assert len(buecher) >= 5
        assert all(buch["verlag"] is not None for buch in buecher)

    @pytest.mark.parametrize("teil", ["a", "LPH", "gamma"])
    def test_get_titel_teil(self, client: TestClient, teil: str) -> None:
        """Teilstring des Titels, unabhängig von Groß-/Kleinschreibung."""
        response = client.get(REST, params={"titel": teil})

        assert response.status_code == status.HTTP_200_OK
        assert all(teil.lower() in buch["titel"].lower() for buch in response.json())

    def test_get_isbn(self, client: TestClient) -> None:
        """Exakte ISBN liefert genau ein Buch."""
        response = client.get(REST, params={"isbn": "978-3-16-148410-0"})

        assert response.status_code == status.HTTP_200_OK
        assert [buch["titel"] for buch in response.json()] == ["Alpha"]

    def test_get_art_und_rating(self, client: TestClient) -> None:
        """Mehrere Parameter werden mit UND verknüpft."""
        response = client.get(REST, params={"art": "HARDCOVER", "rating": 3})

        assert response.status_code == status.HTTP_200_OK
        buecher = response.json()
        assert len(buecher) >= 1
        assert all(b["art"] == "HARDCOVER" and b["rating"] >= 3 for b in buecher)

    def test_get_schlagwort(self, client: TestClient) -> None:
        """Schlagwort im JSON-Array."""
        response = client.get(REST, params={"schlagwort": "python"})

        assert response.status_code == status.HTTP_200_OK
        assert all("PYTHON" in buch["schlagwoerter"] for buch in response.json())

    def test_get_nicht_gefunden(self, client: TestClient) -> None:
        """Kein Treffer: 404."""
        response = client.get(REST, params={"titel": "gibt es nicht"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "params",
        [{"rating": 6}, {"art": "COMIC"}, {"isbn": "123"}, {"unbekannt": "x"}],
    )
    def test_get_ungueltige_parameter(
        self, client: TestClient, params: dict[str, str | int]
    ) -> None:
        """Ungültige oder unbekannte Query-Parameter: 422 durch Pydantic."""
        response = client.get(REST, params=params)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestGetTitel:
    """GET /rest/titel/{teil}."""

    def test_get_titel(self, client: TestClient) -> None:
        """Titel zum Teilstring als Liste von Strings."""
        response = client.get(f"{REST}/titel/a")

        assert response.status_code == status.HTTP_200_OK
        assert "Alpha" in response.json()

    def test_get_titel_nicht_gefunden(self, client: TestClient) -> None:
        """Kein Titel: 404."""
        response = client.get(f"{REST}/titel/xyz")

        assert response.status_code == status.HTTP_404_NOT_FOUND
