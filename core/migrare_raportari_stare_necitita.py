"""
core/migrare_raportari_stare_necitita.py — `public.raportari.stare_necitita`: iConta a schimbat starea firului, iar autorul n-a văzut încă.

Comanda Costin 16.10.2026, completarea 290–295 la lotul 6, deficiența 291 (verbatim în DECIZII): „Bulina roșie de pe butonul Suport apare
pentru cererea trimisă chiar de utilizator. Bulina anunță un răspuns sau o schimbare de stare venită de la iConta, nu propria cerere.”
Bulina = firele autorului cu mesaje necitite de la iConta (admin sau asistentul AI) SAU cu `stare_necitita` (scrisă de schimbarea stării
din Panou Admin, ștearsă când autorul deschide firul). Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie]
core/migrare_raportari_stare_necitita.py`.
"""
from core import db

DDL = """
ALTER TABLE public.raportari ADD COLUMN IF NOT EXISTS stare_necitita boolean NOT NULL DEFAULT false;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'raportari' "
                    "AND column_name = 'stare_necitita'")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_raportari_stare_necitita: coloana %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
