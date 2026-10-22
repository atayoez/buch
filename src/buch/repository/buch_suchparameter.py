"""Suchparameter für die Suche nach Büchern."""

from dataclasses import dataclass

lazy from buch.entity import Buchart

__all__ = ["BuchSuchparameter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class BuchSuchparameter:
    """Suchparameter für GET /rest mit Query-Parametern."""

    titel: str | None = None
    """Teilstring des Titels, Groß-/Kleinschreibung egal."""
    isbn: str | None = None
    """Exakte ISBN."""
    rating: int | None = None
    """Mindest-Rating."""
    art: Buchart | None = None
    lieferbar: bool | None = None
    schlagwort: str | None = None
    """Ein Schlagwort, das im JSON-Array enthalten sein muss."""

    def is_empty(self) -> bool:
        """Prüft, ob kein Suchparameter gesetzt ist."""
        return all(
            getattr(self, feld) is None
            for feld in ("titel", "isbn", "rating", "art", "lieferbar", "schlagwort")
        )
