"""
core/migrare_inregistrare_libera.py — înregistrarea liberă cu confirmarea emailului și comutatorul ei (comanda Costin 15.10.2026,
„Lotul 4”, verbatim în DECIZII).

- `public.setari_platforma` — comutatoarele pe care superadminul le schimbă fără publicare (cheie -> valoare, cine și când). Primul:
  `inregistrare` = `libera` / `invitatie`. Rândul se pune `libera` (decizia din 15.10: „înlocuiește regula «numai prin invitație»”);
  fără rând sau fără tabelă, aplicația citește `invitatie` (închis).
- `public.inregistrari_in_asteptare` — cererea unui cabinet nou, până la clicul pe linkul din email: datele formularului, hash-ul
  parolei, hash-ul tokenului (sha256; tokenul pleacă numai în link), termenul (24 h) și folosirea. Contul și firma se creează abia la
  confirmare, deci până atunci nu există nimic cu care să te poți loga.
Idempotent (CREATE TABLE IF NOT EXISTS, INSERT … ON CONFLICT DO NOTHING). Se aplică prin `python -m core.migrari_registru ruleaza
[--productie] core/migrare_inregistrare_libera.py`.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.setari_platforma (
    cheie         text PRIMARY KEY,
    valoare       text NOT NULL,
    modificat_de  integer,
    modificat_la  timestamptz NOT NULL DEFAULT now()
);
INSERT INTO public.setari_platforma (cheie, valoare) VALUES ('inregistrare', 'libera') ON CONFLICT (cheie) DO NOTHING;
CREATE TABLE IF NOT EXISTS public.inregistrari_in_asteptare (
    id                serial PRIMARY KEY,
    email             text NOT NULL,
    token_hash        text NOT NULL UNIQUE,
    nume_cabinet      text NOT NULL,
    nume              text,
    prenume           text,
    cui               text,
    parola_hash       text NOT NULL,
    termeni_versiune  text NOT NULL,
    ip                text,
    creat_la          timestamptz NOT NULL DEFAULT now(),
    expira_la         timestamptz NOT NULL,
    confirmata_la     timestamptz,
    firm_id           integer
);
CREATE INDEX IF NOT EXISTS inregistrari_in_asteptare_email ON public.inregistrari_in_asteptare (email);
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.setari_platforma') IS NOT NULL AND to_regclass('public.inregistrari_in_asteptare') "
                    "IS NOT NULL")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_inregistrare_libera: tabelele %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
