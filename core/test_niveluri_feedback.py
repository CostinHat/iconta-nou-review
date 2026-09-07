# -*- coding: utf-8 -*-
"""GARD P0 (07.09.2026) — cele patru niveluri de feedback nu pot deveni o scurtătură nesigură.

MODELUL: *modificare → teste direct afectate → regresie subsistem → integrare relevantă → regresie
completă*. Primele trei sunt mulțimi DERIVATE din graful de import și din harta rutelor; a patra e
suita întreagă și nu se derivă.

CE PAZEȘTE, și fiecare probă apără o cale de a strica modelul:

  MONOTONIE   N1 ⊆ N2 ∪ N1 ⊆ N3. Un nivel mai adânc nu are voie să PIARDĂ teste pe care unul mai
              superficial le găsise — altfel „urcă o treaptă" ar putea ascunde un test.
  REFUZUL SE MOȘTENEȘTE  dacă derivarea nu poate închide perimetrul, **toate** nivelurile refuză.
              Un nivel nu poate fi mai îndrăzneț decât derivarea care îl hrănește.
  N4 NU SE DERIVĂ  `nivel("complet")` întoarce listă goală **și motiv**, iar lansatorul refuză să-l
              ruleze. Dacă N4 ar întoarce o listă, cineva ar rula „regresia completă" pe 200 de
              fișiere și ar crede că a rulat 4.161 de teste.
  FRONTIERA CHIAR TAIE  N2 se oprește la rădăcina de compunere. Dacă frontiera ar dispărea, N2 ar
              deveni N3 — se cere ca pe cazul măsurat cele două să DIFERE.
  ANTI-VACUU  pe un modul cunoscut, fiecare nivel întoarce ceva; iar N1 nu e egal cu toată suita.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import perimetru as P  # noqa: E402

#: Cazul de referință: modul real, cu dependenți mulți și cu rute. Măsurat 07.09: 14 / 25 / 47.
CAZ = ["core/control_fiscal_api.py"]


def _n(nume, atinse=None):
    teste, incerte = P.nivel(nume, atinse or CAZ)
    assert not incerte, "derivarea a refuzat pe cazul de referință: %s" % incerte
    return set(teste)


def test_cele_patru_niveluri_sunt_declarate():
    assert P.NIVELURI == ("direct", "subsistem", "integrare", "complet")


def test_fiecare_nivel_intoarce_ceva():
    """ANTI-VACUU: fără asta, toate probele de mai jos ar trece pe mulțimi goale."""
    for nume in ("direct", "subsistem", "integrare"):
        assert _n(nume), "nivelul %s e gol pe cazul de referință" % nume


def test_nivelurile_cresc_si_nu_pierd_nimic():
    """MONOTONIE. `>=` pe mulțimi, nu pe numere: două mulțimi de aceeași mărime pot fi diferite."""
    d, s, i = _n("direct"), _n("subsistem"), _n("integrare")
    assert s >= d, "N2 a pierdut teste pe care N1 le găsise: %s" % sorted(d - s)
    assert i >= s, "N3 a pierdut teste pe care N2 le găsise: %s" % sorted(s - i)


def test_frontiera_chiar_taie():
    """N2 se oprește la rădăcina de compunere; N3 o trece. Dacă ar fi egale, frontiera n-ar face
    nimic, iar modelul ar avea trei niveluri cu numele de patru."""
    assert _n("subsistem") != _n("integrare")
    assert P.FRONTIERA == ("main",)


def test_n1_nu_e_toata_suita():
    """Treapta de secunde trebuie să fie mult mai mică decât cea de minute — altfel n-are rost."""
    toate = [f for f in os.listdir(os.path.join(_RAD, "core"))
             if f.startswith("test_") and f.endswith(".py")]
    assert len(_n("direct")) < len(toate) / 4


@pytest.mark.parametrize("nume", ["direct", "subsistem", "integrare"])
def test_refuzul_se_mosteneste_la_toate_nivelurile(nume):
    """Un `.md` atins, sau `main.py`: derivarea nu poate închide perimetrul. Atunci **fiecare**
    nivel refuză — alternativa la nesiguranță e *tot*, nu *mai puțin*."""
    for atins in ("CONFORMITATE.md", "main.py", "static/js/ecrane/login.js"):
        _teste, incerte = P.nivel(nume, [atins, "core/plati.py"])
        assert incerte, "nivelul %s a închis perimetrul deși s-a atins %s" % (nume, atins)


def test_n4_nu_se_deriva():
    """N4 e suita întreagă. Dacă ar întoarce o listă, cineva ar rula „regresia completă" pe 200 de
    fișiere și ar crede că a rulat 4.161 de teste."""
    teste, incerte = P.nivel("complet", CAZ)
    assert teste == []
    # se cere STRUCTURA raspunsului — exact un motiv, si nu unul gol —, nu un subsir din el:
    # `"suita intreaga" in motiv` ar trece si daca motivul ar spune altceva pe langa.
    assert len(incerte) == 1 and incerte[0].strip()


def test_lansatorul_refuza_nivelul_complet_si_pe_cel_necunoscut(capsys):
    import poarta_scurta as PS
    assert PS.main(["--nivel=complet"]) == 3
    iesire = capsys.readouterr().out
    assert iesire.splitlines()[0].startswith("N4 (complet) NU se ruleaza")
    assert PS.main(["--nivel=nascocit"]) == 3


def test_perimetrul_vechi_e_neatins():
    """`perimetru()` e gardată separat (`core/test_poarta_scurta.py`) și e folosită de lansator.
    Nivelurile s-au adăugat LÂNGĂ ea, nu în locul ei: N3 pornește din ea, iar rezultatul ei pe
    cazul de acceptanță al lui Costin rămâne cel de ieri."""
    teste, incerte = P.perimetru(["core/plati.py"])
    assert incerte == []
    assert set(teste) >= {"core/test_plata_izolare.py"}
    assert [t for t in teste if t.lower().count("d406")] == []
