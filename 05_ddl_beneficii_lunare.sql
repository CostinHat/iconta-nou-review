-- 05_ddl_beneficii_lunare.sql
-- F133 Faza 2a: tichete de vacanta = sume ONE-OFF pe luna (nu config permanent ca tichetele
-- de masa). Tabel per salariat/an/luna/tip. Extensibil pt cadou (2b, tip='cadou' + eveniment).
-- Adauga in FIECARE tenant. Idempotent.
--   sudo -u postgres psql -d iconta_v2 -f 05_ddl_beneficii_lunare.sql
--
-- Tratament fiscal tichete vacanta 2026 (verificat la sursa): CASS 10% + impozit 10% pe
-- valoare, FARA CAS (art. 142 lit. r CF) si FARA CAM; plafon neimpozabil 6 salarii minime/an.

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    LOOP
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I.beneficii_lunare ('
            '  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
            '  salariat_id integer NOT NULL REFERENCES %I.salariati(id),'
            '  an integer NOT NULL,'
            '  luna integer NOT NULL,'
            '  tip varchar(20) NOT NULL,'
            '  valoare numeric(14,2) NOT NULL DEFAULT 0,'
            '  CONSTRAINT beneficii_lunare_tip_ck CHECK (tip IN (''vacanta'', ''cadou'')),'
            '  CONSTRAINT beneficii_lunare_luna_ck CHECK (luna BETWEEN 1 AND 12),'
            '  CONSTRAINT beneficii_lunare_val_ck CHECK (valoare >= 0),'
            '  CONSTRAINT beneficii_lunare_unic UNIQUE (salariat_id, an, luna, tip)'
            ')', r.schema_name, r.schema_name);
    END LOOP;
END $$;

-- verificare
SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.tables t
              WHERE t.table_schema = nspname AND t.table_name = 'beneficii_lunare') AS are_tabel
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
