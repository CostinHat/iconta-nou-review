# -*- coding: utf-8 -*-
"""GARDĂ: constatarea din semaforul de portofoliu e o afirmație VALIDĂ, pe toate cele trei stări.

CALEA CARE CĂDEA ÎN TĂCERE (21.08.2026, a treia instanță a clasei într-o zi). Am rutat
`_flag_constatare` prin `afirmatii.afirmatie()` și am lăsat `an=None, luna=None` „ca să nu ating cei
șapte apelanți". Două din trei ramuri cădeau imediat: `fapt` cere `an`, `necunoastere` cere
`domeniu_de`. Niciun test nu construia o constatare, deci suita ar fi rămas verde peste o cădere pe
ecranul de portofoliu — cel care se deschide primul.

De data asta am probat funcția pe loc, nu prin suită. Testul de aici e ca proba să rămână.

CE PĂZEȘTE: că fiecare stare produce felul potrivit ȘI toate câmpurile cerute de el. Nu că textul e
bun — aia e altă gardă.
"""
import pytest

import main
from core.afirmatii import FELURI

STARI = [("gri", "necunoastere"), ("rosu", "contradictie"), ("verde", "fapt")]


@pytest.mark.parametrize("stare,fel", STARI)
def test_fiecare_stare_produce_o_afirmatie_completa(stare, fel):
    c = main._flag_constatare(stare, "Balanță dezechilibrată", "debit 100 ≠ credit 90",
                              "OMFP 1802 — dubla partidă", 2026, 7)
    assert c["fel"] == fel, "starea %r a produs felul %r" % (stare, c["fel"])
    for camp in FELURI[fel]:
        assert camp in c, "constatarea %r nu e o afirmație validă: lipsește %s" % (stare, camp)
    assert c["stare"] == stare and c["mesaj"] == c["motiv"], "textul s-a despărțit în două surse"


def test_perioada_e_obligatorie_in_semnatura():
    """Ce a produs defectul: un default comod. Semnătura trebuie s-o CEARĂ, nu s-o spere."""
    import inspect
    sem = inspect.signature(main._flag_constatare)
    for p in ("an", "luna"):
        assert sem.parameters[p].default is inspect.Parameter.empty, (
            "`%s` a redevenit opțional în _flag_constatare — asta a ascuns căderea o dată" % p)


def test_gri_poarta_perioada_pe_care_nu_o_poate_verifica():
    """O necunoaștere fără capete se citește peste șase luni ca fapt permanent."""
    c = main._flag_constatare("gri", "Stocuri", "nu pot verifica", "temei", 2026, 7)
    assert c["domeniu_de"] == "2026-07"


def test_esecul_unui_verificator_e_tot_o_afirmatie():
    """`_constatare_esuata` e calea prin care un verificator picat ajunge pe ecran. Dacă ea cade,
    ecranul pierde exact constatarea care spunea că ceva n-a mers."""
    c = main._constatare_esuata("Verificare stocuri — eșuată", "stocurile", ValueError("x"), 2026, 7)
    assert c["fel"] == "necunoastere" and c["stare"] == "gri"
    for camp in FELURI["necunoastere"]:
        assert camp in c
