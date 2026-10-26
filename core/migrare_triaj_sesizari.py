"""
core/migrare_triaj_sesizari.py — triajul AI al sesizărilor își păstrează decizia și motivul; mesajul automat către utilizator, cu
diacritice.

Comanda 13.1, deficiența 573 (anexa, verbatim): „La sesizarea escaladată nu se vede clasificarea/motivul AI; mesajul automat către
utilizator e fără diacritice. Escaladarea funcționează.”

- `raportari.triaj_decizie` (`raspuns` / `escaladare`) și `raportari.triaj_motiv` (de ce a escaladat asistentul AI, pentru echipa iConta;
  utilizatorul nu-l vede); `triaj_la` = când.

DATELE EXISTENTE:
- sesizările escaladate înainte de lotul 13 (`pentru_admin = true`, fără decizie scrisă) primesc `triaj_decizie = 'escaladare'` și motivul
  „escaladată înainte ca aplicația să păstreze motivul (lotul 13)” — motivul real nu s-a păstrat nicăieri, deci nu se inventează;
- confirmarea automată de dinainte, scrisă fără diacritice, primește textul de acum (`core.raportari_api.TEXT_ESCALADARE`) — e textul
  aplicației, nu al omului.
Idempotent. Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_triaj_sesizari.py`.
"""
from core import db

TEXT_VECHI = "Sesizarea ta a fost transmisa echipei iConta. Vei primi raspuns aici, in acest fir."
MOTIV_VECHI = "escaladată înainte ca aplicația să păstreze motivul (lotul 13)"


def aplica(conn):
    from core.raportari_api import TEXT_ESCALADARE
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE public.raportari ADD COLUMN IF NOT EXISTS triaj_decizie text "
                    "CHECK (triaj_decizie IS NULL OR triaj_decizie IN ('raspuns', 'escaladare'))")
        cur.execute("ALTER TABLE public.raportari ADD COLUMN IF NOT EXISTS triaj_motiv text")
        cur.execute("ALTER TABLE public.raportari ADD COLUMN IF NOT EXISTS triaj_la timestamptz")
        cur.execute("UPDATE public.raportari SET triaj_decizie = 'escaladare', triaj_motiv = %s "
                    " WHERE pentru_admin AND triaj_decizie IS NULL AND tip = 'sesizare'", (MOTIV_VECHI,))
        cur.execute("UPDATE public.raportari_mesaje SET text = %s WHERE rol_autor = 'ai' AND text = %s", (TEXT_ESCALADARE, TEXT_VECHI))


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 3 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'raportari' "
                    "AND column_name IN ('triaj_decizie', 'triaj_motiv', 'triaj_la')")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_triaj_sesizari: coloanele %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
