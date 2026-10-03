# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 9: regularizarea dividendelor interimare.

    python frontend_test/proba_lot19_d9_dividende_interimare.py <radacina_cod>
F1 (tenant_049) din baza de producție, calea aplicației: `uc_tenants.nota_asociati` (ruta /nota-asociati, ecranul
Operațiuni › Decontări asociați), pe o singură conexiune al cărei `commit` e neutralizat; ROLLBACK la final.
Ciclul: dividende interimare 2025 brut 50.000 (impozit 10% = 5.000, net 45.000 plătit) -> la aprobare (30.04.2026)
dividend anual 30.000 -> asociatul restituie NETUL excesului, 18.000 (20.05.2026) -> bugetul restituie impozitul
excesului, 2.000 (CPF art.170^1).
  · cod VECHI: nota de regularizare poartă 5121=463 20.000 la 30.04 (încasare care nu a avut loc); după încasarea
    reală de 18.000, 463 iese pe CREDIT (-18.000), 5121 umflat; „interimar” nu se poate cere din ecran;
  · cod NOU: regularizarea fără încasări; 463 = 2.000 debit după restituirea asociatului (impozit de recuperat),
    0 după restituirea bugetului; încasările 5121 = exact cele două sume încasate.
"""
import contextlib
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, uc_tenants, decontari_asociati  # noqa: E402

observare.alerteaza = lambda *a, **k: None
NOU = hasattr(decontari_asociati, "nota_restituire_dividend")
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
    proxy = _Fara(conn)
    db.get_conn = contextlib.contextmanager(lambda *a, **k: (yield proxy))
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name='tenant_049'")
        tid, cab = cur.fetchone()
        cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        ctx = {"uid": cur.fetchone()[0], "rol": "admin_firma"}
        ids = []

        def nota(corp):
            try:
                r = uc_tenants.nota_asociati(tid, corp, ctx)
            except Exception as e:
                print("  %-26s REFUZ: %s" % (corp["operatie"], e))
                return None
            ids.append(r["inregistrare_id"])
            extra = {k: v for k, v in r.items() if k not in ("inregistrare_id", "linii")}
            print("  %-26s %s %s" % (corp["operatie"] + " " + corp["data"], r["linii"], extra or ""))
            return r

        nota({"data": "2025-09-30", "operatie": "dividend", "brut": 50000, "interimar": "1"})
        nota({"data": "2026-04-30", "operatie": "regularizare", "total_interimar": 50000, "dividend_anual": 30000,
              "impozit_interimar": 5000})
        if NOU:
            nota({"data": "2026-05-20", "operatie": "restituire_dividend", "suma_restituita": 18000})
            nota({"data": "2026-09-15", "operatie": "restituire_dividend", "suma_restituita": 2000})
        else:
            # încasarea REALĂ de la asociat, pe extras (calea veche n-avea operație: nota de bancă 5121=463)
            cur.execute("SET search_path TO tenant_049, public")
            cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status) VALUES ('2026-05-20', "
                        "'extras: restituire asociat', 'facturi', 'ciorna') RETURNING id")
            i = cur.fetchone()[0]
            ids.append(i)
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                        "VALUES (%s, '5121', '463', 18000)", (i,))
            print("  extras 2026-05-20           [['5121', '463', '18000']] (încasarea reală, netul)")
        cur.execute("SET search_path TO tenant_049, public")
        cur.execute("""SELECT COALESCE(SUM(CASE WHEN cont_debit='463' THEN suma ELSE 0 END),0)
                            - COALESCE(SUM(CASE WHEN cont_credit='463' THEN suma ELSE 0 END),0),
                              COALESCE(SUM(CASE WHEN cont_debit='5121' THEN suma ELSE 0 END),0)
                       FROM inregistrari_linii WHERE inregistrare_id = ANY(%s)""", (ids,))
        s463, inc = cur.fetchone()
        print("  => sold 463: %s (debit +) · încasări 5121 înregistrate: %s · încasări reale: %s"
              % (s463, inc, "20000 (18000 + 2000)" if NOU else "18000"))
    finally:
        db.get_conn = real
        conn.rollback()
        print("  ROLLBACK — nimic scris")
