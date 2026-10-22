"""FastAPI-App mit einem ersten GET-Request."""

from fastapi import FastAPI
from uvicorn import run

app = FastAPI(title="buch")


@app.get("/")
def hello() -> dict[str, str]:
    """GET-Request für "Hello World"."""
    return {"message": "Hello World"}


def main() -> None:
    """Appserver mit uvicorn starten (siehe project.scripts in pyproject.toml)."""
    run("buch.main:app", host="127.0.0.1", port=8000)
