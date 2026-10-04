# -*- coding: utf-8 -*-
"""PROBĂ CAP-COADĂ — salariul în timp (decizia Costin 04.10.2026): schimbarea salariului cu dată de la care se aplică.

    python frontend_test/proba_salariu_in_timp.py <radacina_cod>
F1 (tenant_049) din baza de producție, calea aplicației (`uc_tenants.salariat_actualizeaza`, cererea ca `SalariatEdit`),
într-o tranzacție ANULATĂ (`commit` neutralizat). Georgescu Ilie: 4.400 lei de la 01.01.2026.
  A. refuzurile: 31.02.2026 (zi inexistentă); 01.12.2025 (înainte de angajare); 01.01.2026 (dată deja în istoric —
     „suprapusă”); 10.07.2026 cu iulie închisă (luna declarată nu se rescrie);
  B. mărirea la 5.000 lei de la 15.09.2026 -> statul de plată din septembrie împarte luna: 10 zile lucrătoare la 4.400 +
     12 la 5.000 (din 22) = 2.000 + 2.727,27 = 4.727,27; D112 septembrie poartă brutul realizat și salariul contractual nou,
     DUK valid;
  C. aceeași dată din nou -> refuz cu intrarea existentă; cu înlocuire explicită -> trece.
  · cod VECHI: acceptă ziua inexistentă (cade în driver), data dinaintea angajării, rescrie tăcut 01.01 și luna închisă;
  · cod NOU: patru refuzuri numite pe câmpul `valabil_din`, apoi aceeași proratare.
"""
import contextlib
import os
import sys
import xml.etree.ElementTree as ET

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, uc_tenants, stat_plata_api, d112, duk  # noqa: E402
from main import SalariatEdit  # noqa: E402

observare.alerteaza = lambda *a, **k: None
S, SID, AN, LUNA = "tenant_049", 3, 2026, 9
print("=== COD: %s" % RAD)


class _Fara:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


def _detaliu(e):
    d = getattr(e, "detaliu", e)
    if isinstance(d, dict):
        camp = [x.get("camp") for x in (d.get("erori_campuri") or [])]
        return "cod=%s câmp=%s — %s" % (d.get("cod"), camp, (d.get("mesaj") or "")[:170])
    return str(d).split("\n")[0][:200]


db.init_pool()
real = db.get_conn
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
        cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        ctx = {"uid": cur.fetchone()[0], "rol": "admin_firma"}

        def schimba(et, **k):
            try:
                cur.execute("SAVEPOINT s")
                r = uc_tenants.salariat_actualizeaza(tid, SID, SalariatEdit(**k), ctx)
                cur.execute("RELEASE SAVEPOINT s")
                print("  %s: ACCEPTAT %s" % (et, r))
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT s")
                print("  %s: REFUZ %s" % (et, _detaliu(e)))

        print("A. refuzuri")
        schimba("zi inexistentă 31.02.2026", salariu_brut=5000, valabil_din="2026-02-31")
        schimba("înainte de angajare 01.12.2025", salariu_brut=5000, valabil_din="2025-12-01")
        schimba("dată deja în istoric 01.01.2026", salariu_brut=4600, valabil_din="2026-01-01")
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 7)")
        schimba("iulie închisă, de la 10.07.2026", salariu_brut=5000, valabil_din="2026-07-10")
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("DELETE FROM perioade_blocate WHERE an=2026 AND luna=7")
        cur.execute("SELECT valabil_din, salariu_brut FROM salariu_istoric WHERE salariat_id=%s ORDER BY 1", (SID,))
        print("  istoric după refuzuri: %s" % cur.fetchall())
        print("B. mărire la 5000 de la 15.09.2026")
        schimba("mărire 15.09.2026", salariu_brut=5000, valabil_din="2026-09-15")
        st = {r["id"]: r for r in stat_plata_api.stat_plata(conn, S, AN, LUNA)}
        g = st[SID]
        print("  stat de plată septembrie, Georgescu: brut %s · CAS %s · CASS %s · impozit %s · net %s"
              % (g["brut"], g["cas"], g["cass"], g["impozit"], g["net"]))
        xml, res = d112.genereaza(conn, S, AN, LUNA)
        rad = ET.fromstring(xml.split("?>", 1)[1] if xml.startswith("<?xml") else xml)
        for el in rad.iter():
            if el.tag.split("}")[-1] == "asigurat" and el.get("prenAsig", "").upper().startswith("ILIE"):
                b1 = [x for x in el.iter() if x.tag.split("}")[-1] == "asiguratB1"]
                print("  D112 Georgescu asiguratB1: %s" % [{k: v for k, v in x.attrib.items()
                                                            if k in ("B1_brutSalarii", "B1_sal1", "B1_sal2", "B1_7", "B1_8")}
                                                           for x in b1])
        v = duk.valideaza(xml, "d112", an=AN, luna=LUNA, timeout=240)
        print("  DUK D112: %s%s" % (v["stare"], (" — " + (v.get("erori") or "")[:160]) if v.get("erori") else ""))
        print("C. aceeași dată din nou")
        schimba("15.09.2026 din nou (5100)", salariu_brut=5100, valabil_din="2026-09-15")
        schimba("15.09.2026, înlocuire explicită", salariu_brut=5100, valabil_din="2026-09-15", inlocuieste=True)
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("SELECT valabil_din, salariu_brut FROM salariu_istoric WHERE salariat_id=%s ORDER BY 1", (SID,))
        print("  istoric final: %s" % cur.fetchall())
    finally:
        db.get_conn = real
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
