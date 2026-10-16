"""
core/migrare_emailuri_dezabonate.py — registrul adreselor dezabonate de la emailurile aplicației (deficiența 268, „Lotul 5”, decizia
în DECIZII).

- `public.emailuri_dezabonate` — o adresă pe rând, normalizată (fără spații, cu litere mici), și momentul dezabonării. Dezabonarea e
  pe ADRESĂ, nu pe cont: o adresă fără cont (invitația, emailul pachetului lunar) se dezabonează la fel. `core/dezabonare.py` citește
  și scrie tabela; `observare.trimite_email_html` nu mai trimite la o adresă de aici, afară de emailurile cerute chiar atunci de
  destinatar (resetarea parolei, linkul de logare, confirmarea propriei adrese).
Idempotent (CREATE TABLE IF NOT EXISTS). Se aplică prin `python -m core.migrari_registru ruleaza [--productie]
core/migrare_emailuri_dezabonate.py`.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.emailuri_dezabonate (
    email          text PRIMARY KEY CHECK (email = lower(btrim(email)) AND email <> ''),
    dezabonat_la   timestamptz NOT NULL DEFAULT now()
);
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.emailuri_dezabonate') IS NOT NULL")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_emailuri_dezabonate: tabela %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
