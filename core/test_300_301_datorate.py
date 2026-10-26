# -*- coding: utf-8 -*-
"""300 + 301 — ce declarații i se propun firmei (comanda Costin 17.10.2026 7.2, verbatim în DECIZII).

300: „D390 · 10/2026 lipsește din «Datorate» deși F1A5 e prestare de servicii UE în octombrie; D112 apare la F1”.
301: „«Alte declarații» pliată, deschisă doar la cerere, numai declarațiile pe care un SRL le poate datora.”
Temei D390: CF art.325 alin.(1) lit.a — declarația recapitulativă cuprinde operațiunile „pentru care exigibilitatea taxei a luat
naștere în luna calendaristică respectivă” (text din `anaf_surse/cod_fiscal_227_2015_consolidat.txt`), deci o operațiune deja facturată în
luna în curs face D390 lunii datorat; absența se poate afirma numai după încheierea lunii.
"""
import datetime

from core import d390, control_fiscal_api as cf, termene_api

AZI = datetime.date(2026, 10, 17)


def test_300_d390_luna_deschisa_cu_factura_ic_e_datorat(monkeypatch):
    """MUTAȚIE: `if prima_urm > azi: return None` pus înaintea citirii facturilor (comportamentul vechi) -> pică."""
    monkeypatch.setattr(d390, "pull", lambda conn, schema, an, luna: ({}, ["F1A5"]))
    monkeypatch.setattr(d390, "_facturi_ic", lambda facturi: (list(facturi), {}))
    monkeypatch.setattr(d390, "pull_manual", lambda conn, schema, an, luna: [])
    assert d390.d390_are_operatiuni(object(), "x", 2026, 10, azi=AZI) is True
    monkeypatch.setattr(d390, "_facturi_ic", lambda facturi: ([], {}))
    assert d390.d390_are_operatiuni(object(), "x", 2026, 10, azi=AZI) is None, "luna deschisă fără IC: absența nu se afirmă"
    assert d390.d390_are_operatiuni(object(), "x", 2026, 9, azi=AZI) is False, "luna încheiată fără IC: nu se datorează"


def test_300_termenele_d112_din_fapt_nu_din_are_salariati(monkeypatch):
    """D112 din FAPT (salariat activ în lună), ca semaforul. MUTAȚIE: `d112_fapt=d112_fapt` scos din `termene_firma` -> D112 apare -> pică."""
    vector = {"platitor_tva": False, "tip_decont": None, "operatiuni_ic": False, "regim_fiscal": "micro", "tip_firma": "srl",
              "partida_simpla": False}
    cu = termene_api.termene_firma(vector, True, set(), AZI, d112_fapt=lambda a, l: False)
    assert not any(d["tip"] == "d112" for d in cu), cu
    assert any(d["tip"] == "d112" for d in termene_api.termene_firma(vector, True, set(), AZI, d112_fapt=lambda a, l: True))


def test_301_persoana_juridica_nu_vede_declaratiile_persoanelor_fizice():
    """MUTAȚIE: `else dict(_NEAP_PERSOANA_JURIDICA)` -> `else {}` -> pică."""
    pj = cf.neaplicabile_forma("srl")
    assert {"d204", "d212", "d216", "d230"} <= set(pj), pj
    assert pj["d212"] == "D212 nu se depune de o persoană juridică — e declarația unică a persoanelor fizice (impozitul pe venit și " \
                         "contribuțiile sociale).", pj["d212"]
    assert not set(cf.neaplicabile_forma("pfa")) & set(cf._NEAP_PERSOANA_JURIDICA), "la PFA declarațiile persoanei fizice rămân"
