# -*- coding: utf-8 -*-
"""Un AN scris literal intr-o cerere catre server ingheata ecranul in trecut.

DE CE EXISTA. Costin, 24.08.2026: «JS-ul a fost scris cand 3750 era valoarea
curenta, si nimeni nu s-a mai uitat de atunci. Intreaba-te ce alte valori au fost
corecte in ianuarie si nu mai sunt.» Masurat: **valorile fiscale din textul
ecranelor sunt toate in vigoare** — nicio cota depasita (19%, 9%, 5%) nu apare.
Ce s-a gasit in schimb e o forma vecina si mai tacuta: `rip_ecran.js` cere
`/rip/d212/2025` cu anul SCRIS IN URL. Ecranul nu afiseaza o cifra gresita — o
afiseaza pe cea de anul trecut, corect etichetata, si nu poate ajunge la anul
curent niciodata.

CE FACE IMPOSIBIL: aparitia unui AL DOILEA an inghetat intr-o cerere.
CE NU FACE, declarat: nu repara cazul existent (R31 tine diferenta) si nu vede
anul construit prin variabila (`${2025}` sau o constanta numita) — pentru asta ar
trebui evaluat JS-ul, nu citit.
"""
import io
import os
import re

import pytest

BAZA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "static", "js")

# un an in interiorul unei cereri catre server
CERERE = re.compile(r"""(?:api\.(?:get|post|put|delete)|fetch)\s*\(\s*[`'"][^`'"]*?\b(20\d\d)\b""")

# CLICHET: cate sunt azi. Nu poate creste. Coboara cand R31 se rezolva.
CLICHET = 1


def _fisiere():
    for rad, _, nume in os.walk(BAZA):
        for f in sorted(nume):
            if f.endswith(".js"):
                yield os.path.join(rad, f)


def gaseste():
    """(fisier, linie, an) pentru fiecare an scris literal intr-o cerere."""
    out = []
    for f in _fisiere():
        src = io.open(f, encoding="utf-8").read()
        for nr, linie in enumerate(src.split("\n"), 1):
            for an in CERERE.findall(linie):
                out.append((os.path.relpath(f, os.path.dirname(BAZA)), nr, an))
    return out


def test_domeniul_nu_e_gol():
    """ANTI-VACUU. Un gard care nu vede niciun fisier raporteaza verde despre nimic."""
    fisiere = list(_fisiere())
    assert len(fisiere) >= 30, "vad doar %d fisiere .js — domeniul e gresit" % len(fisiere)
    assert any("rip_ecran" in f for f in fisiere), "nu vad rip_ecran.js"


def test_tiparul_chiar_prinde_un_an_intr_o_cerere():
    """CALIBRARE POZITIVA, pe forma reala din cod."""
    assert CERERE.findall('const d = await api.get(`/tenants/${t.id}/rip/d212/2025`);')
    assert CERERE.findall("fetch('/raport/2024/luna')")


def test_tiparul_nu_prinde_un_an_din_variabila_sau_din_text():
    """CALIBRARE NEGATIVA. Trei feluri de a NU fi un an inghetat intr-o cerere."""
    assert not CERERE.findall("api.get(`/tenants/${t.id}/rip/d212/${an}`)")       # an din stare
    assert not CERERE.findall('zona.innerHTML = "venituri 2025";')                # doar text
    assert not CERERE.findall("const prag = 2025;")                              # nu e cerere


def test_niciun_an_nou_inghetat_intr_o_cerere():
    """CLICHETUL. Cazul cunoscut ramane numarat pana la R31; al doilea pica."""
    g = gaseste()
    assert len(g) <= CLICHET, (
        "AN INGHETAT INTR-O CERERE — ecranul nu poate ajunge la anul curent:\n" +
        "\n".join("  %s:%d cere anul %s" % x for x in g) +
        "\nDaca anul e al perioadei alese pe ecran, trimite variabila, nu literalul.")


def test_clichetul_nu_ramane_peste_realitate():
    """ANTI-STALE. Daca R31 se rezolva si clichetul ramane la 1, gardul devine mut."""
    g = gaseste()
    if len(g) < CLICHET:
        pytest.fail("sunt doar %d — coboara CLICHET la %d si inchide R31" % (len(g), len(g)))


def test_cazul_cunoscut_e_chiar_cel_din_registru():
    """Clichetul de 1 nu e un numar oarecare: e `rip_ecran.js`. Daca ala se repara
    si apare altul in loc, cifra ar ramane 1 si gardul ar tacea."""
    g = gaseste()
    assert len(g) == 0 or any("rip_ecran" in f for f, _, _ in g), (
        "clichetul de 1 era pentru rip_ecran.js; acum e altundeva: %s" % (g,))
