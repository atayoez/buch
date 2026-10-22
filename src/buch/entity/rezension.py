"""Entity-Klasse für eine Rezension zu einem Buch."""

from typing import override
lazy from datetime import datetime

from sqlalchemy import ForeignKey, Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from buch.entity.base import Base
lazy from buch.entity.buch import Buch


class Rezension(Base):
    """Entity-Klasse für eine Rezension (DB-Tabelle ``rezension``), N:1 zu ``buch``."""

    __tablename__ = "rezension"

    id: Mapped[int | None] = mapped_column(Identity(start=1000), primary_key=True)
    bewertung: Mapped[int]
    """Bewertung von 1 bis 5."""
    kommentar: Mapped[str | None]
    erzeugt: Mapped[datetime | None] = mapped_column(insert_default=func.now())

    buch_id: Mapped[int | None] = mapped_column(ForeignKey("buch.id"))
    buch: Mapped[Buch | None] = relationship(back_populates="rezensionen")

    @override
    def __repr__(self) -> str:
        return f"Rezension(id={self.id}, bewertung={self.bewertung})"
