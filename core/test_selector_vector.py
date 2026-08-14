# -*- coding: utf-8 -*-
"""S1 + #2 (plimbare 14.08.2026): selectorul de declaratii respecta vectorul TVA si periodicitatea firmei.
Garda anti-divergenta: ce e neaplicabil in selector NU trebuie sa apara datorat in semafor (obligatii_datorate)."""
import datetime
from core import declaratii_api as da, control_fiscal_api as cf

AZI = datetime.date(2026, 8, 14)


def test_periodicitate_firma_urmeaza_tip_decont():
    # #2: D300/D394/D406 urmeaza tip_decont; static ignora
    assert da.periodicitate_firma("d300", "T") == "trimestrial"
    assert da.periodicitate_firma("d300", "L") == "lunar"
    assert da.periodicitate_firma("d394", "trimestrial") == "trimestrial"
    assert da.periodicitate_firma("d406", "T") == "trimestrial"
    # fara tip_decont -> static
    assert da.periodicitate_firma("d300", None) == da.periodicitate("d300")
    # D101 nu e in setul TVA -> ramane anual indiferent de tip_decont
    assert da.periodicitate_firma("d101", "T") == "anual"


def test_selector_neplatitor_nu_ofera_d300_d394():
    neap = cf.neaplicabile_selector({"tip_firma": "srl", "platitor_tva": False, "operatiuni_ic": False})
    assert "d300" in neap and "d394" in neap and "d390" in neap
    # anti-divergenta: ce e neaplicabil in selector NU apare datorat in semafor
    vec = {"regim_fiscal": "profit", "platitor_tva": False, "tip_decont": None,
           "operatiuni_ic": False, "partida_simpla": False}
    dat = {d["tip"] for d in cf.declaratii_datorate(vec, are_salariati=False, azi=AZI)["datorate"]}
    assert not (dat & set(neap)), "divergenta selector-vs-semafor: %s" % (dat & set(neap))


def test_selector_platitor_ofera_d300_nu_d301():
    neap = cf.neaplicabile_selector({"tip_firma": "srl", "platitor_tva": True, "operatiuni_ic": True})
    assert "d300" not in neap and "d394" not in neap   # platitor -> D300/D394 aplicabile
    assert "d301" in neap                                # D301 e pt neinregistrati
    assert "d390" not in neap                            # are operatiuni IC


def test_selector_partida_simpla_pastreaza_forma():
    neap = cf.neaplicabile_selector({"tip_firma": "pfa", "platitor_tva": False, "operatiuni_ic": False})
    assert "d100" in neap and "d101" in neap and "d406" in neap   # forma (persoana juridica)
