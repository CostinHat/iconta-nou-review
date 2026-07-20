-- 07_ddl_iban_salariat.sql
-- F134: plata salariilor pe card. Adauga IBAN-ul salariatului (contul beneficiar), necesar
-- pentru fisierul de plata SEPA/ISO 20022 pain.001.001.03 catre banca. Idempotent. Ruleaza:
--   sudo -u postgres psql -d iconta_v2 -f 07_ddl_iban_salariat.sql
--
-- IBAN optional: doar salariatii platiti pe card au IBAN. varchar(34) = lungimea maxima IBAN
-- (ISO 13616); IBAN romanesc = 24 caractere. Validarea (format + mod-97) se face in salariati_api.

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
            'iban varchar(34)', r.schema_name);
    END LOOP;
END $$;

-- verificare
SELECT nspname AS tenant,
       EXISTS(SELECT 1 FROM information_schema.columns c
              WHERE c.table_schema = nspname AND c.table_name = 'salariati'
                AND c.column_name = 'iban') AS are_iban
FROM pg_namespace WHERE nspname LIKE 'tenant_%' ORDER BY nspname;
