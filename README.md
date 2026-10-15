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
- [Hinweis für Linux mit podman](#hinweis-für-linux-mit-podman)

## Voraussetzungen

- Git
- Docker mit Docker Compose (für PostgreSQL)
- Python 3.15 und _uv_ (für den Appserver, folgt)

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

Folgt. Geplant: `uv sync --all-groups` und `uv run buch`.

## Hinweis für Linux mit podman

`docker` darf ein podman-Shim sein. `docker compose` braucht dann das
Docker-Compose-Plugin unter `~/.docker/cli-plugins/` und den User-Socket
(`systemctl --user enable --now podman.socket`). Bei aktivem SELinux muss das
Verzeichnis `extras/compose/postgres/init` das Label `container_file_t` tragen:
`chcon -Rt container_file_t extras/compose/postgres/init`.
