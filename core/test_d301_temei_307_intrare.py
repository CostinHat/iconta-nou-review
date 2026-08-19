# -*- coding: utf-8 -*-
"""GARD (audit tenant_006, temei_307): introducerea unei operatiuni D301 tip 4 (art. 307 alin. 3/5/6)
CERE temeiul (care alineat) - aceeasi regula la introducere ca la preview. Fara temei = respins."""
from core.d301_operatiuni_api import adauga


class _Cur:
    def __init__(self): self._q = ""
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q, params=None): self._q = q
    def fetchone(self):
        if "platitor_tva" in self._q: return (False,)   # neplatitor -> op D301 permisa
        return (99,)


class _Conn:
    def cursor(self, *a, **k): return _Cur()
    def commit(self): pass


_OP = {"nr_doc": "X", "data_doc": "15.06.2026", "val_valuta": 100, "tip_valuta": "EUR",
       "curs": 5, "cota": 21, "partener_tara": "DE", "partener_cod": "777888"}


def test_tip4_fara_temei_respins():
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP, tip=4))
    assert r.get("eroare") and "temei" in r["eroare"].lower(), r


def test_tip4_temei_invalid_respins():
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP, tip=4, temei_307="inexistent"))
    assert r.get("eroare") and "temei" in r["eroare"].lower(), r


def test_tip4_cu_temei_acceptat():
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP, tip=4, temei_307="gaz_energie"))
    assert r.get("ok"), r


def test_tip1_nu_cere_temei():
    # tip != 4 -> temeiul nu se cere
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP, tip=1))
    assert r.get("ok"), r
