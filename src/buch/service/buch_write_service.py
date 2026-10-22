"""Geschäftslogik zum Ändern von Büchern."""

from typing import Any, Final

from loguru import logger
lazy from sqlalchemy.orm import Session

from buch.service.exceptions import IsbnExistsError, NotFoundError, VersionOutdatedError
lazy from buch.entity import Buch
lazy from buch.repository import BuchRepository

__all__ = ["BuchWriteService"]


class BuchWriteService:
    """Service-Klasse für schreibende Zugriffe; pro Request eine Instanz mit Session."""

    def __init__(self, repo: BuchRepository, session: Session) -> None:
        """Konstruktor mit injiziertem Repository und injizierter Session."""
        self.repo: Final = repo
        self.session: Final = session

    def update(self, buch_id: int, version: int, daten: dict[str, Any]) -> Buch:
        """Ein vorhandenes Buch mit neuen Daten überschreiben.

        Optimistische Synchronisation: Der Client schickt in ``If-Match`` die
        Versionsnummer, die er zuletzt gelesen hat. Stimmt sie nicht mit der DB
        überein, hat jemand anderes inzwischen geändert (Lost Update) und der
        Request wird mit 412 abgelehnt. Beim Commit erhöht SQLAlchemy die Version
        (``version_id_col``) und prüft sie zusätzlich im UPDATE.

        Args:
            buch_id: ID des zu ändernden Buches
            version: Versionsnummer aus If-Match
            daten: Die neuen Attributwerte (nur Attribute der Tabelle ``buch``)

        Returns:
            Das geänderte Buch mit der neuen Versionsnummer

        Raises:
            NotFoundError: Falls es kein Buch mit der ID gibt
            VersionOutdatedError: Falls die Versionsnummer nicht aktuell ist
            IsbnExistsError: Falls die neue ISBN zu einem anderen Buch gehört
        """
        logger.debug("buch_id={}, version={}, daten={}", buch_id, version, daten)
        buch: Final = self.repo.find_by_id(buch_id=buch_id, session=self.session)
        if buch is None:
            raise NotFoundError(buch_id=buch_id)
        if buch.version != version:
            raise VersionOutdatedError(version=version, aktuell=buch.version)
        isbn: Final = daten.get("isbn")
        if (
            isbn is not None
            and isbn != buch.isbn
            and self.repo.exists_isbn_other_id(
                isbn=isbn, buch_id=buch_id, session=self.session
            )
        ):
            raise IsbnExistsError(isbn)

        for attribut, wert in daten.items():
            setattr(buch, attribut, wert)
        self.session.commit()
        self.session.refresh(buch)
        logger.debug("aktualisiert: {}", buch)
        return buch
