# buch

Projekt für die Vorlesung _KI-gestützte Serverentwicklung_ (WS 2026/27, Hochschule Karlsruhe).

Appserver mit _FastAPI_, _Pydantic_ und _SQLAlchemy_ für _PostgreSQL_, verwaltet mit _uv_.

Domäne: `Buch` mit genau einem `Verlag` (1:1) und beliebig vielen `Rezensionen` (1:N).

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Repository klonen](#repository-klonen)
- [Datenbank starten](#datenbank-starten)
- [Datenbank zurücksetzen](#datenbank-zurücksetzen)
- [DB-Browser](#db-browser)
- [Appserver](#appserver)
  - [REST-Schnittstelle (GET)](#rest-schnittstelle-get)
  - [REST-Schnittstelle (POST)](#rest-schnittstelle-post)
  - [REST-Schnittstelle (PUT)](#rest-schnittstelle-put)
- [Tests](#tests)
  - [pytest](#pytest)
  - [Bruno](#bruno)
- [Codeanalyse, Formatierung und Typprüfung](#codeanalyse-formatierung-und-typprüfung)
- [Checkliste der Vorlesung](#checkliste-der-vorlesung)
- [Hinweis für Linux mit podman](#hinweis-für-linux-mit-podman)

## Voraussetzungen

- Git
- Docker mit Docker Compose (für PostgreSQL)
- _uv_ (installiert Python 3.15 bei Bedarf selbst)

## Repository klonen

```shell
git clone https://github.com/atayoez/buch.git
cd buch
```

## Datenbank starten

PostgreSQL 18 läuft als Docker Container mit dem offiziellen Image von Docker Hub.
Beim **ersten** Start legt der Container automatisch den DB-User `buch` (Passwort `p`),
die Datenbank `buch` und das Schema `buch` an und führt die Skripte aus
`extras/compose/postgres/init` aus:

| Skript                 | Zweck                                               |
| ---------------------- | --------------------------------------------------- |
| `01-create-schema.sql` | Schema `buch`                                       |
| `02-create.sql`        | Tabellen `buch`, `verlag` (1:1), `rezension` (1:N)  |
| `03-insert.sql`        | Testdaten                                           |

```shell
cd extras/compose/postgres
docker compose up
```

Der Container heißt `buch-postgres` und ist unter `localhost:5432` erreichbar.
Die Daten liegen im Named Volume `buch_pg_data` und bleiben bei `docker compose down`
erhalten.

Überprüfen (in einer zweiten Shell):

```shell
docker exec -e PGPASSWORD=p buch-postgres psql --dbname=buch --username=buch \
  -c "SELECT b.id, b.titel, v.name AS verlag, count(r.id) AS rezensionen
      FROM buch b JOIN verlag v ON v.buch_id = b.id
      LEFT JOIN rezension r ON r.buch_id = b.id
      GROUP BY b.id, b.titel, v.name ORDER BY b.id;"
```

Erwartet werden 5 Bücher mit jeweils einem Verlag und 0 bis 3 Rezensionen.

`psql` interaktiv:

```shell
docker exec -it -e PGPASSWORD=p buch-postgres psql --dbname=buch --username=buch
```

## Datenbank zurücksetzen

Komplett neu aufsetzen (Volume löschen, nächster Start führt die Init-Skripte erneut aus):

```shell
cd extras/compose/postgres
docker compose down -v
docker compose up
```

Nur Tabellen und Testdaten neu laden, Container läuft weiter:

```shell
cd extras/compose/postgres
docker cp drop.sql buch-postgres:/tmp/drop.sql
docker exec -e PGPASSWORD=p buch-postgres psql --dbname=buch --username=buch --file=/tmp/drop.sql
docker exec -e PGPASSWORD=p buch-postgres psql --dbname=buch --username=buch --file=/docker-entrypoint-initdb.d/02-create.sql
docker exec -e PGPASSWORD=p buch-postgres psql --dbname=buch --username=buch --file=/docker-entrypoint-initdb.d/03-insert.sql
```

## DB-Browser

Z.B. mit der VS-Code-Erweiterung _PostgreSQL_ (Microsoft) eine Verbindung anlegen:

| Feld          | Wert        |
| ------------- | ----------- |
| Server name   | `localhost` |
| User name     | `buch`      |
| Password      | `p`         |
| Database name | `buch`      |
| SSL mode      | `disable`   |

Die drei Tabellen liegen im Schema `buch`.

## Appserver

Abhängigkeiten installieren (legt `.venv` mit Python 3.15 an, _uv_ lädt Python bei Bedarf selbst):

```shell
uv sync --all-groups
```

Appserver starten, danach `http://localhost:8000` bzw. `http://localhost:8000/docs` aufrufen:

```shell
uv run buch
```

### REST-Schnittstelle (GET)

Interaktive Dokumentation: `http://localhost:8000/docs`

| Request                        | Beschreibung                                                                 |
| ------------------------------ | ---------------------------------------------------------------------------- |
| `GET /rest/{id}`               | Ein Buch mit Verlag und Rezensionen; Header `ETag` mit der Versionsnummer     |
| `GET /rest/{id}` + `If-None-Match: "<version>"` | Bedingter GET: `304 Not Modified`, falls unverändert            |
| `GET /rest/isbn/{isbn}`        | Ein Buch über die ISBN, sonst wie `GET /rest/{id}`                           |
| `GET /rest`                    | Alle Bücher (ohne Rezensionen)                                               |
| `GET /rest?...`                | Suche mit Query-Parametern, die mit UND verknüpft werden (siehe unten)       |
| `GET /rest/titel/{teil}`       | Titel, die den Teilstring enthalten, als Liste                               |

Jedes Attribut ist Suchparameter für `GET /rest`:

| Parameter                                      | Vergleich                                   |
| ---------------------------------------------- | ------------------------------------------- |
| `id`, `version`, `isbn`, `art`, `lieferbar`, `erscheinungsdatum` | exakt                      |
| `titel`, `homepage`, `verlag` (Name), `ort` (des Verlags) | Teilstring, Groß-/Kleinschreibung egal |
| `rating`, `rabatt`                             | mindestens                                  |
| `preis`                                        | höchstens                                   |
| `schlagwort`                                   | im JSON-Array `schlagwoerter` enthalten     |

Beispiele: `/rest?id=1`, `/rest?titel=a&art=HARDCOVER&rating=3`, `/rest?verlag=hanser&ort=münchen`,
`/rest?preis=30&lieferbar=true`.

Fehler: `404` mit `{"detail": "..."}`, falls nichts gefunden wurde; `422`, falls ein
Parameter ungültig ist (Validierung durch Pydantic und FastAPI).

### REST-Schnittstelle (POST)

| Request      | Beschreibung                                                                  |
| ------------ | ----------------------------------------------------------------------------- |
| `POST /rest` | Neues Buch mit Verlag (Pflicht, 1:1) und Rezensionen (optional, 1:N) anlegen; Antwort `201` ohne Body, Header `Location` mit der URL des neuen Buches und `ETag` `"0"` |

Der Request-Body hat dieselben Attribute wie bei PUT, zusätzlich `verlag` mit `name`
und `ort` sowie optional `rezensionen` mit je `bewertung` (1 bis 5) und `kommentar`.
Die Validierung übernimmt Pydantic (`422` mit Fehlerliste); eine bereits vorhandene
ISBN ergibt ebenfalls `422`.

```shell
curl -i -X POST http://localhost:8000/rest -H 'Content-Type: application/json' \
  -d '{"titel":"Neu","isbn":"978-3-123-45678-9","rating":3,"art":"EPUB","preis":"19.99","verlag":{"name":"Neuer Verlag","ort":"Karlsruhe"},"rezensionen":[{"bewertung":5,"kommentar":"Top"}]}'
```

### REST-Schnittstelle (PUT)

| Request                                   | Beschreibung                                                     |
| ----------------------------------------- | ---------------------------------------------------------------- |
| `PUT /rest/{id}` + `If-Match: "<version>"` | Buch vollständig überschreiben; Antwort `204` mit neuem `ETag`  |

Der Request-Body enthält `titel`, `isbn`, `rating`, `art`, `preis`, `rabatt`,
`lieferbar`, `erscheinungsdatum`, `homepage` und `schlagwoerter`; Verlag und
Rezensionen sind nicht änderbar. Die Validierung übernimmt Pydantic (`422`).

**Lost Updates** werden durch optimistische Synchronisation vermieden: `If-Match`
muss die Versionsnummer aus dem `ETag` des letzten `GET` enthalten. Ist sie veraltet,
hat jemand anderes inzwischen geändert und der Server antwortet mit `412`. Fehlt der
Header, antwortet er mit `428`. Zusätzlich prüft SQLAlchemy die Version beim `UPDATE`
(`version_id_col`).

```shell
curl -i -X PUT http://localhost:8000/rest/50 -H 'If-Match: "0"' -H 'Content-Type: application/json' \
  -d '{"titel":"Epsilon neu","isbn":"978-3-8273-3007-2","rating":4,"art":"PAPERBACK","preis":"55.50","rabatt":"0.055","lieferbar":true}'
```

```shell
curl -i http://localhost:8000/rest/1
curl -i -H 'If-None-Match: "0"' http://localhost:8000/rest/1
curl 'http://localhost:8000/rest?titel=a&art=HARDCOVER'
curl http://localhost:8000/rest/isbn/978-3-16-148410-0
```

Die DB-Verbindung ist in `src/buch/config/db.py` konfiguriert und kann über
Umgebungsvariablen mit dem Präfix `BUCH_DB_` (auch in einer `.env`) geändert werden,
z.B. `BUCH_DB_LOG_STATEMENTS=false`.

## Tests

### pytest

Die Integrationstests brauchen den laufenden PostgreSQL-Container mit den Testdaten:

```shell
uv run pytest
```

Die POST-Tests legen bei jedem Lauf neue Bücher mit zufälliger ISBN an, die PUT-Tests
ändern Buch 50. Zurücksetzen: siehe [Datenbank zurücksetzen](#datenbank-zurücksetzen).

### Bruno

Die Collection `extras/bruno/buch` enthält Requests für GET, POST und PUT mit
Assertions. In _Bruno_: _Open Collection_, das Verzeichnis `extras/bruno/buch`
wählen, Appserver mit `uv run buch` starten, Requests einzeln oder den Ordner `REST`
als _Run_ ausführen.

## Codeanalyse, Formatierung und Typprüfung

Die Konfiguration steht in `pyproject.toml` (`[tool.ruff]`, `[tool.ty]`).

```shell
uv run ruff check --preview src tests
uv run ruff format --preview src tests
uv run ty check src tests
```

## Checkliste der Vorlesung

| Punkt                                                        | Umsetzung                                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| PostgreSQL 18 als Docker Container, 1:1 und 1:N              | `extras/compose/postgres`: `buch` 1:1 `verlag`, `buch` 1:N `rezension`     |
| DB-Browser                                                   | [DB-Browser](#db-browser)                                                 |
| Git-Repository, commit early, commit often                   | https://github.com/atayoez/buch                                           |
| `pyproject.toml` mit uv, ruff, ty                            | `[tool.uv]`, `[tool.ruff]`, `[tool.ty]` in `pyproject.toml`               |
| REST mit FastAPI, Dependency Injection, Pydantic für Response | `src/buch/router`: `Depends(...)` für Session und Service, `BuchModel`     |
| GET mit Pfad-/Query-Parametern, bedingter GET                | `GET /rest/{id}` mit `ETag`/`If-None-Match`, `GET /rest?...`              |
| POST mit Validierung durch Pydantic                          | `POST /rest`, `BuchCreateModel`                                           |
| PUT mit Validierung und Vermeidung von Lost Updates          | `PUT /rest/{id}`, `BuchUpdateModel`, `If-Match` mit Versionsnummer        |
| DB-Zugriff durch SQLAlchemy                                  | `src/buch/entity`, `src/buch/repository`                                  |
| Testen von GET und POST                                      | `tests/rest` mit pytest, `extras/bruno/buch` mit Bruno                    |

## Hinweis für Linux mit podman

`docker` darf ein podman-Shim sein. `docker compose` braucht dann das
Docker-Compose-Plugin unter `~/.docker/cli-plugins/` und den User-Socket
(`systemctl --user enable --now podman.socket`). Bei aktivem SELinux muss das
Verzeichnis `extras/compose/postgres/init` das Label `container_file_t` tragen:
`chcon -Rt container_file_t extras/compose/postgres/init`.
