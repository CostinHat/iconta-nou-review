# -*- coding: utf-8 -*-
"""Teste core/anaf_api.py — freeze best-effort al statutului ANAF pe factura."""
from core import anaf_api


def test_furnizor_incasare_freeze_din_anaf(monkeypatch):
    # [A9 art.297 alin.2] statusTvaIncasare din ANAF -> True, indiferent de fallback
    monkeypatch.setattr(anaf_api, "valideaza_cui",
                        lambda l, data_interogare=None: [{"gasit": True, "tva_la_incasare": True}])
    assert anaf_api.furnizor_incasare_freeze("RO14399840", fallback=False) is True


def test_furnizor_incasare_freeze_anaf_jos_cade_pe_fallback(monkeypatch):
    def _boom(l, data_interogare=None):
        raise RuntimeError("ANAF jos")
    monkeypatch.setattr(anaf_api, "valideaza_cui", _boom)
    assert anaf_api.furnizor_incasare_freeze("RO1", fallback=True) is True
    assert anaf_api.furnizor_incasare_freeze("RO1", fallback=False) is False


def test_furnizor_incasare_freeze_cui_negasit_cade_pe_fallback(monkeypatch):
    monkeypatch.setattr(anaf_api, "valideaza_cui", lambda l, data_interogare=None: [{"gasit": False}])
    assert anaf_api.furnizor_incasare_freeze("RO1", fallback=True) is True


def test_3j_freeze_cere_statutul_la_data_data(monkeypatch):
    # [3j · HG 1/2016 titlul VII pct.67(6)] furnizor_incasare_freeze cere statutul RTVAI al furnizorului
    # ASA CUM ERA la `data` (data emiterii facturii), nu azi. Mutatie: revert `data_interogare=data` in
    # anaf_api -> data ajunge None -> assert pica.
    prins = {}

    def _fake(l, data_interogare=None):
        prins["d"] = data_interogare
        return [{"gasit": True, "tva_la_incasare": True}]
    monkeypatch.setattr(anaf_api, "valideaza_cui", _fake)
    anaf_api.furnizor_incasare_freeze("RO14399840", data="2016-10-10")
    assert prins["d"] == "2016-10-10", "statutul RTVAI trebuie cerut la data emiterii, nu la data curenta"


def test_3j_uc_tenants_paseaza_data_emitere():
    # [3j] cablare: factura_creeaza (uc_tenants) trece data=date.data_emitere catre freeze. Mutatie:
    # scoate `data=date.data_emitere` -> assert pica.
    import io as _io
    import os as _os
    import re as _re
    _r = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    s = _io.open(_os.path.join(_r, "core", "uc_tenants.py"), encoding="utf-8").read()
    assert _re.search(r"furnizor_incasare_freeze\(.*data=date\.data_emitere", s), \
        "uc_tenants nu mai paseaza data emiterii la furnizor_incasare_freeze (3j necablat)"
