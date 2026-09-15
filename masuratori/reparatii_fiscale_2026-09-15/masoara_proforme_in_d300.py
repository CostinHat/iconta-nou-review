# -*- coding: utf-8 -*-
"""Ce cifre D300 se schimbă pe portofoliu, după excluderea proformelor.

Măsurătoarea nu presupune nimic: pentru fiecare firmă și fiecare lună, se iau exact rândurile pe
care D300 le număra până acum și nu le va mai număra — proforme/avize cu status DECLARABIL, în
fereastra de exigibilitate. Suma lor e diferența, leu cu leu.

Rulează pe baza de PRODUCȚIE, în citire (`SELECT`), și nu scrie nimic.
"""
import os
import sys

sys.path.insert(0, "/home/costin/iconta_nou")
os.chdir("/home/costin/iconta_nou")

from core import db  # noqa: E402
from core.nomenclator_status_factura import clauza_sql, clauza_tip_document  # noqa: E402

db.init_pool()
STATUS = clauza_sql("f")
DOC = clauza_tip_document("f")

with db.get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, schema_name, nume FROM public.tenants WHERE activ ORDER BY id")
        firme = cur.fetchall()

print("firme active: %d" % len(firme))
total_randuri = total_baza = total_tva = 0
atinse = []
for tid, schema, nume in firme:
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % schema)
            try:
                cur.execute(
                    "SELECT to_char(COALESCE(f.data_faptului_generator, f.data_emitere), 'YYYY-MM') AS luna, "
                    "       COALESCE(f.tip, 'factura') AS tip, count(*), "
                    "       COALESCE(SUM(f.total - f.tva), 0), COALESCE(SUM(f.tva), 0) "
                    "  FROM facturi f "
                    " WHERE " + STATUS + " AND NOT (" + DOC + ") "
                    " GROUP BY 1, 2 ORDER BY 1, 2")
                randuri = cur.fetchall()
            except Exception as e:
                print("  %-14s EROARE: %s" % (schema, str(e)[:80]))
                conn.rollback()
                continue
    if randuri:
        atinse.append((schema, nume, randuri))
        for _luna, _tip, n, baza, tva in randuri:
            total_randuri += n
            total_baza += float(baza or 0)
            total_tva += float(tva or 0)

print()
print("FIRME ATINSE: %d din %d" % (len(atinse), len(firme)))
for schema, nume, randuri in atinse:
    print("  %s (%s)" % (schema, (nume or "")[:40]))
    for luna, tip, n, baza, tva in randuri:
        print("      %s  %-9s  %2d doc  baza %12.2f  TVA %10.2f" % (luna, tip, n, baza, tva))
print()
print("TOTAL documente scoase din D300: %d" % total_randuri)
print("TOTAL baza care nu se mai declara: %.2f lei" % total_baza)
print("TOTAL TVA care nu se mai declara:  %.2f lei" % total_tva)
