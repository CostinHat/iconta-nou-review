# -*- coding: utf-8 -*-
"""GARD (07.09.2026) — poarta scurta din PLAN_LUCRU regula 4 nu poate deveni o formalitate.

CE PAZESTE, si de ce fiecare proba e aici:

  CELE DOUA CAZURI DE ACCEPTANTA, cerute de Costin cand a comandat instrumentul: o atingere doar in
  `core/plati.py` NU trebuie sa atinga testele D406; una in `core/d112.py` trebuie sa atinga testele
  D112. Le-am probat o data, la constructie. Pinate aici, proba se REFACE la fiecare poarta — altfel
  ar fi ramas o amintire dintr-o dupa-amiaza.

  REFUZUL PE ARGUMENTE. `perimetru.py` accepta cai in argv, fiindca asa se PROBEAZA derivarea.
  Lansatorul nu are voie: ar insemna ca cel care tocmai a scris modificarea alege ce se ruleaza —
  exact ce interzice regula 5 („o exceptie luata o data face regula o formalitate").

  REFUZUL PE NESIGURANTA. Un `.md` atins, sau `main.py`, si derivarea nu mai poate inchide
  perimetrul. Atunci raspunsul e poarta COMPLETA, nu un perimetru mai mic. *Un perimetru ghicit e
  mai rau decat o poarta lunga.*

  ANTI-VACUU. Daca `perimetru()` ar intoarce liste goale din orice motiv, toate probele de mai sus
  ar trece degeaba. De-aia se cere si ca perimetrul unui modul cunoscut sa NU fie gol.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import perimetru as P            # noqa: E402
import poarta_scurta as PS       # noqa: E402


# ── cele doua cazuri de acceptanta ─────────────────────────────────────────
def test_o_atingere_in_plati_nu_atinge_testele_d406():
    """Cazul R43, verbatim din comanda. `plati.py` n-are nicio legatura cu SAF-T."""
    teste, incerte = P.perimetru(["core/plati.py"])
    assert incerte == []
    assert teste, "perimetru gol — anti-vacuu"
    d406 = [t for t in teste if t.lower().count("d406")]
    assert d406 == [], "perimetrul lui plati.py a ajuns la D406: %s" % d406
    assert set(teste) >= {"core/test_plata_izolare.py"}


def test_o_atingere_in_d112_atinge_testele_d112():
    """Celalalt caz din comanda. Aici legatura EXISTA, deci trebuie sa se vada."""
    teste, incerte = P.perimetru(["core/d112.py"])
    assert incerte == []
    assert set(teste) >= {"core/test_d112.py"}, "perimetrul lui d112.py nu contine testele lui"


def test_cele_doua_cazuri_chiar_difera():
    """CALIBRARE: daca derivarea ar intoarce acelasi lucru pentru orice intrare, cele doua probe de
    mai sus ar trece si cu un instrument mort. Se cere ca raspunsurile sa fie DIFERITE."""
    a, _ = P.perimetru(["core/plati.py"])
    b, _ = P.perimetru(["core/d112.py"])
    assert set(a) != set(b)
    assert len(b) > len(a)


# ── refuzurile ─────────────────────────────────────────────────────────────
def test_lansatorul_refuza_fisiere_pe_linia_de_comanda(capsys):
    """Perimetrul se DERIVA, nu se alege. Un lansator care accepta cai e un lansator care poate fi
    convins sa ruleze mai putin."""
    cod = PS.main(["core/plati.py"])
    assert cod == 3
    # structura iesirii, nu un sir: prima linie e refuzul, si numeste fisierul dat
    prima = capsys.readouterr().out.splitlines()[0]
    assert prima.startswith("REFUZ") and prima.rstrip().endswith("comanda.")


@pytest.mark.parametrize("atins,de_ce", [
    ("CONFORMITATE.md", "registru"),
    ("main.py", "rutele sunt citite de scanere care nu importa main"),
    ("static/js/ecrane/facturi_ecran.js", "fisier ne-Python"),
])
def test_derivarea_refuza_ce_nu_poate_vedea(atins, de_ce):
    """Cele trei clase pe care graful de import NU le vede. Fiecare, atinsa alaturi de cod, cere
    poarta completa."""
    _teste, incerte = P.perimetru([atins, "core/plati.py"])
    assert incerte, "derivarea a inchis perimetrul desi s-a atins %s" % atins


def test_lansatorul_cere_poarta_completa_cand_derivarea_nu_e_sigura(monkeypatch, capsys):
    """Nu doar derivarea refuza — si LANSATORUL, cu cod de iesire 2."""
    monkeypatch.setattr(PS.P, "atinse_din_git", lambda: ["CONFORMITATE.md", "core/plati.py"])
    monkeypatch.setattr(PS.P, "netracked", lambda: [])
    cod = PS.main([])
    assert cod == 2
    # se cere ca MOTIVELE sa fie tiparite, numarate ca randuri, nu cautate ca sir
    motive = [x for x in capsys.readouterr().out.splitlines() if x.startswith("   - ")]
    assert len(motive) == 1


def test_commiturile_reale_de_azi_ar_fi_cerut_poarta_completa():
    """MASURAT, nu presupus: pe amandoua reparatiile de 06.09 perimetrul NU se poate inchide,
    fiindca amandoua au atins registre si `main.py`. Poarta scurta e pentru bucla DIN TURA, nu
    pentru commit — iar cifra asta tine afirmatia adevarata."""
    r43 = ["CONFORMITATE.md", "DECIZII.md", "core/plati.py", "main.py",
           "static/js/ecrane/facturi_ecran.js"]
    r94 = ["CONFORMITATE.md", "core/control_fiscal_api.py", "core/declaratii_api.py", "main.py"]
    for nume, lista in (("R43", r43), ("R94", r94)):
        _t, incerte = P.perimetru(lista)
        assert incerte, "%s: derivarea a inchis perimetrul, desi a atins registre si main.py" % nume


def test_perimetrul_nu_e_toata_suita():
    """Un perimetru care ia aproape tot nu deriva nimic, imbraca «ruleaza tot» in alt nume
    (PLAN_LUCRU, regula 5, prima forma esuata). Se cere sa ramana sub jumatate din fisierele de
    test, pe cazul cel mai larg dintre cele doua de acceptanta."""
    toate = [f for f in os.listdir(os.path.join(_RAD, "core"))
             if f.startswith("test_") and f.endswith(".py")]
    teste, _ = P.perimetru(["core/d112.py"])
    assert len(teste) < len(toate) / 2, "%d din %d fisiere — prea larg ca sa fie o derivare" % (
        len(teste), len(toate))
