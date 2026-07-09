-- bonuri_ddl_flux_v2.sql — documentul pozat devine bon SAU chitanta
-- Ruleaza: sudo -u postgres psql iconta_v2 -f bonuri_ddl_flux_v2.sql
DO $$
DECLARE s text;
BEGIN
  FOR s IN SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%'
  LOOP
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS tip varchar(12) NOT NULL DEFAULT ''bon''', s);
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS numar_document varchar(50)', s);
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS mentiuni text', s);
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS factura_id integer', s);
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS casa_operatiune_id integer', s);
  END LOOP;
END $$;
