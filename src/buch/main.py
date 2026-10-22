"""FastAPI-App: Router registrieren und Exceptions auf Statuscodes abbilden."""

from typing import Final

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from uvicorn import run

from buch.router import buch_router
from buch.service import NotFoundError

app: Final = FastAPI(title="buch", version="2026.10.1")
app.include_router(buch_router)


@app.exception_handler(NotFoundError)
def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    """NotFoundError aus der Geschäftslogik als 404 mit JSON-Body."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": exc.message}
    )


@app.get("/")
def hello() -> dict[str, str]:
    """GET-Request für "Hello World"."""
    return {"message": "Hello World"}


def main() -> None:
    """Appserver mit uvicorn starten (siehe project.scripts in pyproject.toml)."""
    run("buch.main:app", host="127.0.0.1", port=8000)
