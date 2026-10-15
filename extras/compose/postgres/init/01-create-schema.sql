-- Schema "buch" mit dem DB-User "buch" als Owner anlegen.
-- Wird vom Entrypoint des postgres-Images beim ersten Start automatisch ausgeführt
-- (Verzeichnis /docker-entrypoint-initdb.d, alphabetische Reihenfolge), und zwar
-- als POSTGRES_USER in der Datenbank POSTGRES_DB aus compose.yml.

CREATE SCHEMA IF NOT EXISTS AUTHORIZATION buch;
ALTER ROLE buch SET search_path = 'buch';
SET search_path = 'buch';
