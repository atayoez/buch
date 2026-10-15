-- Tabellen und Typen für die Domäne "Buch" löschen (Reihenfolge wegen Fremdschlüssel).
-- Aufruf siehe README.md, Abschnitt "Datenbank zurücksetzen".

SET search_path = 'buch';
DROP TABLE IF EXISTS rezension;
DROP TABLE IF EXISTS verlag;
DROP TABLE IF EXISTS buch;
DROP TYPE IF EXISTS buchart;
