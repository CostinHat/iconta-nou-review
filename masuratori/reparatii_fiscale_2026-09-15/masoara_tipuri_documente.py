# -*- coding: utf-8 -*-
"""Câte documente de fiecare TIP există în portofoliu — ca să se știe dacă „zero schimbări"
înseamnă „defectul n-a atins pe nimeni" sau „măsurătoarea s-a uitat în altă parte"."""
import os
import sys

sys.path.insert(0, "/home/costin/iconta_nou")
os.chdir("/home/costin/iconta_nou")
from core import db  # noqa: E402

db.init_pool()
with db.get_conn() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), count(*) FROM public.tenants WHERE activ")
        print("baza:", cur.fetchone())
        cur.execute("SELECT id, schema_name FROM public.tenants WHERE activ ORDER BY id")
        firme = cur.fetchall()

tot = {}
facturi_total = 0
for tid, schema in firme:
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % schema)
            try:
                cur.execute("SELECT COALESCE(tip,'(null)') AS tip, COALESCE(status,'(null)'), count(*) "
                            "FROM facturi GROUP BY 1,2")
                for tip, status, n in cur.fetchall():
                    tot[(tip, status)] = tot.get((tip, status), 0) + n
                    facturi_total += n
            except Exception:
                conn.rollback()

print("documente in portofoliu: %d" % facturi_total)
for (tip, status), n in sorted(tot.items(), key=lambda x: -x[1]):
    print("   %-10s %-14s %6d" % (tip, status, n))
