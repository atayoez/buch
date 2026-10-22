"""Konfiguration für den Zugriff auf PostgreSQL.

Die Werte können über Umgebungsvariablen mit dem Präfix ``BUCH_DB_`` überschrieben
werden, z.B. ``BUCH_DB_HOST=db``. Die Defaults passen zu ``extras/compose/postgres``.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class DbSettings(BaseSettings):
    """Verbindungsdaten für PostgreSQL."""

    model_config = SettingsConfigDict(env_prefix="BUCH_DB_", env_file=".env")

    host: str = "localhost"
    port: int = 5432
    name: str = "buch"
    username: str = "buch"
    password: str = "p"  # ruff: ignore[hardcoded-password-string]
    log_statements: bool = True
    """SQL-Anweisungen von SQLAlchemy protokollieren."""

    @property
    def url(self) -> URL:
        """DB-URL für SQLAlchemy mit dem Treiber psycopg."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


db_settings = DbSettings()
