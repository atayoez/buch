"""Dependency Injection für die Router."""

from typing import Annotated

from fastapi import Depends
lazy from sqlalchemy.orm import Session

from buch.repository import BuchRepository, get_session
from buch.service import BuchService

__all__ = ["get_buch_service"]

_repo = BuchRepository()


def get_buch_service(session: Annotated[Session, Depends(get_session)]) -> BuchService:
    """Pro Request einen BuchService mit der injizierten Session erzeugen."""
    return BuchService(repo=_repo, session=session)
