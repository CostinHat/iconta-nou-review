# -*- coding: utf-8 -*-
"""GARD (interdicția 4): aritmetica fiscală din ecran nu diverge de cea din server.

CE FACE IMPOSIBIL: ca ecranul să arate un TVA pe care factura salvată nu-l are. Măsurat 23.08.2026,
pe date obișnuite: o factură de **50 de rânduri × 3 × 19,99 la 21%** → serverul salvează **629,50**,
ecranul arăta **629,69**. Cauza: serverul rotunjește **pe linie** (`Decimal.quantize`, ROUND_HALF_UP),
iar ecranul aduna în `float` și rotunjea o singură dată, la afișare.

CE NU FACE, declarat — și e partea care contează: **nu scoate regula fiscală din stratul de
prezentare.** Calculul rămâne duplicat în JS, deci rămâne netestat pe cale reală, negardat și
neversionat pe dată — chiar interdicția 4. Gardul oprește **cifra greșită**, nu **duplicarea**;
pentru a doua e nevoie de o cale prin server, iar aia e restanță.

DE CE E UN TEST PYTHON PENTRU COD JS: reproduce **cele două aritmetici** pe aceleași date și cere să
dea la fel, plus verifică pe SURSA JS că rotunjirea pe linie e chiar acolo. Un test care ar rula JS
ar cere un motor de browser în poartă; unul care doar citește sursa n-ar prinde divergența numerică.
Amândouă, împreună, o prind.
"""
import io
import os
import re
from decimal import ROUND_HALF_UP, Decimal

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_JS = os.path.join(_RAD, "static", "js", "ecrane")


def _server(linii):
    """Ce face `creeaza_factura`: quantize pe LINIE, apoi sumă."""
    tva = Decimal("0.00")
    for cant, pret, cota in linii:
        baza = Decimal(str(cant)) * Decimal(str(pret))
        tva += (baza * Decimal(str(cota)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return tva


def _ecran(linii):
    """Ce face `recalc()` DUPĂ reparație: rotunjire pe linie, în float, apoi sumă."""
    tva = 0.0
    for cant, pret, cota in linii:
        tva += round((cant * pret) * (cota / 100.0) * 100) / 100
    return Decimal(str(round(tva, 2)))


def _ecran_vechi(linii):
    """Forma de DINAINTE: sumă nerotunjită. Ținută ca să se poată proba divergența."""
    tva = 0.0
    for cant, pret, cota in linii:
        tva += (cant * pret) * (cota / 100.0)
    return Decimal(str(round(tva, 2)))


CAZURI = [
    ("o linie obișnuită", [(1, 333.33, 21)]),
    ("două cote diferite", [(1, 100.00, 21), (1, 100.00, 11)]),
    ("douăzeci de rânduri mici", [(1, 0.07, 21)] * 20),
    ("factură de 50 de rânduri", [(3, 19.99, 21)] * 50),
    ("sută de rânduri", [(1, 12.34, 11)] * 100),
    ("cote amestecate", [(2, 9.99, 21), (1, 5.55, 11), (7, 1.11, 21), (1, 0.03, 11)] * 12),
]


@pytest.mark.parametrize("nume,linii", CAZURI)
def test_ecranul_da_ACEEASI_cifra_ca_serverul(nume, linii):
    assert _ecran(linii) == _server(linii), (
        "%s: ecranul %s, serverul %s — contabilul ar vedea un total pe care factura nu-l are"
        % (nume, _ecran(linii), _server(linii)))


def test_ANTIVACUU_forma_veche_CHIAR_diverge():
    """Fără asta, testul de mai sus ar putea trece fiindcă niciun caz nu discriminează. Se probează
    că datele alese chiar prind defectul reparat."""
    divergente = [(n, _ecran_vechi(l) - _server(l)) for n, l in CAZURI if _ecran_vechi(l) != _server(l)]
    assert len(divergente) >= 2, (
        "niciun caz nu mai discriminează — cazurile de probă s-au tocit: %r" % divergente)
    assert any(abs(d) >= Decimal("0.09") for _n, d in divergente), \
        "divergențele rămase sunt sub un ban; alege cazuri care chiar despart cele două aritmetici"


@pytest.mark.parametrize("fisier,tipar", [
    ("emitere_ecran.js", r"tva \+= Math\.round\("),
    ("facturi_ecran.js", r"const tva = Math\.round\("),
])
def test_rotunjirea_pe_linie_e_CHIAR_in_sursa_JS(fisier, tipar):
    """Aritmetica de mai sus e o reproducere; asta verifică originalul. Dacă cineva scoate
    rotunjirea din JS, reproducerea ar rămâne verde și ar minți."""
    src = io.open(os.path.join(_JS, fisier), encoding="utf-8").read()
    assert re.search(tipar, src), (
        "%s nu mai rotunjește TVA-ul pe linie — ecranul poate diverge iar de server" % fisier)


def test_nicio_ALTA_aritmetica_de_cota_fara_rotunjire_in_ecrane():
    """Clichet: o a treia formulă de TVA apărută în prezentare, fără rotunjire pe linie, pică."""
    rele = []
    for f in sorted(os.listdir(_JS)):
        if not f.endswith(".js"):
            continue
        src = io.open(os.path.join(_JS, f), encoding="utf-8").read()
        for i, linie in enumerate(src.split("\n"), 1):
            if not re.search(r"\bcota\w*\s*/\s*100|\*\s*cota\w*\s*/\s*100", linie):
                continue
            if "Math.round" in linie or linie.strip().startswith("//"):
                continue
            rele.append("  %s:%d %s" % (f, i, linie.strip()[:90]))
    assert not rele, ("aritmetică de cotă fără rotunjire pe linie, în stratul de prezentare:\n"
                      + "\n".join(rele) + "\n\nVezi interdicția 4: regula fiscală n-are ce căuta în "
                      "ecran; până se scoate, măcar să nu dea altă cifră decât serverul.")
