"""Router für lesende Zugriffe.

GET /rest, GET /rest/{id}, GET /rest/isbn/{isbn} und GET /rest/titel/{teil}.
"""

from typing import Annotated, Final
lazy from collections.abc import Sequence

from fastapi import APIRouter, Depends, Header, Path, Query, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from buch.router.buch_model import BuchFindModel, BuchModel
from buch.router.dependencies import get_buch_service
lazy from buch.entity import Buch
lazy from buch.repository import BuchSuchparameter
lazy from buch.service import BuchService

__all__ = ["buch_router"]

buch_router: Final = APIRouter(prefix="/rest", tags=["Lesen"])

ETAG: Final = "ETag"
IF_NONE_MATCH: Final = "If-None-Match"
ISBN_PATTERN: Final = r"^97[89]-\d{1,5}-\d{1,7}-\d{1,7}-\d$"


@buch_router.get(
    "/{buch_id}",
    response_model=BuchModel,
    responses={
        status.HTTP_304_NOT_MODIFIED: {"description": "Unverändert seit If-None-Match"},
        status.HTTP_404_NOT_FOUND: {"description": "Kein Buch mit dieser ID"},
    },
)
def get_by_id(
    buch_id: int,
    service: Annotated[BuchService, Depends(get_buch_service)],
    if_none_match: Annotated[str | None, Header(alias=IF_NONE_MATCH)] = None,
) -> Response:
    """Suche mit der Buch-ID als Pfadparameter.

    Bedingter GET-Request: Der Header ``ETag`` enthält die Versionsnummer, z.B.
    ``"0"``. Schickt der Client sie als ``If-None-Match`` zurück und ist das Buch
    unverändert, antwortet der Server mit 304 ohne Body.
    """
    buch: Final = service.find_by_id(buch_id)
    return _response_mit_etag(buch, if_none_match)


@buch_router.get(
    "/isbn/{isbn}",
    response_model=BuchModel,
    responses={
        status.HTTP_304_NOT_MODIFIED: {"description": "Unverändert seit If-None-Match"},
        status.HTTP_404_NOT_FOUND: {"description": "Kein Buch mit dieser ISBN"},
    },
)
def get_by_isbn(
    isbn: Annotated[str, Path(pattern=ISBN_PATTERN)],
    service: Annotated[BuchService, Depends(get_buch_service)],
    if_none_match: Annotated[str | None, Header(alias=IF_NONE_MATCH)] = None,
) -> Response:
    """Suche mit der ISBN als Pfadparameter, z.B. ``/rest/isbn/978-3-16-148410-0``.

    Bedingter GET wie bei ``GET /rest/{id}``.
    """
    buch: Final = service.find_by_isbn(isbn)
    return _response_mit_etag(buch, if_none_match)


@buch_router.get(
    "",
    response_model=list[BuchModel],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Keine Bücher gefunden"}},
)
def get(
    find_model: Annotated[BuchFindModel, Query()],
    service: Annotated[BuchService, Depends(get_buch_service)],
) -> Sequence[BuchModel]:
    """Suche mit Query-Parametern, z.B. ``/rest?titel=a&art=HARDCOVER&verlag=hanser``.

    Jedes Attribut ist Suchparameter, siehe ``BuchFindModel``.
    Ohne Query-Parameter werden alle Bücher geliefert. Die Rezensionen werden bei
    der Suche nicht mitgeliefert, nur bei ``GET /rest/{id}``.
    """
    suchparameter: Final = BuchSuchparameter(**find_model.model_dump())
    buecher: Final = service.find(suchparameter)
    return [BuchModel.model_validate(buch) for buch in buecher]


@buch_router.get(
    "/titel/{teil}",
    response_model=list[str],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Keine Titel gefunden"}},
)
def get_titel(
    teil: str, service: Annotated[BuchService, Depends(get_buch_service)]
) -> Sequence[str]:
    """Titel suchen, die den Teilstring enthalten, z.B. für Autovervollständigung."""
    return service.find_titel(teil)


def _response_mit_etag(buch: Buch, if_none_match: str | None) -> Response:
    """Buch als JSON mit ETag, oder 304 falls If-None-Match die aktuelle Version ist."""
    etag: Final = f'"{buch.version}"'
    if if_none_match == etag:
        logger.debug("id={}: 304, version={}", buch.id, buch.version)
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers={ETAG: etag})
    model: Final = BuchModel.model_validate(buch)
    return JSONResponse(content=model.model_dump(mode="json"), headers={ETAG: etag})
