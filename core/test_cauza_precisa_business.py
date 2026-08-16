# -*- coding: utf-8 -*-
"""GARD cauza_precisa: cand un verificator din control_incrucisat prinde o eroare de BUSINESS
(ValueError din d112/d300 - CAEN out-of-enum, CUI invalid), remediul poarta MESAJUL PRECIS al erorii,
nu genericul 'Date lipsa sau profil incomplet' care contrazice explicatia (profilul e complet). Q3.
Fix #18 din M2 acoperise doar PerioadaNeconfirmata; ValueError-ele de business erau lasate pe generic."""
import io


def test_d112_valueerror_business_da_cauza_precisa(monkeypatch):
    from core import d112 as _d112
    from core import control_incrucisat as _ci
    def _boom(*a, **k):
        raise ValueError("D112: CAEN firma '6210' nu exista in nomenclatorul acceptat de D112.")
    monkeypatch.setattr(_d112, "genereaza", _boom)
    r = _ci.verifica_d112(None, "tenant_x", 2026, 8)
    rem = r["constatari"][0]["remediu"]
    assert "nomenclator" in rem["cauza"], "cauza nu poarta mesajul precis al ValueError-ului de business (Q3)"
    assert "Date lips" not in rem["cauza"], "genericul inca acopera explicatia precisa (Q3)"


def test_d112_runtimeerror_ramane_generic(monkeypatch):
    # o eroare NEASTEPTATA (bug, nu business) trebuie sa ramana pe genericul sigur - nu expunem bug intern.
    from core import d112 as _d112
    from core import control_incrucisat as _ci
    def _boom(*a, **k):
        raise RuntimeError("stack trace intern")
    monkeypatch.setattr(_d112, "genereaza", _boom)
    r = _ci.verifica_d112(None, "tenant_x", 2026, 8)
    assert r["constatari"][0]["remediu"]["cauza"] == "Date lipsă sau profil incomplet."
