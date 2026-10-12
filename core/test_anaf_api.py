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


def test_data_inregistrarii_din_anaf_ajunge_ca_data_infiintarii(monkeypatch):
    """[deficiența 229] `date_generale.data_inregistrare` (ANAF WS v9, `anaf_surse/doc_WS_V9.txt`: „Data inregistrare”; răspuns real
    12.10.2026 pentru 14399840: '2002-01-23', J2002000372404) se citește și trece la adăugarea firmei în `firma_profil.data_infiintare`.
    MUTAȚIE: câmpul scos din `valideaza_cui` -> pică."""
    class _R:
        status_code = 200

        def json(self):
            return {"found": [{"date_generale": {"cui": 14399840, "denumire": "DANTE INTERNATIONAL SA", "data_inregistrare": "2002-01-23",
                                                 "nrRegCom": "J2002000372404"}, "inregistrare_scop_Tva": {}}], "notFound": []}
    monkeypatch.setattr(anaf_api.requests, "post", lambda *a, **k: _R())
    r = anaf_api.valideaza_cui([14399840], data_interogare="2026-10-12")
    assert r[0]["data_inregistrare"] == "2002-01-23", r
