"""Router für lesende Zugriffe: GET /rest, GET /rest/{id}, GET /rest/titel/{teil}."""

from typing import Annotated, Final
lazy from collections.abc import Sequence

from fastapi import APIRouter, Depends, Header, Query, Response, status
from fastapi.responses import JSONResponse
from loguru import logger

from buch.router.buch_model import BuchFindModel, BuchModel
from buch.router.dependencies import get_buch_service
lazy from buch.repository import BuchSuchparameter
lazy from buch.service import BuchService

__all__ = ["buch_router"]

buch_router: Final = APIRouter(prefix="/rest", tags=["Lesen"])

ETAG: Final = "ETag"
IF_NONE_MATCH: Final = "If-None-Match"


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
    etag: Final = f'"{buch.version}"'
    if if_none_match == etag:
        logger.debug("buch_id={}: 304, version={}", buch_id, buch.version)
        return Response(status_code=status.HTTP_304_NOT_MODIFIED, headers={ETAG: etag})
    model: Final = BuchModel.model_validate(buch)
    return JSONResponse(content=model.model_dump(mode="json"), headers={ETAG: etag})


@buch_router.get(
    "",
    response_model=list[BuchModel],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Keine Bücher gefunden"}},
)
def get(
    find_model: Annotated[BuchFindModel, Query()],
    service: Annotated[BuchService, Depends(get_buch_service)],
) -> Sequence[BuchModel]:
    """Suche mit Query-Parametern, z.B. ``/rest?titel=a&art=HARDCOVER``.

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
