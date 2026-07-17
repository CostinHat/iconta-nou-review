-- spv_conector_ddl_v1.sql — conectorul SPV: token OAuth per cabinet + CUI-uri acoperite
-- Tabele in PUBLIC (tokenul apartine cabinetului, nu firmei). In tenant_template: NIMIC.
-- Schema EXACTA: ARHITECTURA_SPV.md, sectiunea "CONECTORUL SPV -> SCHEMA" (17.07.2026).
--   Nu se adauga coloane fata de aceasta schema (brief: orice deviere = STOP).
-- access_token/refresh_token se stocheaza CRIPTAT (Fernet) de spv_conector.py; cheia
--   sta in ~/.iconta/api_keys.env (SPV_FERNET_KEY), NU in DB. Dump fara env = inutilizabil.
-- Ruleaza: sudo -u postgres psql iconta_v2 -f spv_conector_ddl_v1.sql

CREATE TABLE IF NOT EXISTS public.spv_token (
  id                 SERIAL PRIMARY KEY,
  accounting_firm_id INT NOT NULL,
  serial_certificat  TEXT NOT NULL,        -- din JWT decodat
  access_token       TEXT NOT NULL,        -- CRIPTAT (Fernet)
  refresh_token      TEXT NOT NULL,        -- CRIPTAT (Fernet)
  access_expira      TIMESTAMPTZ NOT NULL,
  refresh_expira     TIMESTAMPTZ NOT NULL,
  creat_la           TIMESTAMPTZ DEFAULT now(),
  reimprospatat_la   TIMESTAMPTZ,
  activ              BOOLEAN DEFAULT true,
  UNIQUE (accounting_firm_id, serial_certificat)
);

CREATE TABLE IF NOT EXISTS public.spv_cui_acoperit (
  token_id      INT REFERENCES public.spv_token(id) ON DELETE CASCADE,
  cui           TEXT NOT NULL,
  verificat_la  TIMESTAMPTZ,
  are_drept     BOOLEAN,
  UNIQUE (token_id, cui)
);

-- Privilegii pentru rolul aplicatiei, oglindite dupa public.tokene_activare
-- (iconta_user=arwdDxt/postgres). Tabelele raman detinute de postgres (conventia DDL).
GRANT ALL PRIVILEGES ON public.spv_token, public.spv_cui_acoperit TO iconta_user;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public.spv_token_id_seq TO iconta_user;
