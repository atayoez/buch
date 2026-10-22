"""Engine und Session-Factory für SQLAlchemy sowie die Dependency für FastAPI."""

from typing import Final
lazy from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from buch.config import db_settings

__all__ = ["SessionFactory", "engine", "get_session"]

engine: Final = create_engine(
    db_settings.url, pool_size=10, echo=db_settings.log_statements
)
"""Engine für SQLAlchemy: verwaltet den Connection-Pool."""

SessionFactory: Final = sessionmaker(bind=engine, autoflush=False)
"""Factory für Sessions, in denen die SQL-Anweisungen in Transaktionen laufen."""


def get_session() -> Iterator[Session]:
    """Dependency für FastAPI: eine Session pro Request, am Ende geschlossen."""
    with SessionFactory() as session:
        yield session
