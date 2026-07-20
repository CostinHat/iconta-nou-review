-- 04_ddl_tichet_masa.sql
-- F133 Faza 1: tichete de masa. Config per salariat = valoarea nominala a unui tichet
-- (0 = nu primeste tichete). Numarul de tichete = zile efectiv lucrate (din pontaj),
-- calculat la stat, nu stocat. Adauga in FIECARE tenant. Idempotent.
--   sudo -u postgres psql -d iconta_v2 -f 04_ddl_tichet_masa.sql
--
-- Plafonul legal (45 lei/2026, Legea 201/2025) traieste in common.COTE (valoare fiscala
-- cu data), nu in DB - aici stocam DOAR valoarea aleasa de firma pt salariat.

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.salariati ADD COLUMN IF NOT EXISTS '
            'tichet_masa_valoare numeric NOT NULL DEFAULT 0',
            r.schema_name);
    END LOOP;
END $$;

-- verificare
SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.columns c
              WHERE c.table_schema = nspname AND c.table_name = 'salariati'
                AND c.column_name = 'tichet_masa_valoare') AS are_coloana
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
