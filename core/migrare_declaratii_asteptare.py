"""
core/migrare_declaratii_asteptare.py — `public.declaratii_in_asteptare`: declarația de TVA refuzată la „Trimite în coadă” care așteaptă
validarea notelor ce explică diferența.

Comanda Costin 16.10.2026, „Lotul 6”, completarea 1, deficiența 284 (verbatim în DECIZII): „refuzul de la «Trimite în coadă» numește
nota sau notele care explică diferența [...], cu link spre ele [...]. După validarea notei, declarația se regenerează singură și intră în
coadă; depunerea la ANAF rămâne clicul contabilului.” Rândul păstrează cererea (`cerere`, ca la `POST /coada`), cine a trimis-o (`user_id`,
`rol` — drepturile se citesc din nou la reluare, `uc_comun._are_permisiune`) și notele așteptate (`note_ids`). Reluarea o face
`uc_coada.reia_declaratiile_in_asteptare` (middleware-ul, după orice cerere de modificare reușită a cabinetului); rezultatul ei se scrie
pe rând (`rezolvata_la`, `rezultat`) și se anunță prin notificare. O singură așteptare deschisă pe (firmă, declarație, perioadă).
Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_declaratii_asteptare.py`.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.declaratii_in_asteptare (
    id           serial PRIMARY KEY,
    cabinet_id   integer NOT NULL,
    tenant_id    integer NOT NULL,
    tip          text NOT NULL CHECK (tip = lower(tip)),
    an           integer NOT NULL,
    luna         integer,
    trim         integer,
    cerere       jsonb NOT NULL,
    user_id      integer NOT NULL,
    rol          text,
    note_ids     integer[] NOT NULL,
    creat_la     timestamptz NOT NULL DEFAULT now(),
    rezolvata_la timestamptz,
    rezultat     jsonb
);
CREATE UNIQUE INDEX IF NOT EXISTS declaratii_in_asteptare_deschisa
    ON public.declaratii_in_asteptare (tenant_id, tip, an, COALESCE(luna, 0), COALESCE(trim, 0)) WHERE rezolvata_la IS NULL;
CREATE INDEX IF NOT EXISTS declaratii_in_asteptare_cabinet ON public.declaratii_in_asteptare (cabinet_id) WHERE rezolvata_la IS NULL;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'declaratii_in_asteptare_deschisa'")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_declaratii_asteptare: tabela %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
