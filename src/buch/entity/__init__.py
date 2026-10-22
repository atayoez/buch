"""Entity-Klassen für das OR-Mapping mit SQLAlchemy."""

from buch.entity.base import Base
from buch.entity.buch import Buch
from buch.entity.buchart import Buchart
from buch.entity.rezension import Rezension
from buch.entity.verlag import Verlag

__all__ = ["Base", "Buch", "Buchart", "Rezension", "Verlag"]
