# -*- coding: utf-8 -*-
"""GARD neconformitate T4/G-bc1 + G-bc2 (CATALOG_INVALIDITATE.md): "avertizeaza-dar-emite-invalid".

G-bc1 (R233.5): un op1 C/V catre partener TVA RO (tip_partener=1) FARA categoria art.331 se emitea
FARA sectiunea op11 -> DUK il respingea; avertismentul NU bloca. FIX: op1-ul se EXCLUDE inainte de
rezumat/reconciliere (consistent cu excluderea N-fara-subcod), cu motiv exact + citare DUK R233.5;
nu mai expediem XML pe care DUK il respinge.

G-bc2 (R233.4): un op1 N (tip_partener=2) cu cuiP = CUI de FIRMA (nu CNP de persoana fizica)
contrazice op11-ul de persoana fizica. FIX: detectam CUI-vs-CNP (core.identitate) inainte de a
emite N-op11 si excludem cu motiv exact.

Pe HEAD (8b74ccb): op1 C/V/N raman in declaratie (emise fara/cu op11 gresit) -> acest test PICA.
Dupa fix: operatiunile sunt EXCLUSE cu avertismente exacte -> TRECE.
"""
from core.common import Perioada
from core import d394

_PROF = {"cui": "RO14399840", "caen": "4690", "nume": "TEST SRL",
         "adresa": "str X", "telefon": "0700", "tip_decont": "L"}
_PER = Perioada(2026, luna=8)


def _calc(facturi, manual=None):
    return d394.calcul_d394(_PROF, _PER, {"facturi": facturi, "serii": {}}, manual)


def test_manual_C_fara_categorie_exclus_nu_emis_fara_op11():
    manual = {"operatiuni": [{"tip": "C", "tip_partener": 1, "cota": 19,
                              "cuiP": "14399840", "denP": "FURN FARA CAT SRL",
                              "nrFact": 1, "baza": 1000, "tva": 190}]}  # FARA categorie_331
    res = _calc([], manual)
    assert not any(k[0] == "C" for k in res.op1), \
        "C fara op11 inca emis in op1 -> XML DUK-invalid R233.5 (G-bc1)"
    assert any("R233.5" in a and "FURN FARA CAT SRL" in a for a in res.avertismente)
    xml = d394.build_xml(res)
    assert 'tip="C"' not in xml, "XML contine op1 tip C fara op11 -> DUK il respinge"


def test_manual_V_fara_categorie_exclus():
    manual = {"operatiuni": [{"tip": "V", "tip_partener": 1, "cota": 0,
                              "cuiP": "14399840", "denP": "CLIENT V SRL",
                              "nrFact": 1, "baza": 2000, "tva": 0}]}
    res = _calc([], manual)
    assert not any(k[0] == "V" for k in res.op1), \
        "V fara op11 inca emis -> DUK R233.5 (G-bc1)"
    assert any("R233.5" in a and "CLIENT V SRL" in a for a in res.avertismente)


def test_N_cu_cui_de_firma_exclus_R233_4():
    manual = {"operatiuni": [{"tip": "N", "tip_partener": 2, "cota": 0,
                              "cuiP": "14399840", "denP": "PJ NEPLATITOR SRL",
                              "nrFact": 1, "baza": 800, "tva": 0,
                              "categorie_331": "deseuri"}]}
    res = _calc([], manual)
    assert not any(k[0] == "N" for k in res.op1), \
        "N cu CUI de firma inca emis -> op11 persoana fizica pe partener PJ -> DUK R233.4 (G-bc2)"
    assert any("R233.4" in a and "PJ NEPLATITOR SRL" in a for a in res.avertismente)


def test_manual_C_cu_categorie_ramane_valid():
    # regresie: C art.331 CU categorie ramane in declaratie cu op11 corect (nu-l excludem)
    manual = {"operatiuni": [{"tip": "C", "tip_partener": 1, "cota": 19,
                              "cuiP": "14399840", "denP": "FURN OK SRL",
                              "nrFact": 1, "baza": 1000, "tva": 190,
                              "categorie_331": "deseuri"}]}
    res = _calc([], manual)
    k = ("C", 1, 19, "14399840", "FURN OK SRL")
    assert k in res.op11 and res.op11[k]["codPR"] == "22"
