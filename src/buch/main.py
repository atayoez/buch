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

@app.post(
    "/buecher",
    response_model=BuchResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_buch(
    payload: BuchCreate,
    db: Session = Depends(get_db),
) -> Buch:
    buch = Buch(**payload.model_dump())
    db.add(buch)

    try:
        db.commit()
        db.refresh(buch)
    except Exception:
        db.rollback()
        raise

    return buch


@app.put(
    "/buecher/{buch_id}",
    response_model=BuchResponse,
)
def update_buch(
    buch_id: int,
    payload: BuchPut,
    db: Session = Depends(get_db),
) -> Buch:
    buch = db.get(Buch, buch_id)

    if buch is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buch nicht gefunden",
        )

    if buch.version != payload.expected_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Das Buch wurde zwischenzeitlich geändert.",
        )

    data = payload.model_dump(exclude={"expected_version"})
    for field, value in data.items():
        if field == "homepage" and value is not None:
            value = str(value)
        setattr(buch, field, value)

    try:
        db.commit()
        db.refresh(buch)
    except StaleDataError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Das Buch wurde parallel geändert. Bitte neu laden.",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return buch

def main() -> None:
    """Appserver mit uvicorn starten (siehe project.scripts in pyproject.toml)."""
    run("buch.main:app", host="127.0.0.1", port=8000)
