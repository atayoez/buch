"""Exceptions der Geschäftslogik, die der Router auf HTTP-Statuscodes abbildet."""

lazy from buch.repository import BuchSuchparameter

__all__ = ["NotFoundError"]


class NotFoundError(Exception):
    """Kein Buch bzw. keine Bücher gefunden."""

    def __init__(
        self,
        *,
        buch_id: int | None = None,
        suchparameter: BuchSuchparameter | None = None,
        teil: str | None = None,
    ) -> None:
        """Konstruktor; genau ein Argument beschreibt, wonach gesucht wurde."""
        if buch_id is not None:
            self.message = f"Kein Buch mit der ID {buch_id}"
        elif suchparameter is not None:
            self.message = f"Keine Bücher gefunden: {suchparameter}"
        elif teil is not None:
            self.message = f"Keine Titel mit {teil!r} gefunden"
        else:
            self.message = "Nicht gefunden"
        super().__init__(self.message)
