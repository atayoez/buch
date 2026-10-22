"""Router für schreibende Zugriffe: PUT /rest/{id}."""

from typing import Annotated, Final

from fastapi import APIRouter, Depends, Header, Response, status
from loguru import logger

from buch.router.dependencies import get_buch_write_service
lazy from buch.router.buch_model import BuchUpdateModel
lazy from buch.service import BuchWriteService

__all__ = ["buch_write_router"]

buch_write_router: Final = APIRouter(prefix="/rest", tags=["Schreiben"])

ETAG: Final = "ETag"
IF_MATCH: Final = "If-Match"


@buch_write_router.put(
    "/{buch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Kein Buch mit dieser ID"},
        status.HTTP_412_PRECONDITION_FAILED: {
            "description": "If-Match ist ungültig oder die Version ist veraltet"
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Ungültige Daten oder ISBN bereits vorhanden"
        },
        status.HTTP_428_PRECONDITION_REQUIRED: {"description": "Header If-Match fehlt"},
    },
)
def put(
    buch_id: int,
    update_model: BuchUpdateModel,
    service: Annotated[BuchWriteService, Depends(get_buch_write_service)],
    if_match: Annotated[str | None, Header(alias=IF_MATCH)] = None,
) -> Response:
    """Ein Buch vollständig überschreiben.

    Der Header ``If-Match`` muss die zuletzt gelesene Versionsnummer enthalten,
    z.B. ``"0"`` aus dem ``ETag`` von ``GET /rest/{id}``. Damit werden Lost Updates
    vermieden. Antwort: 204 mit dem neuen ``ETag``.
    """
    logger.debug("buch_id={}, if_match={}, {}", buch_id, if_match, update_model)
    if if_match is None:
        return Response(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            content="Header If-Match fehlt",
        )
    version: Final = _parse_version(if_match)
    if version is None:
        return Response(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            content=f"Ungültiger Header If-Match: {if_match}",
        )
    buch: Final = service.update(
        buch_id=buch_id, version=version, daten=update_model.model_dump()
    )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT, headers={ETAG: f'"{buch.version}"'}
    )


def _parse_version(if_match: str) -> int | None:
    """Versionsnummer aus ``"<zahl>"`` lesen, sonst None."""
    min_len: Final = 3
    if len(if_match) < min_len or not (if_match[0] == if_match[-1] == '"'):
        return None
    try:
        return int(if_match[1:-1])
    except ValueError:
        return None
