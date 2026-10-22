"""Basisklasse für alle Entity-Klassen."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Basisklasse für das OR-Mapping mit SQLAlchemy."""
