# -*- coding: utf-8 -*-
"""Valorile fiscale scrise in ECRANE se confrunta cu REGISTRUL, nu cu memoria mea.

DE CE EXISTA. Costin, 24.08.2026: «la fiecare schimbare de valoare fiscala, JS-ul
se cauta explicit. Nu decurge din nimic.» O observatie scrisa intr-un registru se
poate rata; asta nu. Cand o cota din `COTE` se schimba, testul de mai jos devine
ROSU si NUMESTE fisierul de ecran care ramane in urma — deci cautarea in JS nu mai
trebuie tinuta minte, se intampla singura.

CE FACE IMPOSIBIL: o cota din registru care se schimba fara ca ecranul care o are
scrisa literal sa fie atins.
CE NU FACE, declarat: (a) nu descopera singur valori fiscale noi in JS — tabelul
de mai jos e scris de om, iar `core/scan_valori_afisate.py` e cel care il
alimenteaza; (b) nu vede o valoare scrisa fara cifra (un prag numit doar in
cuvinte); (c) nu judeca daca eticheta e in locul potrivit — doar daca cifra din ea
e cea in vigoare.
"""
import datetime
import io
import os

import pytest

from core import common

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sursa(rel):
    return io.open(os.path.join(RAD, rel), encoding="utf-8").read()


def _procent(cheie, la_data):
    """Cota din registru, ca procent SCRIS CA IN ECRAN: 0.21 -> «21», 0.225 -> «22,5».
    Zerourile de coada se taie: ecranul scrie «21%», nu «21.00%»."""
    v, _t = common.cota(cheie, la_data)
    s = format(v * 100, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


# (fisier, ancora pe linie, cheia din COTE, cum arata valoarea in sursa)
# Alimentat din `core/scan_valori_afisate.py` — vezi R31 si campania din 24.08.2026.
TABEL = [
    ("static/js/ecrane/rip_ecran.js", "CAS (", "cas", "{p}%"),
    ("static/js/ecrane/rip_ecran.js", "CASS (", "cass", "{p}%"),
    ("static/js/ecrane/rip_ecran.js", "Impozit (", "impozit_venit", "{p}%"),
    ("static/js/ecrane/firme.js", "Total 11%", "tva_redusa", "{p}%"),
    ("static/js/ecrane/firme.js", "TVA 11%:", "tva_redusa", "{p}%"),
    ("static/js/ecrane/firme.js", "TVA 21%:", "tva_standard", "{p}%"),
]


def _linii_cu(sursa, ancora):
    return [ln for ln in sursa.split("\n") if ancora in ln]


@pytest.mark.parametrize("rel,ancora,cheie,forma", TABEL)
def test_valoarea_din_ecran_e_cea_din_registru(rel, ancora, cheie, forma):
    """Fiecare cota scrisa literal intr-un ecran = cota in vigoare AZI, din `COTE`."""
    azi = datetime.date.today()
    asteptat = forma.format(p=_procent(cheie, azi))
    linii = _linii_cu(_sursa(rel), ancora)
    assert linii, "ancora %r nu mai exista in %s — tabelul a ramas in urma codului" % (ancora, rel)
    for ln in linii:
        assert asteptat in ln, (
            "%s: linia cu %r scrie o cota care NU e cea din registru.\n"
            "  registrul (`%s`, azi): %s\n  linia: %s"
            % (rel, ancora, cheie, asteptat, ln.strip()[:160]))


def test_tabelul_nu_e_gol_si_ancorele_traiesc():
    """ANTI-VACUU. Un tabel din care ancorele au disparut ar trece pe vid."""
    assert len(TABEL) >= 6
    for rel, ancora, _c, _f in TABEL:
        assert _linii_cu(_sursa(rel), ancora), "ancora moarta: %s / %r" % (rel, ancora)


def test_confruntarea_chiar_ar_pica_pe_o_valoare_gresita():
    """CALIBRARE NEGATIVA. Daca registrul ar spune altceva decat ecranul, testul de
    mai sus trebuie sa cada — altfel confrunta doua lucruri care coincid din intamplare."""
    sursa = _sursa("static/js/ecrane/rip_ecran.js")
    linii = _linii_cu(sursa, "CAS (")
    assert linii
    assert not any("99%" in ln for ln in linii), "calibrarea presupune ca 99% NU e in sursa"
    # forma reala trece, o valoare inventata nu
    assert any("25%" in ln for ln in linii)


def test_cotele_confruntate_exista_chiar_in_registru():
    """Un test care cere o cheie inexistenta ar pica din alt motiv decat cel scris."""
    azi = datetime.date.today()
    for _rel, _a, cheie, _f in TABEL:
        v, temei = common.cota(cheie, azi)
        assert v is not None and temei, "cheia %r n-are valoare/temei la %s" % (cheie, azi)
