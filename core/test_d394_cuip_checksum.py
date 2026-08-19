# -*- coding: utf-8 -*-
"""GARD neconformitate T1/G-c1 (CATALOG_INVALIDITATE.md): checksum-ul CUI/CIF al partenerului NU
era validat de app -> un cod cu cifra de control gresita era emis TACIT, il prindea doar DUK
(R218.2 pt CUI RO / R218.3 pt cod partener neinregistrat) cu mesaj brut la depunere. Idem CUI-ul
PROPRIEI firme (prezent-dar-invalid).

FIX (core/d394.py): validare pre-DUK cu sursa canonica core.identitate (valideaza_cui/valideaza_cif),
avertisment care NUMESTE partenerul + motivul exact + citarea regulii DUK; own cui in valideaza().

# cui-invalid-ok: CUI deliberat invalid pentru testul negativ de checksum (R6/R218)
143000000 = CUI valid; 143000009 = checksum gresit (dovada in docstring core/identitate.py).
Pe HEAD (8b74ccb): niciun avertisment de checksum -> acest test PICA. Dupa fix: TRECE.
"""
from core.common import Perioada
from core import d394

_PROF = {"cui": "RO14399840", "caen": "4690", "nume": "TEST SRL",
         "adresa": "str X", "telefon": "0700", "tip_decont": "L"}
_PER = Perioada(2026, luna=8)


def _calc(facturi, manual=None):
    return d394.calcul_d394(_PROF, _PER, {"facturi": facturi, "serii": {}}, manual)


def test_partener_cuiP_checksum_avertisment_R218_2():
    # cui-invalid-ok: CUI deliberat invalid pentru testul negativ de checksum (R6/R218)
    facturi = [{"cui": "143000009", "nume": "CLIENT RAU SRL", "directie": "emisa",
                "taxare_inversa": False, "cota": 21, "baza": 1000, "tva": 210,
                "platitor_tva": True}]
    res = _calc(facturi)
    assert any("R218.2" in a and "CLIENT RAU SRL" in a for a in res.avertismente), \
        "cuiP RO cu checksum gresit emis TACIT - fara avertisment pre-DUK (G-c1/R218.2)"


def test_partener_tip2_cif_invalid_avertisment_R218_3():
    manual = {"operatiuni": [{"tip": "LS", "tip_partener": 2, "cota": 0,
                              # cui-invalid-ok: CUI deliberat invalid pentru testul negativ de checksum (R6/R218)
                              "cuiP": "143000009", "denP": "NEINREG SRL", "nrFact": 1,
                              "baza": 500, "tva": 0}]}
    res = _calc([], manual)
    assert any("R218.3" in a and "NEINREG SRL" in a for a in res.avertismente), \
        "cod fiscal tip_partener=2 invalid emis TACIT (G-c1/R218.3)"


def test_own_cui_invalid_valideaza_R6():
    # cui-invalid-ok: CUI deliberat invalid pentru testul negativ de checksum (R6/R218)
    prof = dict(_PROF, cui="143000009")
    res = d394.Rezultat(an=2026, luna=8, prof=prof)
    erori = d394.valideaza(res)
    assert any("R6" in e for e in erori), \
        "CUI propriu prezent-dar-invalid nedetectat pre-DUK (G-c1 own cui)"


def test_cui_valid_fara_avertisment():
    # regresie: un CUI corect nu produce fals-pozitiv
    facturi = [{"cui": "14399840", "nume": "CLIENT BUN SRL", "directie": "emisa",
                "taxare_inversa": False, "cota": 21, "baza": 1000, "tva": 210,
                "platitor_tva": True}]
    res = _calc(facturi)
    assert not any("R218" in a for a in res.avertismente)
