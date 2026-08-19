# -*- coding: utf-8 -*-
"""GARD (audit 006/R24.1, clasa preview↔salvare): la introducerea unei operațiuni D301 cu furnizor UE,
algoritmul codului de TVA (offline: DE/FR/HR) se verifică ACUM — simetric cu cifra de control a CUI RO la
partenerii interni — și produce un AVERTISMENT (neblocant), nu abia la respingerea DUK (R24.1). Fără asta,
codul era acceptat tăcut + confirmat „→ D390 cod A", apoi respins de validator: aceeași regulă, verdicte
diferite în etape diferite."""
from core.d301_operatiuni_api import adauga


class _Cur:
    def __init__(self): self._q = ""
    def __enter__(self): return self
    def __exit__(self, *a): pass
    def execute(self, q, params=None): self._q = q
    def fetchone(self):
        if "platitor_tva" in self._q: return (False,)   # neplatitor -> op D301 permisa
        return (777,)  # oid la INSERT


class _Conn:
    def cursor(self, *a, **k): return _Cur()
    def commit(self): pass


_OP = {"tip": 1, "nr_doc": "INV-1", "data_doc": "15.06.2026",
       "val_valuta": 1000, "tip_valuta": "EUR", "curs": 4.97, "cota": 21}


def test_cod_de_invalid_da_avertisment_la_introducere():
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP, partener_tara="DE", partener_cod="811234567"))
    assert r.get("ok"), r  # neblocant - operatiunea se inregistreaza
    assert r.get("avertisment") and "R24.1" in r["avertisment"], \
        "cod DE care pica algoritmul trebuie sa dea avertisment la introducere: %r" % r.get("avertisment")


def test_fara_partener_fara_avertisment():
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP))
    assert r.get("ok") and not r.get("avertisment"), r


def test_cod_de_valid_fara_avertisment():
    # cod DE valid (checksum MOD 11,10 corect) -> fara avertisment
    from core.d390 import _vies_mod1110
    corp = "12345678"
    cod = corp + str(_vies_mod1110(corp))  # 8 cifre + cifra de control corecta = 9
    r = adauga(_Conn(), "t", 2026, 6, dict(_OP, partener_tara="DE", partener_cod=cod))
    assert r.get("ok") and not r.get("avertisment"), (cod, r)
