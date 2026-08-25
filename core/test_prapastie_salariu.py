# -*- coding: utf-8 -*-
"""GARD [R49, varianta (c)]: prăpastia salariului minim se spune CU CIFRE, și cifrele sunt ale
salariatului, nu ale unui salariat implicit.

Decizia lui Costin: *„Contabilul care mărește un salariu cu 100 de lei are nevoie să vadă CÂT
pierde salariatul, nu că pierde."* R28 scosese varianta veche fiindcă pasa **doi** din
optsprezece parametri — restul luau valorile implicite, deci cifra nu putea coincide cu
fluturașul. Gardul ăsta ține exact partea aia: **elementele contează**.
"""
from datetime import date

import pytest

from core import common as _c
from core import prapastie_salariu as p

_LA = date(2026, 8, 1)
_PRAG = float(_c.cota("salariu_minim", _LA)[0])


def test_sub_prag_nu_se_afirma_nimic():
    r = p.prapastie(_PRAG - 100, {}, la_data=_LA)
    assert r["aplicabil"] is False
    assert r["cod"] == p.COD_SUB_PRAG, "un rezultat neaplicabil spune de ce, cu un COD"


def test_un_leu_peste_prag_arata_CAT_se_pierde():
    r = p.prapastie(_PRAG + 1, {}, la_data=_LA)
    assert r["aplicabil"] is True
    assert r["pierdere"] > 0, "netul trebuie să fie MAI MIC decât la prag"
    assert r["net_acum"] < r["net_la_prag"]
    assert r["brut_egal"] and r["brut_egal"] > _PRAG, (
        "trebuie spus și de la ce brut netul redevine cel de la minim")


def test_departe_peste_prag_nu_mai_e_o_prapastie():
    """Calibrare în cealaltă direcție: la un brut mult peste prag netul e MAI MARE, deci nu se
    afișează nimic. Fără proba asta, o funcție care spune «pierzi» mereu ar trece testul de sus."""
    r = p.prapastie(_PRAG * 1.5, {}, la_data=_LA)
    assert r["aplicabil"] is False
    assert r["cod"] == p.COD_NETUL_NU_SCADE
    assert r["pierdere"] < 0


def test_ELEMENTELE_schimba_cifra():
    """Inima gardului, și chiar motivul pentru care R28 a scos varianta veche: cifra trebuie să
    depindă de elementele salariatului. Două persoane în întreținere schimbă deducerea, deci
    schimbă netul — dacă cifra e aceeași, funcția calculează pe un salariat implicit."""
    brut = _PRAG + 1
    fara = p.prapastie(brut, {}, la_data=_LA)
    cu = p.prapastie(brut, {"persoane_intretinere": 2}, la_data=_LA)
    assert fara["net_acum"] != cu["net_acum"], (
        "netul nu se schimbă cu persoanele în întreținere — se calculează pe valori implicite, "
        "exact defectul care a invalidat estimarea la R28")


def test_pragul_vine_din_REGISTRU_cu_temei():
    r = p.prapastie(_PRAG + 1, {}, la_data=_LA)
    assert r["prag"] == _PRAG
    assert r["prag_temei"], "pragul trebuie să poarte temeiul din registru"
    assert r["plafon_temei"], "și plafonul, fiindcă el mărginește căutarea"
    assert r["temei"], "afirmația despre facilitate trebuie să poarte temeiul ei"


def test_fara_brut_nu_se_afirma():
    r = p.prapastie(0, {}, la_data=_LA)
    assert r["aplicabil"] is False and r["cod"] == p.COD_FARA_BRUT


@pytest.mark.parametrize("cheie", ["prag", "net_acum", "net_la_prag", "pierdere"])
def test_cifrele_sunt_numere_rotunjite_la_ban(cheie):
    r = p.prapastie(_PRAG + 1, {}, la_data=_LA)
    v = r[cheie]
    assert isinstance(v, float)
    assert round(v, 2) == v, "cifra afișată unui om se rotunjește la ban, nu la 12 zecimale"
