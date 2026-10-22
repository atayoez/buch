"""Repository für die Entity-Klasse Buch: lesende Zugriffe."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from buch.entity import Buch
lazy from buch.repository.buch_suchparameter import BuchSuchparameter

__all__ = ["BuchRepository"]


class BuchRepository:
    """Lesende Zugriffe auf die DB-Tabelle ``buch`` mit SQLAlchemy."""

    def find_by_id(self, buch_id: int, session: Session) -> Buch | None:
        """Suche mit der Buch-ID einschließlich Verlag und Rezensionen.

        Args:
            buch_id: ID des gesuchten Buches
            session: Session für SQLAlchemy

        Returns:
            Das gefundene Buch oder None
        """
        statement: Final = (
            select(Buch)
            .options(joinedload(Buch.verlag), selectinload(Buch.rezensionen))
            .where(Buch.id == buch_id)
        )
        buch: Final = session.scalar(statement)
        logger.debug("buch_id={}: {}", buch_id, buch)
        return buch

    def find(
        self, suchparameter: BuchSuchparameter, session: Session
    ) -> Sequence[Buch]:
        """Suche mit Suchparametern, die mit UND verknüpft werden.

        Args:
            suchparameter: Suchparameter, ggf. alle None
            session: Session für SQLAlchemy

        Returns:
            Die gefundenen Bücher, ggf. leer
        """
        statement = select(Buch).options(joinedload(Buch.verlag)).order_by(Buch.id)
        if suchparameter.titel is not None:
            statement = statement.where(Buch.titel.ilike(f"%{suchparameter.titel}%"))
        if suchparameter.isbn is not None:
            statement = statement.where(Buch.isbn == suchparameter.isbn)
        if suchparameter.rating is not None:
            statement = statement.where(Buch.rating >= suchparameter.rating)
        if suchparameter.art is not None:
            statement = statement.where(Buch.art == suchparameter.art)
        if suchparameter.lieferbar is not None:
            statement = statement.where(Buch.lieferbar == suchparameter.lieferbar)
        if suchparameter.schlagwort is not None:
            # JSONB-Operator "?" prüft, ob der String im JSON-Array enthalten ist
            statement = statement.where(
                func.jsonb_exists(Buch.schlagwoerter, suchparameter.schlagwort.upper())
            )
        buecher: Final = session.scalars(statement).all()
        logger.debug("{}: {} Treffer", suchparameter, len(buecher))
        return buecher

    def exists_isbn_other_id(self, isbn: str, buch_id: int, session: Session) -> bool:
        """Prüft, ob die ISBN bereits bei einem anderen Buch vorhanden ist.

        Args:
            isbn: die zu prüfende ISBN
            buch_id: ID des Buches, das selbst nicht zählt
            session: Session für SQLAlchemy

        Returns:
            True, falls ein anderes Buch diese ISBN hat
        """
        statement: Final = (
            select(func.count())
            .select_from(Buch)
            .where(Buch.isbn == isbn, Buch.id != buch_id)
        )
        return (session.scalar(statement) or 0) > 0

    def find_titel(self, teil: str, session: Session) -> Sequence[str]:
        """Titel suchen, die den Teilstring enthalten.

        Args:
            teil: Teilstring des Titels
            session: Session für SQLAlchemy

        Returns:
            Die gefundenen Titel, ggf. leer
        """
        statement: Final = (
            select(Buch.titel).where(Buch.titel.ilike(f"%{teil}%")).order_by(Buch.titel)
        )
        return session.scalars(statement).all()
