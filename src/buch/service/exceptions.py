"""Exceptions der Geschäftslogik, die der Router auf HTTP-Statuscodes abbildet."""

lazy from buch.repository import BuchSuchparameter

__all__ = ["IsbnExistsError", "NotFoundError", "VersionOutdatedError"]


class NotFoundError(Exception):
    """Kein Buch bzw. keine Bücher gefunden (HTTP 404)."""

    def __init__(
        self,
        *,
        buch_id: int | None = None,
        isbn: str | None = None,
        suchparameter: BuchSuchparameter | None = None,
        teil: str | None = None,
    ) -> None:
        """Konstruktor; genau ein Argument beschreibt, wonach gesucht wurde."""
        if buch_id is not None:
            self.message = f"Kein Buch mit der ID {buch_id}"
        elif isbn is not None:
            self.message = f"Kein Buch mit der ISBN {isbn}"
        elif suchparameter is not None:
            self.message = f"Keine Bücher gefunden: {suchparameter}"
        elif teil is not None:
            self.message = f"Keine Titel mit {teil!r} gefunden"
        else:
            self.message = "Nicht gefunden"
        super().__init__(self.message)


class VersionOutdatedError(Exception):
    """Die Versionsnummer aus If-Match ist nicht aktuell (HTTP 412): Lost Update."""

    def __init__(self, version: int, aktuell: int) -> None:
        """Konstruktor mit der Version des Clients und der aktuellen Version."""
        self.message = f"Die Version {version} ist veraltet, aktuell ist {aktuell}"
        super().__init__(self.message)


class IsbnExistsError(Exception):
    """Die ISBN gehört bereits zu einem anderen Buch (HTTP 422)."""

    def __init__(self, isbn: str) -> None:
        """Konstruktor mit der bereits vorhandenen ISBN."""
        self.message = f"Die ISBN {isbn} existiert bereits"
        super().__init__(self.message)
