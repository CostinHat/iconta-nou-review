# -*- coding: utf-8 -*-
"""GARD (sweep audit tenant_006): rutele de intrare MANUALĂ de declarație verifică eligibilitatea față
de vector înainte de a scrie — simetric cu d301_operatiuni_api. D300 cere plătitor (platitor_tva=True);
D390 cere operațiuni IC (operatiuni_ic=True). Altfel se creează stare inconsistentă (rânduri/linii pentru
o declarație pe care selectorul o blochează). Direcțional: eligibilul NU e blocat pe statut."""
from core.d300_manual_api import adauga as d300_adauga
from core.d390_clasificare_api import manual_adauga as d390_manual


class _Cur:
    def __init__(self, valori): self._v = valori; self._q = ""
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q, params=None): self._q = q
    def fetchone(self):
        if "platitor_tva" in self._q: return (self._v.get("platitor_tva"),)
        if "operatiuni_ic" in self._q: return (self._v.get("operatiuni_ic"),)
        return (999,)


class _Conn:
    def __init__(self, **valori): self._v = valori
    def cursor(self, *a, **k): return _Cur(self._v)
    def commit(self): pass


# --- D300 ---
def test_d300_neplatitor_blocat():
    r = d300_adauga(_Conn(platitor_tva=False), "t", 2026, 6,
                    {"rand": "R1", "baza": 1000, "tva": 210})
    assert r.get("eroare") and "plătitori" in r["eroare"], r


def test_d300_platitor_nu_e_blocat_de_statut():
    # platitor -> statutul nu blocheaza; rand invalid -> eroare de camp, nu blocul de statut
    r = d300_adauga(_Conn(platitor_tva=True), "t", 2026, 6,
                    {"rand": "ZZZ", "baza": 1000, "tva": 210})
    assert "plătitori" not in (r.get("eroare") or ""), r
    assert r.get("eroare"), "rand invalid trebuie sa dea eroare de camp"


# --- D390 ---
def test_d390_fara_ic_blocat():
    r = d390_manual(_Conn(operatiuni_ic=False), "t", 2026, 6, "A", "DE", "", "Furnizor", 1000)
    assert r.get("eroare") and "intracomunitare" in r["eroare"], r


def test_d390_cu_ic_nu_e_blocat_de_statut():
    # operatiuni_ic True -> statutul nu blocheaza; tip invalid -> eroare de camp
    r = d390_manual(_Conn(operatiuni_ic=True), "t", 2026, 6, "ZZ", "DE", "", "Furnizor", 1000)
    assert "nu are operațiuni intracomunitare" not in (r.get("eroare") or ""), r
    assert r.get("eroare"), "tip invalid trebuie sa dea eroare de camp"
