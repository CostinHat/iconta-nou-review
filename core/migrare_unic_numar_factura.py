# -*- coding: utf-8 -*-
"""core/migrare_unic_numar_factura.py — index UNIC pe numărul facturilor emise (C1).

DE CE (C1, audit 17.09.2026). `facturi` n-avea nicio constrângere de unicitate pe (serie, numar):
două cereri concurente puteau primi același număr (`numerotare` citea fără `FOR UPDATE`, incrementul
venea târziu). Reparația principală e rezervarea ATOMICĂ din `facturi_api._rezerva_numar` (UPDATE
... +1 RETURNING, care blochează rândul). Indexul de aici e PLASA A DOUA: dacă vreun drum viitor ar
ocoli rezervarea, a doua inserare cu același număr PICĂ la ANAF-nivel de bază, nu se strecoară tăcut
(art. 319 CF: numerotare secvențială unică).

Index PARȚIAL pe emise (facturile PRIMITE poartă numărul furnizorului, care se poate repeta între
furnizori — nu se constrânge). `COALESCE(serie,'')` ca o serie lipsă să nu scape constrângerii.

NU se aplică dacă EXISTĂ deja duplicate (le-ar respinge crearea indexului). Atunci le RAPORTEAZĂ, cu
CUI-ul firmei, ca omul să le corecteze (storno + reemitere) — nu se șterge nimic tăcut.

Idempotent (`CREATE UNIQUE INDEX IF NOT EXISTS`). Oglinda DDL e în `tenant_template.sql`. Se aplică:
tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_unic_numar_factura`.
"""
import sys

from core import db

_NUME_INDEX = "facturi_numar_emisa_uniq"
_DDL = ('CREATE UNIQUE INDEX IF NOT EXISTS %s ON "{s}".facturi '
        "(COALESCE(serie, ''), numar) WHERE directie = 'emisa';" % _NUME_INDEX)


def duplicate(conn, schema):
    """Listă de (serie, numar, count) duplicate pe emise — trebuie goală înainte de index."""
    with conn.cursor() as cur:
        cur.execute('SELECT COALESCE(serie, \'\') AS s, numar, count(*) AS n FROM "{s}".facturi '
                    "WHERE directie = 'emisa' GROUP BY COALESCE(serie, ''), numar "
                    "HAVING count(*) > 1 ORDER BY n DESC".format(s=schema))
        return cur.fetchall()


def aplica(conn, schema):
    """Creează indexul dacă nu există duplicate. Întoarce (creat: bool, duplicate: list)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    dup = duplicate(conn, schema)
    if dup:
        return False, dup
    with conn.cursor() as cur:
        cur.execute(_DDL.format(s=schema))
    return True, []


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname=%s AND indexname=%s",
                    (schema, _NUME_INDEX))
        return cur.fetchone()[0] == 1


def main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE COALESCE(activ, true) ORDER BY id")
            schemas = [r[0] for r in cur.fetchall()]
    ok = blocate = 0
    for s in schemas:
        with db.get_conn() as conn:
            creat, dup = aplica(conn, s)
            conn.commit()
        if creat:
            ok += 1
        else:
            blocate += 1
            print("  %-28s BLOCAT — duplicate de corectat (storno+reemitere): %s"
                  % (s, ", ".join("%s%s x%d" % (a, b, n) for a, b, n in dup[:5])))
    print("TOTAL: %d indici creați; %d scheme blocate de duplicate existente." % (ok, blocate))
    return 0


if __name__ == "__main__":
    sys.exit(main())
