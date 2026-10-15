"""
core/migrare_invitatii_cabinet.py — `public.invitatii_cabinet`: invitațiile prin care se creează un cont nou de cabinet.

Comanda Costin 14.10.2026 (verbatim în DECIZII „Lotul 2”), pct.3: „Înregistrarea liberă se închide: în pilot, conturile noi se creează
numai prin invitație.” Tabela ține NUMAI hash-ul tokenului (sha256), emailul invitat, cine a invitat, termenul și folosirea.
Idempotent (CREATE TABLE IF NOT EXISTS). Se aplică prin `python -m core.migrari_registru ruleaza [--productie]
core/migrare_invitatii_cabinet.py`.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.invitatii_cabinet (
    id          serial PRIMARY KEY,
    email       text NOT NULL,
    token_hash  text NOT NULL UNIQUE,
    creat_de    integer,
    creat_la    timestamptz NOT NULL DEFAULT now(),
    expira_la   timestamptz NOT NULL,
    folosita_la timestamptz,
    firm_id     integer
)
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.invitatii_cabinet')")
        return cur.fetchone()[0] is not None


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_invitatii_cabinet: tabela %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
