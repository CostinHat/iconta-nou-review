# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 10: ajustarea pentru bunuri de capital (CF art.305) în D300 rd.34 (R31_2).

    python frontend_test/proba_lot19_d10_d300_r31.py <radacina_cod>
F1 (tenant_049, plătitor TVA) din baza de producție, luna 08/2026. Calea aplicației: `d300_manual_api.adauga`
(ecranul «Rânduri manuale D300») -> `d300.genereaza` cu manual=None (calea de depunere: rândurile persistate) ->
validatorul DUK instalat. `commit` neutralizat, ROLLBACK la final.
  · cod VECHI: R31 refuzat la introducere (nu există cale de a declara ajustarea); R29 cu bază acceptat -> D300 invalid
    la DUK („R29_1: atribut necunoscut”);
  · cod NOU: R31 = -3.000 intră în rd.34 și în totalul R32, D300 valid; R29 cu bază refuzat la introducere.
"""
import os
import re
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, d300, d300_manual_api, duk  # noqa: E402
from core.common import Perioada  # noqa: E402

observare.alerteaza = lambda *a, **k: None
print("=== COD: %s (%s)" % (RAD, "NOU" if hasattr(d300, "RANDURI_ADITIVE") else "VECHI"))
S, AN, LUNA = "tenant_049", 2026, 8
db.init_pool()


class _Fara:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


with db.get_conn() as conn:
    px = _Fara(conn)
    try:
        conn.cursor().execute("SET search_path TO %s, public" % S)
        for cerere in ({"rand": "R31", "tva": -3000, "descriere": "ajustare art.305 - cladire vanduta scutit"},
                       {"rand": "R29", "baza": 1000, "tva": 210, "descriere": "restituire cumparator strain"}):
            r = d300_manual_api.adauga(px, S, AN, LUNA, cerere)
            print("  adaugă %s: %s" % (cerere["rand"], r.get("eroare") or "acceptat (id %s)" % r.get("id")))
        try:
            xml, res = d300.genereaza(px, S, Perioada(AN, luna=LUNA), None)
        except ValueError as e:
            print("  genereaza: REFUZ %s" % e)
        else:
            at = {k: re.search(r' %s="(-?\d+)"' % k, xml).group(1) for k in ("R31_2", "R32_2", "R29_1") if
                  re.search(r' %s="' % k, xml)}
            v = duk.valideaza(xml, "d300", an=AN, luna=LUNA, timeout=110)
            print("  D300 08/2026: %s · DUK: %s %s" % (at, v["stare"], (v.get("erori") or "")[:160].replace("\n", " ")))
    finally:
        conn.rollback()
        print("  ROLLBACK — nimic scris")
