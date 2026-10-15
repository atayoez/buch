-- DB-User, Datenbank und Tablespace für "buch" anlegen.
-- Aufruf als Superuser "postgres" in der DB "postgres":
--   psql --dbname=postgres --username=postgres --file=create-db.sql
-- Voraussetzung: das Verzeichnis /tablespace/buch existiert im Container.

CREATE USER buch PASSWORD 'p';
CREATE DATABASE buch;
GRANT ALL ON DATABASE buch TO buch;
CREATE TABLESPACE buchspace OWNER buch LOCATION '/tablespace/buch';
