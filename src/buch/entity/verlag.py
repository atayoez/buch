"""Entity-Klasse für den Verlag eines Buches."""

from typing import override

from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship

from buch.entity.base import Base
lazy from buch.entity.buch import Buch


class Verlag(Base):
    """Entity-Klasse für den Verlag (DB-Tabelle ``verlag``), 1:1 zu ``buch``."""

    __tablename__ = "verlag"

    id: Mapped[int | None] = mapped_column(Identity(start=1000), primary_key=True)
    name: Mapped[str]
    ort: Mapped[str | None]

    buch_id: Mapped[int | None] = mapped_column(ForeignKey("buch.id"), unique=True)
    """Fremdschlüssel; UNIQUE erzwingt die 1:1-Beziehung."""

    buch: Mapped[Buch | None] = relationship(back_populates="verlag")

    @override
    def __repr__(self) -> str:
        return f"Verlag(id={self.id}, name={self.name!r}, ort={self.ort!r})"
