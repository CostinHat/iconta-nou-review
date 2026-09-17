# -*- coding: utf-8 -*-
"""core/migrare_curs_lei.py — backfill ONEST al conversiei in lei pe facturile ISTORICE.

DE CE (A1, 17.09.2026). Coloanele `curs_bnr/total_lei/tva_lei` existau, dar se scriau doar la emiterea
in valuta; facturile RON si cele PRIMITE aveau `total_lei = NULL`, iar generatoarele nu le citeau
oricum. De acum `creeaza_factura` scrie sumele in lei la INSERT pentru orice factura noua (RON->curs
1), iar declaratiile citesc lei. Facturile istorice raman insa cu `NULL`.

CE FACE, si CAT DE DEPARTE MERGE:
  - factura in RON fara `total_lei`: cursul e 1 PRIN LEGE, deci lei = valoarea. Se completeaza
    `curs_bnr=1, total_lei=total, tva_lei=tva, data_curs=data_emitere, curs_sursa='ron'`. E o
    CUNOASTERE, nu o ghicire.
  - factura in VALUTA fara curs: cursul istoric NU se poate sti din nimic de pe factura. NU se
    completeaza (interdictia 32: un necunoscut nu se rotunjeste la „stiu ca nu"). Ramane `NULL`, iar
    contarea o refuza si declaratiile o exclud, SEMNALAT — nu intra tacit ca lei.

Idempotent: atinge doar randurile cu `total_lei IS NULL`. Nu suprascrie o conversie deja scrisa.
Se aplica: tenanti NOI n-au nevoie (template + `creeaza_factura`); EXISTENTI prin
`python3 -m core.migrare_curs_lei`.
"""
import sys

from core import db


def aplica(conn, schema):
    """Backfill pe o schema. Intoarce (ron_completate, valuta_ramase_nule)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        # RON fara lei -> curs 1, lei = valoarea. `moneda` NULL istoric = RON (default coloanei).
        cur.execute(
            'UPDATE "{s}".facturi SET curs_bnr=1, total_lei=total, tva_lei=tva, '
            "data_curs=data_emitere, curs_sursa='ron' "
            "WHERE total_lei IS NULL AND (moneda IS NULL OR upper(moneda)='RON')".format(s=schema))
        ron = cur.rowcount
        # Valuta fara curs: raman NULL (necunoastere), doar le numaram pentru raport.
        cur.execute(
            'SELECT count(*) FROM "{s}".facturi WHERE total_lei IS NULL '
            "AND moneda IS NOT NULL AND upper(moneda) <> 'RON'".format(s=schema))
        valuta_nule = cur.fetchone()[0]
    return ron, valuta_nule


def verifica(conn, schema):
    """Nicio factura RON nu mai are `total_lei` NULL (backfill complet pe partea cunoscuta)."""
    with conn.cursor() as cur:
        cur.execute(
            'SELECT count(*) FROM "{s}".facturi WHERE total_lei IS NULL '
            "AND (moneda IS NULL OR upper(moneda)='RON')".format(s=schema))
        return cur.fetchone()[0] == 0


def _schemas(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE COALESCE(activ, true) ORDER BY id")
        return [r[0] for r in cur.fetchall()]


def main():
    db.init_pool()
    with db.get_conn() as conn:
        schemas = _schemas(conn)
    total_ron = total_val = 0
    for s in schemas:
        with db.get_conn() as conn:
            ron, val = aplica(conn, s)
            conn.commit()
        total_ron += ron
        total_val += val
        print("  %-28s RON completate=%-5d  valuta ramase NULE=%d" % (s, ron, val))
    print("TOTAL: %d facturi RON completate; %d facturi in valuta raman fara curs "
          "(necunoscut istoric — semnalate la contare/declaratie)." % (total_ron, total_val))
    return 0


if __name__ == "__main__":
    sys.exit(main())
