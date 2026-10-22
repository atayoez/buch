"""Enum für die Art eines Buches."""

from enum import StrEnum


class Buchart(StrEnum):
    """Art eines Buches, entspricht dem Enum-Typ ``buchart`` in PostgreSQL."""

    HARDCOVER = "HARDCOVER"
    PAPERBACK = "PAPERBACK"
    EPUB = "EPUB"
