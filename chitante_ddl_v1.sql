-- chitante_ddl_v1.sql — tabela chitante + seria pe firma, in toate schemele tenant
-- Ruleaza: sudo -u postgres psql iconta_v2 -f chitante_ddl_v1.sql
DO $$
DECLARE s text;
BEGIN
  FOR s IN SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'tenant_%'
  LOOP
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I.chitante (
      id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      serie varchar(10) NOT NULL,
      numar integer NOT NULL,
      data date NOT NULL,
      factura_id integer,
      client_nume text,
      client_cui varchar(30),
      suma numeric(12,2) NOT NULL,
      reprezentand text,
      casa_operatiune_id integer,
      inregistrare_id integer,
      anulata boolean NOT NULL DEFAULT false,
      creat_la timestamptz NOT NULL DEFAULT now())', s);
    EXECUTE format('ALTER TABLE %I.chitante OWNER TO iconta_user', s);
    EXECUTE format('ALTER TABLE %I.firma_profil ADD COLUMN IF NOT EXISTS serie_chitanta varchar(10) DEFAULT ''CH''', s);
  END LOOP;
END $$;
