-- spv_conector_ddl_v1.sql — conectorul SPV: token OAuth per PRINCIPAL + CUI-uri acoperite
-- Tabele in PUBLIC (tokenul apartine PRINCIPALULUI: cabinet XOR firma gratuita). In tenant_template: NIMIC.
-- Schema: ARHITECTURA_SPV.md "CONECTORUL SPV". PRINCIPAL (F160, DECIZII 18.07): accounting_firm_id
--   (cabinet) SAU tenant_id (gratuit), exact unul (CHECK). Mirror al core/migrare_spv_token_principal.py.
-- access_token/refresh_token CRIPTAT (Fernet) de spv_conector.py; cheia in ~/.iconta/api_keys.env
--   (SPV_FERNET_KEY), NU in DB. Dump fara env = inutilizabil.
-- Ruleaza CA OWNER: sudo -u postgres psql iconta_v2 -f spv_conector_ddl_v1.sql

CREATE TABLE IF NOT EXISTS public.spv_token (
  id                 SERIAL PRIMARY KEY,
  accounting_firm_id INT,                  -- cabinet (XOR tenant_id)
  tenant_id          INT,                  -- firma gratuita (XOR accounting_firm_id)
  serial_certificat  TEXT NOT NULL,        -- din JWT decodat
  access_token       TEXT NOT NULL,        -- CRIPTAT (Fernet)
  refresh_token      TEXT NOT NULL,        -- CRIPTAT (Fernet)
  access_expira      TIMESTAMPTZ NOT NULL,
  refresh_expira     TIMESTAMPTZ NOT NULL,
  creat_la           TIMESTAMPTZ DEFAULT now(),
  reimprospatat_la   TIMESTAMPTZ,
  activ              BOOLEAN DEFAULT true
);
-- GARDUL 1: XOR principal in DB (exact unul dintre accounting_firm_id / tenant_id)
ALTER TABLE public.spv_token DROP CONSTRAINT IF EXISTS spv_token_principal_chk;
ALTER TABLE public.spv_token ADD CONSTRAINT spv_token_principal_chk CHECK (
    (accounting_firm_id IS NOT NULL)::int + (tenant_id IS NOT NULL)::int = 1);
-- unicitate (principal, serial) - partiala per principal
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_firm
    ON public.spv_token (accounting_firm_id, serial_certificat) WHERE accounting_firm_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_tenant
    ON public.spv_token (tenant_id, serial_certificat) WHERE tenant_id IS NOT NULL;
-- GARDUL 1: un singur token VIU (activ) per principal
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_firm_viu
    ON public.spv_token (accounting_firm_id) WHERE activ AND accounting_firm_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_tenant_viu
    ON public.spv_token (tenant_id) WHERE activ AND tenant_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS public.spv_cui_acoperit (
  token_id      INT REFERENCES public.spv_token(id) ON DELETE CASCADE,
  cui           TEXT NOT NULL,
  verificat_la  TIMESTAMPTZ,
  are_drept     BOOLEAN,
  UNIQUE (token_id, cui)
);

-- Privilegii pentru rolul aplicatiei. Tabelele raman detinute de postgres (conventia DDL).
GRANT ALL PRIVILEGES ON public.spv_token, public.spv_cui_acoperit TO iconta_user;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE public.spv_token_id_seq TO iconta_user;
