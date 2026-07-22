"""
core/migrare_declaratii_tip_lowercase.py — canonizare `tip` la LOWERCASE + gardă CHECK.

SCHEMA PUBLIC. `tip` (declaratii_depuse, declaratii_coada) e CHEIE DE JOIN, nu text de afișare:
o singură formă la stocare (lowercase, ca dispecerul declaratii_api + CHEIE_DUK-key + scadente).
Forma ANAF uppercase trăiește în duk.CHEIE_DUK și se face upper() DOAR la randare, NU în coloană.
Vezi DECIZII 22.07.

BUG reparat (prins de prima depunere reală prin app): app stoca lowercase ('d300'), importul
istoric uppercase ('D300'), iar semaforul (declaratii_datorate) matcheza uppercase -> depunerile
prin app apăreau ca nedepuse. Toți writerii + matcherii trec pe lowercase; CHECK-ul apără cauza.

ORDINE (contează): UPDATE datele întâi -> apoi CHECK (altfel CHECK-ul pică pe rândurile uppercase).
Idempotent: UPDATE ... WHERE tip<>lower(tip) (no-op a doua oară) + CHECK adăugat doar dacă lipsește.
"""
from core import db

DDL = """
-- 1) canonizare date existente (5 randuri migrare uppercase; coada deja lowercase)
UPDATE public.declaratii_depuse SET tip = lower(tip) WHERE tip <> lower(tip);
UPDATE public.declaratii_coada  SET tip = lower(tip) WHERE tip <> lower(tip);

-- 2) GARDA: tip trebuie sa fie lowercase (dupa UPDATE). Idempotent.
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_depuse_tip_lower') THEN
    ALTER TABLE public.declaratii_depuse
      ADD CONSTRAINT declaratii_depuse_tip_lower CHECK (tip = lower(tip));
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='declaratii_coada_tip_lower') THEN
    ALTER TABLE public.declaratii_coada
      ADD CONSTRAINT declaratii_coada_tip_lower CHECK (tip = lower(tip));
  END IF;
END $$;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    """True daca zero randuri uppercase + ambele CHECK-uri exista."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.declaratii_depuse WHERE tip<>lower(tip)")
        d_ok = cur.fetchone()[0] == 0
        cur.execute("SELECT count(*) FROM public.declaratii_coada WHERE tip<>lower(tip)")
        c_ok = cur.fetchone()[0] == 0
        cur.execute("SELECT count(*) FROM pg_constraint WHERE conname IN "
                    "('declaratii_depuse_tip_lower','declaratii_coada_tip_lower')")
        chk = cur.fetchone()[0] == 2
    return d_ok and c_ok and chk


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
    with db.get_conn() as conn:
        ok = verifica(conn)
    print("Migrare declaratii tip lowercase + CHECK:", "OK" if ok else "ESEC")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
