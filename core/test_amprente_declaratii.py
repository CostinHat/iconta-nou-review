# -*- coding: utf-8 -*-
"""GĂRZI R2 — amprentele declarațiilor pe portofoliu (`scripts/amprente_declaratii.py`, comanda Costin 08.10.2026, verbatim în DECIZII;
pașii R2/R8 din TESTE.md: „XML normalizat + SHA”, „Amprentele «după» = «înainte»”). Funcțiile pure; rularea pe portofoliu e artefactul."""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import amprente_declaratii as ad  # noqa: E402


def test_cererile_urmeaza_periodicitatea_fara_repetitii():
    """Fiecare perioadă cu date, o singură dată, la periodicitatea tipului. MUTAȚIE: trimestrul calculat `m // 3` -> martie cade în T1
    și ianuarie în T0 -> pică."""
    luni = [(2025, 1), (2025, 3), (2025, 4), (2025, 7), (2026, 12)]
    assert ad.perioade("lunar", luni) == [{"an": 2025, "luna": m} for m in (1, 3, 4, 7)] + [{"an": 2026, "luna": 12}]
    assert ad.perioade("trimestrial", luni) == [{"an": 2025, "trim": 1}, {"an": 2025, "trim": 2}, {"an": 2025, "trim": 3},
                                                {"an": 2026, "trim": 4}]
    assert ad.perioade("semestrial", luni) == [{"an": 2025, "luna": 6}, {"an": 2025, "luna": 12}, {"an": 2026, "luna": 12}]
    assert ad.perioade("anual", luni) == [{"an": 2025}, {"an": 2026}]
    assert [ad.eticheta(b) for b in ({"an": 2025, "trim": 3}, {"an": 2025, "luna": 7}, {"an": 2025})] == ["T3/2025", "07/2025", "2025"]


def test_amprenta_ignora_data_generarii_si_vede_orice_cifra():
    """Două generări ale aceleiași declarații diferă numai prin data generării: aceeași amprentă; o cifră schimbată: altă amprentă.
    MUTAȚIE: `rezultat` amprentează XML-ul brut (fără `_amprenta`) -> pică pe prima egalitate."""
    a = '<D300 data_generare="2026-10-10 10:00" R9_1="100"/>'
    b = '<D300 data_generare="2026-10-11 09:00" R9_1="100"/>'
    c = '<D300 data_generare="2026-10-10 10:00" R9_1="101"/>'
    assert ad.rezultat(xml=a) == ad.rezultat(xml=b)
    assert ad.rezultat(xml=a) != ad.rezultat(xml=c)
    assert ad.rezultat(xml=a.encode("utf-8")) == ad.rezultat(xml=a)


def test_pe_firmele_din_afara_cabinetului_de_test_nu_se_pastreaza_text():
    """Comanda: amprenta, nu conținutul. Refuzul unei firme reale poate numi date ale ei (CUI, parteneri): se păstrează numai SHA-ul lui.
    MUTAȚIE: `rezultat` păstrează textul și pe firmele reale -> pică."""
    refuz = "ValueError: partenerul RO123 n-are CUI valid"
    assert ad.rezultat(refuz=refuz, de_test=True) == {"refuz": refuz}
    real = ad.rezultat(refuz=refuz, de_test=False)
    assert set(real) == {"refuz_sha"} and "RO123" not in str(real) and len(real["refuz_sha"]) == 64


def test_compararea_numeste_fiecare_diferenta_si_datele_schimbate():
    """R8: orice amprentă diferită, lipsă sau nouă iese pe nume (schemă, tip, perioadă); date diferite ale firmei, separat. MUTAȚIE:
    `compara` ignoră perioadele care lipsesc într-o parte -> pică."""
    a = {"t1": {"date": "x", "declaratii": {"d300": {"01/2025": {"amprenta": "1"}, "02/2025": {"amprenta": "2"}}}}}
    b = {"t1": {"date": "y", "declaratii": {"d300": {"01/2025": {"amprenta": "1"}, "03/2025": {"amprenta": "3"}}}}}
    assert ad.compara(a, a) == []
    assert ad.compara(a, b) == [("t1", "(datele firmei)", "", "x", "y"),
                                ("t1", "d300", "02/2025", {"amprenta": "2"}, None),
                                ("t1", "d300", "03/2025", None, {"amprenta": "3"})]
