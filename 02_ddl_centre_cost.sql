-- 02_ddl_centre_cost.sql
-- F143 Faza 1: centre de cost (management accounting intern - dimensiune interna, NU
-- contabilitate bugetara publica; confirmat la sursa in CONCURENTA.csv 20.07: FGO/Keez/
-- WinMentor/Nexus = analiza pe centre + plan buget vs realizat, firme private).
--
-- Adauga in FIECARE tenant: tabelul centre_cost + coloana centru_cost_id pe
-- inregistrari_linii. Idempotent. Ruleaza: sudo -u postgres psql -d iconta_v2 -f 02_ddl_centre_cost.sql
--
-- Dimensiunea sta pe LINIE, nu pe antet: centrul de cost e proprietatea liniei de
-- cheltuiala/venit (clasa 6/7); o nota poate acoperi mai multe centre. NULL = nealocat
-- (default). Faza 1: doar notele MANUALE (jurnal_api) primesc centru; notele automate
-- raman NULL. Bugetele = Faza 2 (tabel separat, neinclus aici).

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    LOOP
        -- tabelul de centre de cost (nomenclator per firma)
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I.centre_cost ('
            '  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
            '  nume varchar(100) NOT NULL,'
            '  activ boolean NOT NULL DEFAULT true,'
            '  creat_la timestamptz NOT NULL DEFAULT now()'
            ')', r.schema_name);

        -- dimensiunea pe linia de nota (nullable = nealocat)
        EXECUTE format(
            'ALTER TABLE %I.inregistrari_linii ADD COLUMN IF NOT EXISTS centru_cost_id integer',
            r.schema_name);

        -- integritate: linia trimite la un centru din ACELASI tenant
        BEGIN
            EXECUTE format(
                'ALTER TABLE %I.inregistrari_linii ADD CONSTRAINT inregistrari_linii_centru_cost_fk '
                'FOREIGN KEY (centru_cost_id) REFERENCES %I.centre_cost(id)',
                r.schema_name, r.schema_name);
        EXCEPTION WHEN duplicate_object THEN
            NULL;  -- constraint deja exista
        END;
    END LOOP;
END $$;

-- verificare: fiecare tenant are tabelul + coloana
SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.tables t
              WHERE t.table_schema = nspname AND t.table_name = 'centre_cost') AS are_tabel,
       EXISTS(SELECT 1 FROM information_schema.columns c
              WHERE c.table_schema = nspname AND c.table_name = 'inregistrari_linii'
                AND c.column_name = 'centru_cost_id') AS are_coloana
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
