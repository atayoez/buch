"""Pydantic-Modelle für Request- und Response-Daten der REST-Schnittstelle."""

from decimal import Decimal
lazy from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

lazy from buch.entity import Buchart

__all__ = [
    "BuchFindModel",
    "BuchModel",
    "BuchUpdateModel",
    "RezensionModel",
    "VerlagModel",
]


class VerlagModel(BaseModel):
    """Verlag im Response-Body."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    ort: str | None


class RezensionModel(BaseModel):
    """Rezension im Response-Body."""

    model_config = ConfigDict(from_attributes=True)

    bewertung: int
    kommentar: str | None
    erzeugt: datetime | None


class BuchModel(BaseModel):
    """Buch im Response-Body, erzeugt aus der Entity-Klasse (``from_attributes``)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    version: int
    titel: str
    isbn: str
    rating: int
    art: Buchart | None
    preis: Decimal
    rabatt: Decimal
    lieferbar: bool
    erscheinungsdatum: date | None
    homepage: str | None
    schlagwoerter: list[str] | None
    verlag: VerlagModel | None
    rezensionen: list[RezensionModel] = []


class BuchFindModel(BaseModel):
    """Query-Parameter für GET /rest, validiert durch Pydantic."""

    model_config = ConfigDict(extra="forbid")

    titel: str | None = Field(default=None, max_length=100)
    isbn: str | None = Field(
        default=None, pattern=r"^97[89]-\d{1,5}-\d{1,7}-\d{1,7}-\d$"
    )
    rating: int | None = Field(default=None, ge=0, le=5)
    art: Buchart | None = None
    lieferbar: bool | None = None
    schlagwort: str | None = Field(default=None, max_length=50)


class BuchUpdateModel(BaseModel):
    """Request-Body für PUT /rest/{id}; Verlag und Rezensionen sind nicht änderbar."""

    model_config = ConfigDict(extra="forbid")

    titel: str = Field(min_length=1, max_length=100)
    isbn: str = Field(pattern=r"^97[89]-\d{1,5}-\d{1,7}-\d{1,7}-\d$")
    rating: int = Field(ge=0, le=5)
    art: Buchart | None = None
    preis: Decimal = Field(ge=0, max_digits=8, decimal_places=2)
    rabatt: Decimal = Field(
        default=Decimal(0), ge=0, lt=1, max_digits=4, decimal_places=3
    )
    lieferbar: bool = False
    erscheinungsdatum: date | None = None
    homepage: str | None = Field(default=None, max_length=200)
    schlagwoerter: list[str] | None = None
