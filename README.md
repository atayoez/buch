# buch

Projekt für die Vorlesung _KI-gestützte Serverentwicklung_ (WS 2026/27, Hochschule Karlsruhe).

Appserver mit _FastAPI_, _Pydantic_ und _SQLAlchemy_ für _PostgreSQL_, verwaltet mit _uv_.

Domäne: `Buch` mit genau einem `Verlag` (1:1) und beliebig vielen `Rezensionen` (1:N).

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Repository klonen](#repository-klonen)
- [Datenbank einrichten](#datenbank-einrichten)
- [Datenbank zurücksetzen](#datenbank-zurücksetzen)
- [DB-Browser](#db-browser)
- [Appserver](#appserver)

## Voraussetzungen

Die Installation aus der Installationsanleitung der Vorlesung, insbesondere:

- Git
- Python 3.15 und _uv_
- Docker (oder podman mit Docker-Compose-Plugin) für PostgreSQL
- Der PostgreSQL-Container aus dem Kursbeispiel `fastapi` (Verzeichnis
  `extras/compose/postgres`), eingerichtet nach dessen `ReadMe.md`, d.h. mit den
  Named Volumes `pg_data`, `pg_tablespace` und `pg_init` sowie TLS.

## Repository klonen

```shell
git clone https://github.com/atayoez/buch.git
cd buch
```

## Datenbank einrichten

Die SQL-Skripte liegen in `extras/compose/postgres/init/buch/sql`:

| Skript              | Zweck                                                     | Als User   | In DB      |
| ------------------- | --------------------------------------------------------- | ---------- | ---------- |
| `create-db.sql`     | DB-User `buch`, Datenbank `buch`, Tablespace `buchspace`  | `postgres` | `postgres` |
| `create-schema.sql` | Schema `buch`                                             | `buch`     | `buch`     |
| `create.sql`        | Tabellen `buch`, `verlag` (1:1), `rezension` (1:N)        | `buch`     | `buch`     |
| `insert.sql`        | Testdaten                                                 | `buch`     | `buch`     |
| `drop.sql`          | Tabellen und Typen löschen                                | `buch`     | `buch`     |

Zuerst den PostgreSQL-Container aus dem Kursbeispiel starten (in einer eigenen Shell):

```shell
cd <KURSBEISPIEL>/extras/compose/postgres
docker compose up
```

Dann in einer zweiten Shell im Wurzelverzeichnis dieses Repositories die Skripte
in den Container kopieren und in der angegebenen Reihenfolge ausführen.
Das Passwort für beide DB-User ist `p`.

```shell
docker compose -f <KURSBEISPIEL>/extras/compose/postgres/compose.yml exec postgres mkdir -p /tablespace/buch
docker cp extras/compose/postgres/init/buch/sql postgres:/tmp/buch-sql

docker exec -e PGPASSWORD=p postgres psql --dbname=postgres --username=postgres --file=/tmp/buch-sql/create-db.sql
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch --file=/tmp/buch-sql/create-schema.sql
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch --file=/tmp/buch-sql/create.sql
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch --file=/tmp/buch-sql/insert.sql
```

Überprüfen:

```shell
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch \
  -c "SELECT b.id, b.titel, v.name AS verlag, count(r.id) AS rezensionen
      FROM buch b JOIN verlag v ON v.buch_id = b.id
      LEFT JOIN rezension r ON r.buch_id = b.id
      GROUP BY b.id, b.titel, v.name ORDER BY b.id;"
```

Erwartet werden 5 Bücher mit jeweils einem Verlag und 0 bis 3 Rezensionen.

## Datenbank zurücksetzen

```shell
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch --file=/tmp/buch-sql/drop.sql
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch --file=/tmp/buch-sql/create.sql
docker exec -e PGPASSWORD=p postgres psql --dbname=buch --username=buch --file=/tmp/buch-sql/insert.sql
```

## DB-Browser

Mit der VS-Code-Erweiterung _PostgreSQL_ (Microsoft) eine Verbindung anlegen:

| Feld                 | Wert                                                                  |
| -------------------- | --------------------------------------------------------------------- |
| Server name          | `localhost`                                                           |
| User name            | `buch`                                                                |
| Password             | `p`                                                                   |
| Database name        | `buch`                                                                |
| SSL mode (Erweitert) | `require`                                                             |
| SSL certificate file | `<KURSBEISPIEL>/extras/compose/postgres/init/tls/server.crt`          |

## Appserver

Folgt. Geplant: `uv sync --all-groups` und `uv run buch`.

## Hinweis für Linux mit podman und SELinux

`docker` darf ein podman-Shim sein; `docker compose` braucht dann das
Docker-Compose-Plugin unter `~/.docker/cli-plugins/` und den User-Socket
(`systemctl --user enable --now podman.socket`). Dateien, die per Bind-Mount
in Container gereicht werden, benötigen das Label `container_file_t`
(`chcon -Rt container_file_t <pfad>`).
