-- 01_ddl_tip_firma.sql
-- Adaugă tip_firma pe firma_profil în FIECARE tenant. Idempotent.
-- Rulează în psql: sudo -u postgres psql -d iconta_v2 -f 01_ddl_tip_firma.sql
--
-- tip_firma: 'srl' (partidă dublă, D100-D406) | 'pfa' (partidă simplă, RIP/D212)
-- default 'srl' — firmele existente sunt toate partidă dublă azi, deci corect.
-- 'srl' e umbrelă pentru orice persoană juridică pe dublă (SRL/SA/etc);
-- 'pfa' e umbrelă pentru PF pe simplă (PFA/II/IF). Nu suprasegmentăm.

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schema_name FROM information_schema.schemata
        WHERE schema_name LIKE 'tenant_%'
    LOOP
        -- adaugă coloana dacă lipsește
        EXECUTE format(
            'ALTER TABLE %I.firma_profil ADD COLUMN IF NOT EXISTS tip_firma '
            'VARCHAR(4) NOT NULL DEFAULT ''srl''',
            r.schema_name
        );
        -- gard de integritate: doar srl/pfa
        BEGIN
            EXECUTE format(
                'ALTER TABLE %I.firma_profil ADD CONSTRAINT tip_firma_valid '
                'CHECK (tip_firma IN (''srl'', ''pfa''))',
                r.schema_name
            );
        EXCEPTION WHEN duplicate_object THEN
            NULL;  -- constraint deja există
        END;
    END LOOP;
END $$;

-- verificare: listează tip_firma pe fiecare tenant
SELECT nspname AS tenant,
       (SELECT tip_firma FROM information_schema.columns c
        WHERE c.table_schema = nspname AND c.table_name = 'firma_profil'
          AND c.column_name = 'tip_firma') IS NOT NULL AS are_coloana
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
