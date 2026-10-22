"""Repository für die Entity-Klasse Buch: lesende Zugriffe."""

from typing import Final
lazy from collections.abc import Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from buch.entity import Buch, Verlag
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

    def find_by_isbn(self, isbn: str, session: Session) -> Buch | None:
        """Suche mit der ISBN einschließlich Verlag und Rezensionen.

        Args:
            isbn: ISBN des gesuchten Buches
            session: Session für SQLAlchemy

        Returns:
            Das gefundene Buch oder None
        """
        statement: Final = (
            select(Buch)
            .options(joinedload(Buch.verlag), selectinload(Buch.rezensionen))
            .where(Buch.isbn == isbn)
        )
        buch: Final = session.scalar(statement)
        logger.debug("isbn={}: {}", isbn, buch)
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
        if suchparameter.verlag is not None or suchparameter.ort is not None:
            statement = statement.join(Buch.verlag)
        sp = suchparameter
        bedingungen = [
            (sp.id, lambda: Buch.id == sp.id),
            (sp.version, lambda: Buch.version == sp.version),
            (sp.titel, lambda: Buch.titel.ilike(f"%{sp.titel}%")),
            (sp.isbn, lambda: Buch.isbn == sp.isbn),
            (sp.rating, lambda: Buch.rating >= sp.rating),
            (sp.art, lambda: Buch.art == sp.art),
            (sp.preis, lambda: Buch.preis <= sp.preis),
            (sp.rabatt, lambda: Buch.rabatt >= sp.rabatt),
            (sp.lieferbar, lambda: Buch.lieferbar == sp.lieferbar),
            (
                sp.erscheinungsdatum,
                lambda: Buch.erscheinungsdatum == sp.erscheinungsdatum,
            ),
            (sp.homepage, lambda: Buch.homepage.ilike(f"%{sp.homepage}%")),
            # JSONB-Operator "?" prüft, ob der String im JSON-Array enthalten ist
            (
                sp.schlagwort,
                lambda: func.jsonb_exists(
                    Buch.schlagwoerter, str(sp.schlagwort).upper()
                ),
            ),
            (sp.verlag, lambda: Verlag.name.ilike(f"%{sp.verlag}%")),
            (sp.ort, lambda: Verlag.ort.ilike(f"%{sp.ort}%")),
        ]
        for wert, bedingung in bedingungen:
            if wert is not None:
                statement = statement.where(bedingung())
        buecher: Final = session.scalars(statement).all()
        logger.debug("{}: {} Treffer", suchparameter, len(buecher))
        return buecher

    def exists_isbn(self, isbn: str, session: Session) -> bool:
        """Prüft, ob es bereits ein Buch mit der ISBN gibt.

        Args:
            isbn: die zu prüfende ISBN
            session: Session für SQLAlchemy

        Returns:
            True, falls die ISBN vorhanden ist
        """
        statement: Final = (
            select(func.count()).select_from(Buch).where(Buch.isbn == isbn)
        )
        return (session.scalar(statement) or 0) > 0

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

    def save(self, buch: Buch, session: Session) -> Buch:
        """Ein neues Buch einschließlich Verlag und Rezensionen speichern.

        Args:
            buch: das neue Buch, noch ohne ID
            session: Session für SQLAlchemy

        Returns:
            Das gespeicherte Buch mit generierter ID
        """
        session.add(buch)
        session.flush()
        logger.debug("gespeichert: {}", buch)
        return buch

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
