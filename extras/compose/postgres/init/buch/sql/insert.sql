-- Testdaten. Feste IDs unterhalb von 1000, damit die IDENTITY-Sequenz nicht kollidiert.
--   psql --dbname=buch --username=buch --file=insert.sql

INSERT INTO buch (id, version, titel, isbn, rating, art, preis, rabatt, lieferbar, erscheinungsdatum, homepage, schlagwoerter, erzeugt, aktualisiert)
OVERRIDING SYSTEM VALUE VALUES
    (1,  0, 'Alpha',   '978-3-16-148410-0', 4, 'HARDCOVER', 11.10, 0.011, true,  '2025-02-01', 'https://acme.at',  '["JAVASCRIPT"]',           '2025-02-01 00:00:00', '2025-02-01 00:00:00'),
    (20, 0, 'Beta',    '978-0-306-40615-7', 2, 'PAPERBACK', 22.20, 0.022, true,  '2025-02-02', 'https://acme.biz', '["TYPESCRIPT"]',           '2025-02-02 00:00:00', '2025-02-02 00:00:00'),
    (30, 0, 'Gamma',   '978-1-4028-9462-6', 1, 'EPUB',      33.30, 0.033, true,  '2025-02-03', 'https://acme.com', '["JAVASCRIPT","PYTHON"]',  '2025-02-03 00:00:00', '2025-02-03 00:00:00'),
    (40, 0, 'Delta',   '978-0-07-881809-8', 3, 'HARDCOVER', 44.40, 0.044, true,  '2025-02-04', 'https://acme.de',  NULL,                       '2025-02-04 00:00:00', '2025-02-04 00:00:00'),
    (50, 0, 'Epsilon', '978-3-8273-3007-2', 2, 'PAPERBACK', 55.50, 0.055, false, '2025-02-05', 'https://acme.es',  '["PYTHON"]',               '2025-02-05 00:00:00', '2025-02-05 00:00:00');

INSERT INTO verlag (id, name, ort, buch_id)
OVERRIDING SYSTEM VALUE VALUES
    (1,  'dpunkt.verlag',  'Heidelberg', 1),
    (20, 'Springer',       'Berlin',     20),
    (30, 'O''Reilly',      'Sebastopol', 30),
    (40, 'Hanser',         'München',    40),
    (50, 'Rheinwerk',      'Bonn',       50);

INSERT INTO rezension (id, bewertung, kommentar, erzeugt, buch_id)
OVERRIDING SYSTEM VALUE VALUES
    (1,  5, 'Sehr gut erklärt',          '2025-03-01 00:00:00', 1),
    (2,  3, 'Solide, aber etwas knapp',  '2025-03-02 00:00:00', 1),
    (20, 2, 'Veraltete Beispiele',       '2025-03-03 00:00:00', 20),
    (30, 4, 'Guter Einstieg',            '2025-03-04 00:00:00', 30),
    (31, 5, 'Klare Empfehlung',          '2025-03-05 00:00:00', 30),
    (32, 1, 'Zu oberflächlich',          '2025-03-06 00:00:00', 30),
    (40, 3, NULL,                        '2025-03-07 00:00:00', 40);
