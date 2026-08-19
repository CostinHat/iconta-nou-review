# -*- coding: utf-8 -*-
"""Teste D402 (declaratie informativa DAC1 - venituri salariale/asimilate platite in Romania
unor beneficiari nerezidenti UE; OMFP 2727/2015). Structura = XSD OFICIAL ANAF
(anaf_surse/d402_20160226.xsd) + D402Validator.jar. Aici probam GOLDEN pe date POPULATE:
fixtura valida -> erori_generare gol -> XML generat VALIDEAZA contra XSD-ului oficial (lxml).
DUK e lenient ([[duk-lenient-audit-field-by-field]]); XSD-ul e a doua cale, structurala."""
import os
import pytest
from lxml import etree
from core import d402

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_XSD = os.path.join(_RAD, "anaf_surse", "d402_20160226.xsd")


def _manual():
    return {
        "cif": "14399840", "den_p": "SC EXEMPLU SRL", "adresa_p": "Str Exemplu 1 Otopeni",
        "tip_p": 1, "forma_jurid_p": 2, "d_rec": 0,
        "nume_declar": "Popescu", "prenume_declar": "Ion", "functie_declar": "Administrator",
        "beneficiari": [{
            "id_benef": 1, "nume": "Schmidt Hans", "nationalitate": "DE",
            "data_nasterii": "15.03.1980", "stat_r": "DE", "localitate_r": "Berlin",
            "strada_r": "Hauptstrasse", "nr_r": "10", "codp_r": "10115",
            "cif_rom": "1800101412340", "calitate_b": 1, "tip_adr": 1, "categ_b": 1,
            "impozit_venit": 800,
            "venituri": [{
                "id_venit": 1, "tip_venit": 4, "da_nu": 1, "data_i": "01.01.2024",
                "data_s": "31.12.2024", "per_venit": 1, "regim_fisc": 1,
                "suma_venit": 12000, "moneda_venit": "EUR",
            }],
        }],
    }


def test_d402_fixtura_valida_fara_erori():
    er = d402.erori_generare({"an": 2024}, _manual())
    assert not er, "fixtura d402 ar trebui valida, dar erori_generare intoarce: %s" % er


def test_d402_xml_valideaza_xsd_oficial():
    """GOLDEN structural: XML-ul generat pe date populate valideaza contra XSD-ului oficial ANAF."""
    xml = d402.build_xml({"an": 2024}, 2024, 12, _manual())
    schema = etree.XMLSchema(etree.parse(_XSD))
    doc = etree.fromstring(xml.encode("utf-8"))
    ok = schema.validate(doc)
    assert ok, "XML D402 generat NU valideaza XSD-ul oficial: %s" % schema.error_log


def test_d402_calcul_total_suma_randuri():
    """DUK regula R14: totalPlata_A = suma tuturor Suma_venit din toate <venit>
    (Regula 14.2 - totalul afisat = suma randurilor). Probat pe 2 venituri."""
    m = _manual()
    m["beneficiari"][0]["venituri"].append({
        "id_venit": 2, "tip_venit": 4, "da_nu": 1, "data_i": "01.06.2024",
        "per_venit": 1, "regim_fisc": 1, "suma_venit": 3000, "moneda_venit": "EUR",
    })
    c = d402.calcul_d402(m)
    assert c["totalPlata_A"] == 15000 and c["nr_venituri"] == 2  # 12000 + 3000
