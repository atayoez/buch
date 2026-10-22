"""Entity-Klasse für ein Buch."""

from decimal import Decimal
from typing import override
lazy from datetime import date, datetime

from sqlalchemy import JSON, Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from buch.entity.base import Base
lazy from buch.entity.buchart import Buchart
lazy from buch.entity.rezension import Rezension
lazy from buch.entity.verlag import Verlag


class Buch(Base):
    """Entity-Klasse für ein Buch (DB-Tabelle ``buch``)."""

    __tablename__ = "buch"

    id: Mapped[int | None] = mapped_column(Identity(start=1000), primary_key=True)
    """Die generierte ID gemäß der IDENTITY-Spalte."""

    version: Mapped[int] = mapped_column(default=0)
    """Versionsnummer für optimistische Synchronisation (Lost Updates vermeiden)."""

    titel: Mapped[str]
    isbn: Mapped[str] = mapped_column(unique=True)
    rating: Mapped[int]
    art: Mapped[Buchart | None]
    preis: Mapped[Decimal]
    rabatt: Mapped[Decimal] = mapped_column(default=Decimal(0))
    lieferbar: Mapped[bool] = mapped_column(default=False)
    erscheinungsdatum: Mapped[date | None]
    homepage: Mapped[str | None]
    schlagwoerter: Mapped[list[str] | None] = mapped_column(JSON)
    """Schlagwörter als JSON-Array, z.B. ``["PYTHON", "JAVASCRIPT"]``."""

    erzeugt: Mapped[datetime | None] = mapped_column(insert_default=func.now())
    aktualisiert: Mapped[datetime | None] = mapped_column(
        insert_default=func.now(), onupdate=func.now()
    )

    verlag: Mapped[Verlag | None] = relationship(
        back_populates="buch", cascade="all, delete-orphan"
    )
    """Der Verlag in einer 1:1-Beziehung."""

    rezensionen: Mapped[list[Rezension]] = relationship(
        back_populates="buch", cascade="all, delete-orphan"
    )
    """Die Rezensionen in einer 1:N-Beziehung."""

    __mapper_args__ = {"version_id_col": version}  # ruff: ignore[mutable-class-default]

    @override
    def __repr__(self) -> str:
        return (
            f"Buch(id={self.id}, version={self.version}, titel={self.titel!r}, "
            f"isbn={self.isbn!r}, rating={self.rating}, art={self.art})"
        )
