"""
core/migrare_inregistrari_email.py — `public.inregistrari_in_asteptare`: când a plecat emailul de confirmare și de câte ori s-a retrimis.

Comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.11 (deficiența 282, verbatim în DECIZII): „Cardul «Înregistrare» le listează: data,
denumirea cabinetului, emailul, dacă emailul de confirmare a plecat și când expiră linkul, cu acțiunea «Retrimite confirmarea».”
`email_trimis_la` se scrie la fiecare trimitere reușită (`uc_auth._register_liber`, `uc_auth.retrimite_confirmarea`); `retrimiteri`
numără retrimiterile din Panou Admin. Rândurile existente: cererea rămâne în tabelă NUMAI dacă emailul a plecat (la eșec `_register_liber`
o șterge — `inregistrare_libera.sterge`), deci momentul trimiterii lor e momentul creării — de aceea `email_trimis_la = creat_la`.
Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_inregistrari_email.py`.
"""
from core import db

DDL = """
ALTER TABLE public.inregistrari_in_asteptare ADD COLUMN IF NOT EXISTS email_trimis_la timestamptz;
ALTER TABLE public.inregistrari_in_asteptare ADD COLUMN IF NOT EXISTS retrimiteri integer NOT NULL DEFAULT 0;
UPDATE public.inregistrari_in_asteptare SET email_trimis_la = creat_la WHERE email_trimis_la IS NULL;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 2 FROM information_schema.columns WHERE table_schema = 'public' "
                    "AND table_name = 'inregistrari_in_asteptare' AND column_name IN ('email_trimis_la', 'retrimiteri')")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_inregistrari_email: coloanele %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
