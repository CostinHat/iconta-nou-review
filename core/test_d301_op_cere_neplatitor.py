# -*- coding: utf-8 -*-
"""GARD (audit tenant_006): ecranul D301 (adauga operatiune -> d301_operatiuni) NU accepta operatiuni
daca firma e platitoare de TVA (platitor_tva=True). D301 (decont special art.324) e DOAR pentru
neplatitori; altfel se creeaza stare inconsistenta ca tenant_006 (3 operatiuni pentru o declaratie pe
care selectorul o blocheaza cu 'firma e platitoare'). Refuz cu mesaj care indruma spre Vectorul fiscal."""
from core.d301_operatiuni_api import adauga


class _FakeCur:
    def __init__(self, platitor):
        self._p = platitor
        self._last = ""
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q, params=None): self._last = q
    def fetchone(self):
        if "platitor_tva" in self._last:
            return (self._p,)
        return (12345,)  # oid la INSERT


class _FakeConn:
    def __init__(self, platitor): self._p = platitor
    def cursor(self, *a, **k): return _FakeCur(self._p)
    def commit(self): pass


_OP_VALIDA = {"tip": 1, "nr_doc": "INV-DE-1", "data_doc": "15.06.2026",
              "val_valuta": 1000, "tip_valuta": "EUR", "curs": 4.97, "cota": 21}


def test_platitor_tva_blocheaza_operatiunea_d301():
    r = adauga(_FakeConn(True), "tenant_x", 2026, 6, dict(_OP_VALIDA))
    assert r.get("eroare") and "plătitoare" in r["eroare"], r


def test_neplatitor_nu_e_blocat_de_statut():
    # platitor_tva=False -> statutul NU blocheaza; cu un camp invalid (tip) primim eroare de CAMP,
    # nu blocul de statut -> dovada ca garda e directionala (doar platitorii).
    r = adauga(_FakeConn(False), "tenant_x", 2026, 6, dict(_OP_VALIDA, tip=99))
    assert "plătitoare" not in (r.get("eroare") or ""), r
    assert r.get("eroare"), "un tip invalid trebuie sa dea eroare de camp"
