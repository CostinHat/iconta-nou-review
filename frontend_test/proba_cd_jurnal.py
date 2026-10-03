# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — jurnalul bifei „C&D” (decizia Costin 04.10.2026: „fiecare schimbare se jurnalizează: utilizator,
dată, valoare veche → nouă”).

    python frontend_test/proba_cd_jurnal.py <radacina_cod>
F1 (tenant_049) din baza de producție, calea aplicației (`uc_tenants.mijloc_fix_destinatie_cd`, utilizatorul din ctx), pe un
activ TEMPORAR, într-o tranzacție ANULATĂ (`commit` neutralizat): bifa pusă, apăsată din nou pe aceeași valoare, scoasă.
  · cod VECHI: bifa se schimbă, jurnalul rămâne gol — nimeni nu poate spune cine a deschis amortizarea accelerată;
  · cod NOU: două rânduri (false->true, true->false), cu utilizatorul și ora; apăsarea fără schimbare nu scrie nimic.
"""
import contextlib
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, uc_tenants  # noqa: E402

observare.alerteaza = lambda *a, **k: None
S = "tenant_049"
db.init_pool()
real = db.get_conn


class _Fara:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


with real() as conn:
    px = _Fara(conn)

    def _gc(schema=None, *a, **k):
        if schema:
            conn.cursor().execute("SET search_path TO %s, public" % schema)
        yield px
    db.get_conn = contextlib.contextmanager(_gc)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name=%s", (S,))
        tid, cab = cur.fetchone()
        cur.execute("SELECT id, email FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        uid, email = cur.fetchone()
        ctx = {"uid": uid, "rol": "admin_firma"}
        cur.execute("INSERT INTO %s.mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, "
                    "data_pif, metoda) VALUES ('PRB-CDJ','Spectrometru PROBA','2132','2813',60000,0,60,'2026-01-15','liniara') "
                    "RETURNING id" % S)
        mid = cur.fetchone()[0]
        print("=== COD: %s · F1, activ temporar %s, utilizator %s (id %s)" % (RAD, mid, email, uid))
        for v in (True, True, False):
            r = uc_tenants.mijloc_fix_destinatie_cd(tid, mid, {"destinatie_cd": "1" if v else "0"}, ctx)
            print("  bifa C&D -> %s: %s" % ("da" if v else "nu", r))
        cur.execute("SELECT to_regclass(%s)", ("%s.mijloace_fixe_jurnal" % S,))
        if cur.fetchone()[0]:
            cur.execute("SELECT camp, valoare_veche, valoare_noua, user_id, to_char(la, 'YYYY-MM-DD HH24:MI') FROM "
                        "%s.mijloace_fixe_jurnal WHERE mijloc_id=%%s ORDER BY id" % S, (mid,))
            rows = cur.fetchall()
            print("  jurnal: %d rânduri" % len(rows))
            for x in rows:
                print("   ", x)
        else:
            print("  jurnal: tabelul nu există")
    finally:
        db.get_conn = real
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
