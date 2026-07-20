-- 08_ddl_cor_ocupatii.sql
-- F137: nomenclatorul COR (Clasificarea Ocupatiilor din Romania). NATIONAL (acelasi pt toate
-- firmele) -> tabel GLOBAL in public, NU per-tenant (nu intra in tenant_template). Datele se
-- incarca separat din fisierul oficial (cor_surse/cor2024.xml) prin cor_incarca.py. Idempotent.
--   sudo -u postgres psql -d iconta_v2 -f 08_ddl_cor_ocupatii.sql
--
-- cod: 6 cifre (cheie). denumire: ocupatia oficiala. denumire_cauta: forma normalizata (ASCII
-- minuscule) pt cautare diacritic-insensitiva (numele contin ă/î/ș/ț).

CREATE TABLE IF NOT EXISTS public.cor_ocupatii (
    cod           char(6) PRIMARY KEY,
    denumire      text NOT NULL,
    denumire_cauta text NOT NULL
);

CREATE INDEX IF NOT EXISTS cor_ocupatii_cauta_idx ON public.cor_ocupatii (denumire_cauta);

-- verificare (dupa incarcare trebuie sa fie 4422 - Ordin 573/180/2024)
SELECT count(*) AS nr_ocupatii FROM public.cor_ocupatii;
