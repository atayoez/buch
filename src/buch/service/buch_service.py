"""Geschäftslogik zum Lesen von Büchern."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
lazy from sqlalchemy.orm import Session

from buch.service.exceptions import NotFoundError
lazy from buch.entity import Buch
lazy from buch.repository import BuchRepository, BuchSuchparameter

__all__ = ["BuchService"]


class BuchService:
    """Service-Klasse für lesende Zugriffe; pro Request eine Instanz mit Session."""

    def __init__(self, repo: BuchRepository, session: Session) -> None:
        """Konstruktor mit injiziertem Repository und injizierter Session."""
        self.repo: Final = repo
        self.session: Final = session

    def find_by_id(self, buch_id: int) -> Buch:
        """Suche mit der Buch-ID.

        Raises:
            NotFoundError: Falls es kein Buch mit der ID gibt
        """
        buch: Final = self.repo.find_by_id(buch_id=buch_id, session=self.session)
        if buch is None:
            raise NotFoundError(buch_id=buch_id)
        return buch

    def find_by_isbn(self, isbn: str) -> Buch:
        """Suche mit der ISBN.

        Raises:
            NotFoundError: Falls es kein Buch mit der ISBN gibt
        """
        buch: Final = self.repo.find_by_isbn(isbn=isbn, session=self.session)
        if buch is None:
            raise NotFoundError(isbn=isbn)
        return buch

    def find(self, suchparameter: BuchSuchparameter) -> Sequence[Buch]:
        """Suche mit Suchparametern.

        Raises:
            NotFoundError: Falls kein Buch gefunden wurde
        """
        buecher: Final = self.repo.find(
            suchparameter=suchparameter, session=self.session
        )
        if len(buecher) == 0:
            raise NotFoundError(suchparameter=suchparameter)
        logger.debug("{} Bücher gefunden", len(buecher))
        return buecher

    def find_titel(self, teil: str) -> Sequence[str]:
        """Titel zum Teilstring suchen.

        Raises:
            NotFoundError: Falls kein Titel gefunden wurde
        """
        titel: Final = self.repo.find_titel(teil=teil, session=self.session)
        if len(titel) == 0:
            raise NotFoundError(teil=teil)
        return titel
