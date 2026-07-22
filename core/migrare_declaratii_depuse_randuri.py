"""
core/migrare_declaratii_depuse_randuri.py — F163v2: persistarea declaratiei depuse
(xml + randuri) in public.declaratii_depuse.

SCHEMA PUBLIC, nu tenant: tabelul e GLOBAL (public.declaratii_depuse), nu per-tenant.
Convenția migrare_* clasica bucleaza schemele tenant_ (information_schema.schemata ~
'^tenant_'); aici e o singura tabela in public -> un singur ALTER, fara bucla. E prima
migrare "ca lumea" pe schema public (pana acum singurul precedent era ALTER-ul lazy
asigura_coloana_sursa din istoric_declaratii_import_api, workaround fiindca migrare_*
nu acopera public). F165 auditeaza doar tenant vs template; public n-are template/audit
-> vezi DE_FACUT.

Idempotent (ADD COLUMN IF NOT EXISTS). Consolideaza TOATE coloanele adaugate lui
declaratii_depuse pe schema public:
  - xml text     — XML-ul efectiv depus (era in payload-ul cozii, se arunca la jurnal);
  - randuri jsonb — `res` serializat (asdict + default=str), pentru control D-vs-D real
    (D390<->D300 etc.) fara reparsare XML. NULL pentru d112 (nu expune totaluri
    structurate — vezi temeiul din coada_api.randuri_din_res / DECIZII F163v2);
  - sursa text NOT NULL DEFAULT 'iconta' — 'iconta' (depus din app) vs 'migrare' (import
    istoric de la contabilul anterior). Era adaugata LAZY (asigura_coloana_sursa, workaround
    fiindca migrare_* nu acoperea public); golul e inchis (GRANT CREATE pe public, DECIZII
    22.07), workaround-ul eliminat -> aici e locul normativ. xml/randuri NULLABLE (istoricul
    de dinainte de v2 ramane fara — nu fabricam ce nu s-a capturat).
"""
from core import db

DDL = """
ALTER TABLE public.declaratii_depuse ADD COLUMN IF NOT EXISTS xml text;
ALTER TABLE public.declaratii_depuse ADD COLUMN IF NOT EXISTS randuri jsonb;
ALTER TABLE public.declaratii_depuse ADD COLUMN IF NOT EXISTS sursa text NOT NULL DEFAULT 'iconta';
"""


def aplica(conn):
    """Aplica DDL-ul idempotent pe public. Comiterea o face apelantul / _main."""
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    """True daca public.declaratii_depuse are AMBELE coloane F163v2."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='public' "
            "AND table_name='declaratii_depuse' AND column_name IN ('xml','randuri','sursa')")
        return cur.fetchone()[0] == 3


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
    with db.get_conn() as conn:
        ok = verifica(conn)
    print("Migrare declaratii_depuse_randuri (public): %s" % ("OK" if ok else "ESEC"))
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
