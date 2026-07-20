-- 06_ddl_cadou_eveniment.sql
-- F133 Faza 2b1: tichete cadou. Adauga dimensiunea EVENIMENT pe beneficii_lunare (pragul de
-- 300 lei e per-eveniment; legalitatea depinde de eveniment). Idempotent. Ruleaza:
--   sudo -u postgres psql -d iconta_v2 -f 06_ddl_cadou_eveniment.sql
--
-- eveniment: '' (non-cadou, ex. vacanta) | paste | craciun | 8martie | 1iunie | altul (nelegal).
-- Cele 4 legale <=300 = neimpozabile; 'altul' sau >300 = taxabil (Faza 2b2 - deocamdata semnal).
-- Unique extins pe (salariat, an, luna, tip, eveniment): un cadou per eveniment; vacanta ramane
-- unica per salariat/an/luna (eveniment='').

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.beneficii_lunare ADD COLUMN IF NOT EXISTS '
            'eveniment varchar(20) NOT NULL DEFAULT ''''', r.schema_name);
        EXECUTE format(
            'ALTER TABLE %I.beneficii_lunare DROP CONSTRAINT IF EXISTS beneficii_lunare_eveniment_ck',
            r.schema_name);
        EXECUTE format(
            'ALTER TABLE %I.beneficii_lunare ADD CONSTRAINT beneficii_lunare_eveniment_ck '
            'CHECK (eveniment IN ('''', ''paste'', ''craciun'', ''8martie'', ''1iunie'', ''altul''))',
            r.schema_name);
        -- inlocuieste unique-ul vechi (fara eveniment) cu cel extins
        EXECUTE format('ALTER TABLE %I.beneficii_lunare DROP CONSTRAINT IF EXISTS beneficii_lunare_unic', r.schema_name);
        EXECUTE format('ALTER TABLE %I.beneficii_lunare DROP CONSTRAINT IF EXISTS beneficii_lunare_unic_v2', r.schema_name);
        EXECUTE format(
            'ALTER TABLE %I.beneficii_lunare ADD CONSTRAINT beneficii_lunare_unic_v2 '
            'UNIQUE (salariat_id, an, luna, tip, eveniment)', r.schema_name);
    END LOOP;
END $$;

-- verificare
SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.columns c
              WHERE c.table_schema = nspname AND c.table_name = 'beneficii_lunare'
                AND c.column_name = 'eveniment') AS are_eveniment
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
