# -*- coding: utf-8 -*-
"""core/migrare_cabinet_de_test.py — `public.accounting_firms.de_test` (comanda 14.3, 715.1, Costin: „Cabinetul de test se marchează explicit (marcaj în
Panou Admin), iar excepția urmează marcajul.”).

Alerta de acces anormal (`core/alerta_acces.py`) nu mai ghicește cabinetele de test după cuvintele „test” / „proba” din nume (un cabinet real cu un
asemenea cuvânt n-ar mai fi alertat niciodată): le lasă deoparte numai pe cele marcate aici. Marcajul îl pune superadminul din Panou Admin › Activitate
cabinete. Singura valoare pusă din oficiu: cabinetul cu EXACT numele „Cabinet Test Sesiunea B SRL” (cabinetul firmelor de test F1–F8). Idempotent.
Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_cabinet_de_test.py`."""
from core import db

CABINET_TEST = "Cabinet Test Sesiunea B SRL"
DDL = "ALTER TABLE public.accounting_firms ADD COLUMN IF NOT EXISTS de_test boolean NOT NULL DEFAULT false;"


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)
        cur.execute("UPDATE public.accounting_firms SET de_test = true WHERE nume = %s AND NOT de_test", (CABINET_TEST,))


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'accounting_firms' "
                    "AND column_name = 'de_test'")
        return cur.fetchone() is not None


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_cabinet_de_test: %s" % ("aplicată" if verifica(conn) else "INCOMPLETĂ"))


if __name__ == "__main__":
    _main()
