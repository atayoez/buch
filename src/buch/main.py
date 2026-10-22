"""FastAPI-App mit einem ersten GET-Request."""

from fastapi import FastAPI
from uvicorn import run

app = FastAPI(title="buch")


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
