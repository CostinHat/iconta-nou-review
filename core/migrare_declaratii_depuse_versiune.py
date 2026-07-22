"""
core/migrare_declaratii_depuse_versiune.py — F163v2 / varianta A: versionarea depunerilor.

PROBLEMA (verificat la sursa 22.07): PK vechi = (tenant_id, an, luna, tip) + ON CONFLICT
DO NOTHING la depunere -> re-depunerea ACELUIASI tip pe aceeasi perioada era ignorata tacit
(first-write-wins). Odata ce persistam VALORI (xml + randuri, F163v2), first-write-wins devine
FALS FISCAL: rectificativa D300/D390/D394 e practica normala; controlul D-vs-D ar compara cu
actul INLOCUIT, nu cu cel in vigoare. Vezi DECIZII 22.07 F163v2 (de ce A si nu B).

SOLUTIE (varianta A, DA Costin): nr_depunere in PK -> istoric append-only al depunerilor per
perioada; "curenta" = nr_depunere maxim, expusa printr-o VEDERE. Fara FK spre declaratii_depuse
(verificat: NICIUNUL), deci PK-ul se poate reface fara efecte referentiale.

Idempotent:
  1. ADD COLUMN nr_depunere integer NOT NULL DEFAULT 1 (ADD COLUMN aplica DEFAULT pe randurile
     EXISTENTE -> backfill la 1 automat, fara UPDATE separat);
  2. PK (tenant,an,luna,tip) -> (tenant,an,luna,tip,nr_depunere), doar daca inca e cel vechi;
  3. VEDERE public.declaratii_depuse_curente = ultima versiune per (tenant,an,luna,tip).

SCHEMA PUBLIC (nu tenant) — a doua migrare "ca lumea" pe public dupa randuri (F165 nu acopera
public; vezi DE_FACUT).
"""
from core import db

DDL = """
-- 1) nr_depunere: existentele -> 1 (DEFAULT pe ADD COLUMN backfill-uieste)
ALTER TABLE public.declaratii_depuse ADD COLUMN IF NOT EXISTS nr_depunere integer NOT NULL DEFAULT 1;

-- 2) PK (tenant,an,luna,tip) -> +nr_depunere, idempotent (doar daca inca e cel vechi)
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'public.declaratii_depuse'::regclass AND contype = 'p'
      AND pg_get_constraintdef(oid) = 'PRIMARY KEY (tenant_id, an, luna, tip)'
  ) THEN
    ALTER TABLE public.declaratii_depuse DROP CONSTRAINT declaratii_depuse_pkey;
    ALTER TABLE public.declaratii_depuse
      ADD CONSTRAINT declaratii_depuse_pkey
      PRIMARY KEY (tenant_id, an, luna, tip, nr_depunere);
  END IF;
END $$;

-- 3) vedere "curenta": ultima versiune per (tenant,an,luna,tip)
CREATE OR REPLACE VIEW public.declaratii_depuse_curente AS
  SELECT DISTINCT ON (tenant_id, an, luna, tip) *
  FROM public.declaratii_depuse
  ORDER BY tenant_id, an, luna, tip, nr_depunere DESC;
"""


def aplica(conn):
    """Aplica DDL-ul idempotent pe public. Comiterea o face apelantul / _main."""
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    """True daca: nr_depunere exista + PK include nr_depunere + vederea exista."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema='public' "
                    "AND table_name='declaratii_depuse' AND column_name='nr_depunere'")
        are_col = cur.fetchone()[0] == 1
        cur.execute("SELECT pg_get_constraintdef(oid) FROM pg_constraint "
                    "WHERE conrelid='public.declaratii_depuse'::regclass AND contype='p'")
        pk = cur.fetchone()
        pk_ok = pk is not None and "nr_depunere" in pk[0]
        cur.execute("SELECT to_regclass('public.declaratii_depuse_curente')")
        are_view = cur.fetchone()[0] is not None
    return are_col and pk_ok and are_view


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
    with db.get_conn() as conn:
        ok = verifica(conn)
    print("Migrare declaratii_depuse_versiune (public): %s" % ("OK" if ok else "ESEC"))
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
