# -*- coding: utf-8 -*-
"""Teste core/anaf_api.py — freeze best-effort al statutului ANAF pe factura."""
from core import anaf_api


def test_furnizor_incasare_freeze_din_anaf(monkeypatch):
    # [A9 art.297 alin.2] statusTvaIncasare din ANAF -> True, indiferent de fallback
    monkeypatch.setattr(anaf_api, "valideaza_cui",
                        lambda l: [{"gasit": True, "tva_la_incasare": True}])
    assert anaf_api.furnizor_incasare_freeze("RO14399840", fallback=False) is True


def test_furnizor_incasare_freeze_anaf_jos_cade_pe_fallback(monkeypatch):
    def _boom(l):
        raise RuntimeError("ANAF jos")
    monkeypatch.setattr(anaf_api, "valideaza_cui", _boom)
    assert anaf_api.furnizor_incasare_freeze("RO1", fallback=True) is True
    assert anaf_api.furnizor_incasare_freeze("RO1", fallback=False) is False


def test_furnizor_incasare_freeze_cui_negasit_cade_pe_fallback(monkeypatch):
    monkeypatch.setattr(anaf_api, "valideaza_cui", lambda l: [{"gasit": False}])
    assert anaf_api.furnizor_incasare_freeze("RO1", fallback=True) is True
