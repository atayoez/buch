"""Suchparameter für die Suche nach Büchern."""

from dataclasses import dataclass, fields
lazy from datetime import date
lazy from decimal import Decimal

lazy from buch.entity import Buchart

__all__ = ["BuchSuchparameter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class BuchSuchparameter:
    """Suchparameter für GET /rest; alle gesetzten Parameter werden mit UND verknüpft.

    Semantik: exakter Vergleich, außer wo anders angegeben.
    """

    id: int | None = None
    version: int | None = None
    titel: str | None = None
    """Teilstring, Groß-/Kleinschreibung egal."""
    isbn: str | None = None
    rating: int | None = None
    """Mindestens."""
    art: Buchart | None = None
    preis: Decimal | None = None
    """Höchstens."""
    rabatt: Decimal | None = None
    """Mindestens."""
    lieferbar: bool | None = None
    erscheinungsdatum: date | None = None
    homepage: str | None = None
    """Teilstring, Groß-/Kleinschreibung egal."""
    schlagwort: str | None = None
    """Ein Schlagwort, das im JSON-Array enthalten sein muss."""
    verlag: str | None = None
    """Teilstring des Verlagsnamens, Groß-/Kleinschreibung egal."""
    ort: str | None = None
    """Teilstring des Verlagsorts, Groß-/Kleinschreibung egal."""

    def is_empty(self) -> bool:
        """Prüft, ob kein Suchparameter gesetzt ist."""
        return all(getattr(self, feld.name) is None for feld in fields(self))
