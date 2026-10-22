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
  - [REST-Schnittstelle (PUT)](#rest-schnittstelle-put)
- [Tests](#tests)
- [Codeanalyse, Formatierung und Typprüfung](#codeanalyse-formatierung-und-typprüfung)
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
| `GET /rest`                    | Alle Bücher (ohne Rezensionen)                                               |
| `GET /rest?titel=a&art=HARDCOVER&rating=3` | Suche; Parameter `titel`, `isbn`, `rating` (min.), `art`, `lieferbar`, `schlagwort` werden mit UND verknüpft |
| `GET /rest/titel/{teil}`       | Titel, die den Teilstring enthalten, als Liste                               |

Fehler: `404` mit `{"detail": "..."}`, falls nichts gefunden wurde; `422`, falls ein
Parameter ungültig ist (Validierung durch Pydantic und FastAPI).

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
```

Die DB-Verbindung ist in `src/buch/config/db.py` konfiguriert und kann über
Umgebungsvariablen mit dem Präfix `BUCH_DB_` (auch in einer `.env`) geändert werden,
z.B. `BUCH_DB_LOG_STATEMENTS=false`.

## Tests

Die Integrationstests brauchen den laufenden PostgreSQL-Container mit den Testdaten:

```shell
uv run pytest
```

## Codeanalyse, Formatierung und Typprüfung

Die Konfiguration steht in `pyproject.toml` (`[tool.ruff]`, `[tool.ty]`).

```shell
uv run ruff check --preview src tests
uv run ruff format --preview src tests
uv run ty check src tests
```

## Hinweis für Linux mit podman

`docker` darf ein podman-Shim sein. `docker compose` braucht dann das
Docker-Compose-Plugin unter `~/.docker/cli-plugins/` und den User-Socket
(`systemctl --user enable --now podman.socket`). Bei aktivem SELinux muss das
Verzeichnis `extras/compose/postgres/init` das Label `container_file_t` tragen:
`chcon -Rt container_file_t extras/compose/postgres/init`.
