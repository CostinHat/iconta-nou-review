# -*- coding: utf-8 -*-
"""Ce parteneri din D394 se schimbă după decizia 47 (factura bate fișa).

Se numără exact facturile EMISE pe care cele două surse **nu spun același lucru**: `tert_cui` de pe
document vs `clienti.cui` din fișă. Doar acolo se schimbă ceva; oriunde coincid, declarația iese
identică. Citire pură pe producție.
"""
import os
import sys

sys.path.insert(0, "/home/costin/iconta_nou")
os.chdir("/home/costin/iconta_nou")
from core import db  # noqa: E402

db.init_pool()
with db.get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database()")
        print("baza:", cur.fetchone()[0])
        cur.execute("SELECT id, schema_name, nume FROM public.tenants WHERE activ ORDER BY id")
        firme = cur.fetchall()

divergente = 0
fara_tert = 0
total_emise = 0
detalii = []
for tid, schema, nume in firme:
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % schema)
            try:
                cur.execute(
                    "SELECT f.id, f.numar, f.data_emitere, f.tert_cui, c.cui "
                    "  FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                    " WHERE f.directie = 'emisa' AND COALESCE(f.tip,'factura') = 'factura'")
                for fid, numar, data, tert, fisa in cur.fetchall():
                    total_emise += 1
                    t = (tert or "").replace("RO", "").strip()
                    fc = (fisa or "").replace("RO", "").strip()
                    if not t and fc:
                        fara_tert += 1
                        detalii.append((schema, numar, data, tert, fisa, "factura fara tert_cui -> ia din fisa"))
                    elif t and fc and t != fc:
                        divergente += 1
                        detalii.append((schema, numar, data, tert, fisa, "DIVERGENTA: se schimba"))
            except Exception:
                conn.rollback()

print("facturi emise (tip=factura): %d" % total_emise)
print("cu tert_cui DIFERIT de fisa (se schimba D394): %d" % divergente)
print("fara tert_cui, cu fisa completata (raman pe fisa, ca rezerva): %d" % fara_tert)
for d in detalii[:20]:
    print("   ", d)
