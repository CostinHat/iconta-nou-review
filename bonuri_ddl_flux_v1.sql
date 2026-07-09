-- bonuri_ddl_flux_v1.sql — coloane pentru fluxul bon (draft/confirmare, TVA pe cote, poze)
-- Ruleaza: sudo -u postgres psql iconta_v2 -f bonuri_ddl_flux_v1.sql
DO $$
DECLARE s text;
BEGIN
  FOR s IN SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%'
  LOOP
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS tva jsonb DEFAULT ''[]''::jsonb', s);
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS nr_imagini integer NOT NULL DEFAULT 0', s);
    EXECUTE format('ALTER TABLE %I.bonuri ADD COLUMN IF NOT EXISTS bon_complet boolean NOT NULL DEFAULT true', s);
  END LOOP;
END $$;
