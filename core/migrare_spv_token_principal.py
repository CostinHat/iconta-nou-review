"""
core/migrare_spv_token_principal.py — spv_token capata un PRINCIPAL: cabinet XOR gratuit (F160).

public.spv_token era cheiat DOAR pe accounting_firm_id (NOT NULL) = cabinet. Contul gratuit n-are
cabinet (accounting_firm_id NULL pe tenant) -> nu-si putea chei tokenul. Optiunea A (DECIZII 18.07):
  - adaug tenant_id (nullable);
  - accounting_firm_id devine nullable;
  - CHECK: EXACT unul dintre (accounting_firm_id, tenant_id) e setat (cabinet XOR gratuit);
  - unicitate (tenant_id, serial_certificat) pentru randurile gratuit.
Randurile cabinet existente raman neatinse (accounting_firm_id setat, tenant_id NULL). Idempotent.
Tabel PUBLIC (nu per-tenant), detinut de postgres: se ruleaza CA OWNER (sudo -u postgres psql),
nu cu userul app. Mirror in spv_conector_ddl_v1.sql pentru deploy nou.
"""
from core import db

DDL = """
ALTER TABLE public.spv_token ADD COLUMN IF NOT EXISTS tenant_id integer;
ALTER TABLE public.spv_token ALTER COLUMN accounting_firm_id DROP NOT NULL;
-- GARDUL 1: XOR in DB (exact unul dintre principaluri)
ALTER TABLE public.spv_token DROP CONSTRAINT IF EXISTS spv_token_principal_chk;
ALTER TABLE public.spv_token ADD CONSTRAINT spv_token_principal_chk CHECK (
    (accounting_firm_id IS NOT NULL)::int + (tenant_id IS NOT NULL)::int = 1);
-- unicitatea firm devine PARTIALA (nu se aplica randurilor gratuit cu accounting_firm_id NULL)
ALTER TABLE public.spv_token DROP CONSTRAINT IF EXISTS spv_token_accounting_firm_id_serial_certificat_key;
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_firm
    ON public.spv_token (accounting_firm_id, serial_certificat) WHERE accounting_firm_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_tenant
    ON public.spv_token (tenant_id, serial_certificat) WHERE tenant_id IS NOT NULL;
-- GARDUL 1: un singur token VIU (activ) per principal
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_firm_viu
    ON public.spv_token (accounting_firm_id) WHERE activ AND accounting_firm_id IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_spv_token_tenant_viu
    ON public.spv_token (tenant_id) WHERE activ AND tenant_id IS NOT NULL;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT is_nullable FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name='spv_token' AND column_name='accounting_firm_id'")
        af_nullable = cur.fetchone()[0] == 'YES'
        cur.execute("SELECT count(*) FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name='spv_token' AND column_name='tenant_id'")
        tid = cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM pg_constraint WHERE conname='spv_token_principal_chk'")
        chk = cur.fetchone()[0] == 1
    return af_nullable and tid and chk


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
    with db.get_conn() as conn:
        ok = verifica(conn)
    print("Migrare spv_token principal:", "OK" if ok else "ESEC")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
