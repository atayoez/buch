"""Router der REST-Schnittstelle."""

from buch.router.buch_router import buch_router
from buch.router.buch_write_router import buch_write_router

__all__ = ["buch_router", "buch_write_router"]
