-- Schema "buch" mit dem DB-User "buch" als Owner anlegen.
-- Aufruf in der DB "buch" als User "buch":
--   psql --dbname=buch --username=buch --file=create-schema.sql

CREATE SCHEMA IF NOT EXISTS AUTHORIZATION buch;
ALTER ROLE buch SET search_path = 'buch';
