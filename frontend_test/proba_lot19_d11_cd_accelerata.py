# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 11: amortizarea accelerată a aparaturii C&D din orice cont (CF art.20 alin.(1)
lit.b)).

    python frontend_test/proba_lot19_d11_cd_accelerata.py <radacina_cod>
F1 (tenant_049) din baza de producție, calea aplicației: `uc_tenants.nota_inventariere` (Operațiuni › Inventariere ›
Plus mijloc fix, cum trimite ecranul) -> `tenant_mijloace_fixe` (registrul) -> `mijloc_fix_destinatie_cd` (bifa din
registru). `commit` neutralizat, ROLLBACK la final.
  · cod VECHI: spectrometrul de laborator pe 2132 cu metoda accelerată e refuzat (nu există bifa C&D);
  · cod NOU: cu bifa, intră și se amortizează accelerat; scoasă bifa, registrul arată refuzul cu temeiul.
"""
import contextlib
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, uc_tenants  # noqa: E402

observare.alerteaza = lambda *a, **k: None
NOU = hasattr(uc_tenants, "mijloc_fix_destinatie_cd")
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
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
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name='tenant_049'")
        tid, cab = cur.fetchone()
        cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        ctx = {"uid": cur.fetchone()[0], "rol": "admin_firma"}
        corp = {"data": "2026-09-30", "operatie": "plus_mf", "valoare": 60000, "denumire": "Spectrometru laborator C&D",
                "cont_imobilizare": "2132", "dnf_luni": 60, "data_pif": "2026-01-15", "metoda": "accelerata",
                "destinatie_cd": "1"}
        try:
            r = uc_tenants.nota_inventariere(tid, corp, ctx)
            mid = r.get("mijloc_fix_id")
            print("  plus mijloc fix 2132, accelerată, C&D=da: ÎNREGISTRAT (id %s), nota %s" % (mid, r["linii"]))
        except Exception as e:
            mid = None
            print("  plus mijloc fix 2132, accelerată, C&D=da: REFUZ — %s" % str(getattr(e, "mesaj", e))[:200])
        if mid:
            def rand():
                lst = uc_tenants.tenant_mijloace_fixe(tid, ctx)["mijloace"]
                return [x for x in lst if x["id"] == mid][0]
            x = rand()
            print("  registru: metoda %s · C&D %s · amortizat la zi %s · rămas %s · eroare %s"
                  % (x["metoda"], x.get("destinatie_cd"), x["amortizat"], x["ramas"], x["eroare"]))
            uc_tenants.mijloc_fix_destinatie_cd(tid, mid, {"destinatie_cd": "0"}, ctx)
            x = rand()
            print("  după bifa C&D=nu: amortizat %s · eroare: %s" % (x["amortizat"], (x["eroare"] or "")[:170]))
    finally:
        db.get_conn = real
        conn.rollback()
        print("  ROLLBACK — nimic scris")
