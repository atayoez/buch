"""Gemeinsame Fixtures: TestClient für die FastAPI-App.

Die Integrationstests brauchen den PostgreSQL-Container aus
``extras/compose/postgres`` mit den Testdaten.
"""

lazy from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from buch import app


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Ein TestClient für alle Tests einer Session."""
    with TestClient(app) as test_client:
        yield test_client
