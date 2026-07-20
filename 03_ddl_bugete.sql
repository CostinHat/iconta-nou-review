-- 03_ddl_bugete.sql
-- F143 Faza 2: bugete pe centru de cost (management accounting intern).
-- Adauga in FIECARE tenant tabelul bugete. Idempotent. Ruleaza:
--   sudo -u postgres psql -d iconta_v2 -f 03_ddl_bugete.sql
--
-- GRANULARITATE per clasa: o pereche (buget_cheltuieli, buget_venituri) per (centru, an) -
-- ca sa se potriveasca cu raportul Faza 1 care e per-clasa (cheltuieli/venituri/net); un
-- buget net unic ar ascunde depasirea pe cheltuieli mascata de venituri sub plan.
-- PERIODICITATE anuala: o cifra per centru/an/tip - cel mai simplu de intretinut pt un cabinet
-- mic (vs 12x lunar). UNIQUE(centru_cost_id, an) = un rand de buget per centru pe an.

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    LOOP
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I.bugete ('
            '  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
            '  centru_cost_id integer NOT NULL REFERENCES %I.centre_cost(id),'
            '  an integer NOT NULL,'
            '  buget_cheltuieli numeric(14,2) NOT NULL DEFAULT 0,'
            '  buget_venituri numeric(14,2) NOT NULL DEFAULT 0,'
            '  CONSTRAINT bugete_centru_an_unic UNIQUE (centru_cost_id, an)'
            ')', r.schema_name, r.schema_name);
    END LOOP;
END $$;

-- verificare: fiecare tenant are tabelul
SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.tables t
              WHERE t.table_schema = nspname AND t.table_name = 'bugete') AS are_tabel
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
