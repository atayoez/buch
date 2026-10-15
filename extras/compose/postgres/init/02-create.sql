-- Tabellen für die Domäne "Buch":
--   buch 1:1 verlag      (UNIQUE auf verlag.buch_id)
--   buch 1:N rezension
-- Wird beim ersten Start des Containers automatisch ausgeführt (siehe 01-create-schema.sql).

SET search_path = 'buch';

-- https://www.postgresql.org/docs/current/datatype-enum.html
CREATE TYPE buchart AS ENUM ('HARDCOVER', 'PAPERBACK', 'EPUB');

CREATE TABLE IF NOT EXISTS buch (
    id                INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
                      -- Versionsnummer für optimistisches Locking (Lost Updates vermeiden)
    version           INTEGER NOT NULL DEFAULT 0,
    titel             TEXT NOT NULL,
                      -- ISBN-13, z.B. 978-3-16-148410-0; impliziter Index durch UNIQUE
    isbn              TEXT NOT NULL UNIQUE CHECK (isbn ~ '^97[89]-\d{1,5}-\d{1,7}-\d{1,7}-\d$'),
    rating            INTEGER NOT NULL CHECK (rating >= 0 AND rating <= 5),
    art               buchart,
                      -- 8 Stellen, davon 2 Nachkommastellen
    preis             NUMERIC(8,2) NOT NULL CHECK (preis >= 0),
                      -- Rabatt als Anteil, z.B. 0.125 = 12,5 %
    rabatt            NUMERIC(4,3) NOT NULL DEFAULT 0 CHECK (rabatt >= 0 AND rabatt < 1),
    lieferbar         BOOLEAN NOT NULL DEFAULT FALSE,
    erscheinungsdatum DATE CHECK (erscheinungsdatum <= current_date),
    homepage          TEXT,
                      -- https://www.postgresql.org/docs/current/datatype-json.html
    schlagwoerter     JSONB,
    erzeugt           TIMESTAMP NOT NULL DEFAULT now(),
    aktualisiert      TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS buch_titel_idx ON buch(titel);

-- 1:1 — jedes Buch hat genau einen Verlag, jeder Verlag-Datensatz gehört zu genau einem Buch
CREATE TABLE IF NOT EXISTS verlag (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    name        TEXT NOT NULL,
    ort         TEXT,
    buch_id     INTEGER NOT NULL UNIQUE REFERENCES buch ON DELETE CASCADE
);

-- 1:N — ein Buch hat beliebig viele Rezensionen
CREATE TABLE IF NOT EXISTS rezension (
    id          INTEGER GENERATED ALWAYS AS IDENTITY(START WITH 1000) PRIMARY KEY,
    bewertung   INTEGER NOT NULL CHECK (bewertung >= 1 AND bewertung <= 5),
    kommentar   TEXT,
    erzeugt     TIMESTAMP NOT NULL DEFAULT now(),
    buch_id     INTEGER NOT NULL REFERENCES buch ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS rezension_buch_id_idx ON rezension(buch_id);
