"""FastAPI-App: Router registrieren und Exceptions auf Statuscodes abbilden."""

from typing import Final

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from uvicorn import run

from buch.router import buch_router, buch_write_router
from buch.service import IsbnExistsError, NotFoundError, VersionOutdatedError

app: Final = FastAPI(title="buch", version="2026.10.1")
app.include_router(buch_router)
app.include_router(buch_write_router)


@app.exception_handler(NotFoundError)
def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    """NotFoundError aus der Geschäftslogik als 404 mit JSON-Body."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
    )


@app.exception_handler(VersionOutdatedError)
def version_outdated_handler(
    _request: Request, exc: VersionOutdatedError
) -> JSONResponse:
    """Veraltete Version aus If-Match als 412 (Lost Update verhindert)."""
    return JSONResponse(
        status_code=status.HTTP_412_PRECONDITION_FAILED, content={"detail": exc.message}
    )


@app.exception_handler(IsbnExistsError)
def isbn_exists_handler(_request: Request, exc: IsbnExistsError) -> JSONResponse:
    """Bereits vorhandene ISBN als 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": exc.message},
    )


@app.get("/")
def hello() -> dict[str, str]:
    """GET-Request für "Hello World"."""
    return {"message": "Hello World"}


def main() -> None:
    """Appserver mit uvicorn starten (siehe project.scripts in pyproject.toml)."""
    run("buch.main:app", host="127.0.0.1", port=8000)
