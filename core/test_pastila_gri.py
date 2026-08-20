# -*- coding: utf-8 -*-
"""GARD (20.08.2026): griul nu se falsifică niciodată în verde.

DE CE. Verdele e o AFIRMAȚIE — „am verificat și e în regulă". Griul spune că afirmația nu se poate face.
O afirmație parțial imposibilă nu devine adevărată prin partea care s-a putut face.

CE S-A ÎNTÂMPLAT. `_RANG_STARE` n-avea intrare pentru „gri", deci primea rangul 0, iar `max` îl punea sub
verde (rang 1). Orice constatare verde ștergea griul — deși verdele nu escaladează nimic. Ambele
docstring-uri spuneau opusul: `_stare` („Gri nu poate fi ascuns ca verde") și `pastila_firma` („base 'gri'
se păstrează dacă nimic confirmat nu escaladează"). Regula era scrisă corect și neimplementată.

EFECT MĂSURAT pe cabinetul 1968: 2 firme afișate verzi, AMÂNDOUĂ cu baza gri. Lista de firme curate a
contabilului era falsă în întregime — iar cele două erau exact firmele despre care aplicația știa cel mai
puțin. A treia instanță în două zile a clasei „verde = n-am ce contrazice, nu = am verificat"; primele
două erau interne (F3/F7 pe tabele goale la 006; raportul meu de audit pe t001). **Asta o vede clientul.**

Gardul lucrează pe funcția PURĂ — nu depinde de nicio firmă, deci nu poate fi „verde fiindcă n-are ce
contrazice", chiar defectul pe care îl păzește.
"""
import pytest

from core.common import pastila_firma, _RANG_STARE


def test_gri_nu_devine_verde():
    """Miezul: o constatare verde nu poate scoate firma din gri."""
    assert pastila_firma("gri", [{"stare": "verde"}]) == "gri"
    assert pastila_firma("gri", [{"stare": "verde"}, {"stare": "verde"}]) == "gri"


def test_gri_ramane_gri_fara_constatari():
    assert pastila_firma("gri", []) == "gri"
    assert pastila_firma("gri", [{"stare": "gri"}]) == "gri"
    assert pastila_firma("gri", [None]) == "gri"


def test_confirmatul_escaladeaza_griul():
    """O problemă CUNOSCUTĂ bate o necunoaștere — altfel griul ar ascunde restanțe."""
    assert pastila_firma("gri", [{"stare": "galben"}]) == "galben"
    assert pastila_firma("gri", [{"stare": "rosu"}]) == "rosu"
    assert pastila_firma("gri", [{"stare": "verde"}, {"stare": "rosu"}]) == "rosu"


def test_bazele_necolorate_gri_neatinse():
    """Fixul nu schimbă nimic pe celelalte baze - escaladarea rămâne max(base, constatări)."""
    assert pastila_firma("verde", [{"stare": "verde"}]) == "verde"
    assert pastila_firma("verde", [{"stare": "rosu"}]) == "rosu"
    assert pastila_firma("rosu", [{"stare": "verde"}]) == "rosu"
    assert pastila_firma("galben", [{"stare": "verde"}]) == "galben"
    assert pastila_firma("galben", [{"stare": "rosu"}]) == "rosu"


def test_supra_escaladarea_ramane_interzisa():
    """Contractul vechi, neatins: pastila NU poate depăși max(constatări) când baza e mai blândă."""
    assert pastila_firma("verde", [{"stare": "galben"}]) == "galben"
    assert pastila_firma("verde", []) == "verde"


def test_gardul_chiar_vede_functia():
    """Anti-vacuu: dacă tabelul de ranguri se schimbă sub gardă, testele de mai sus ar putea trece pe gol."""
    assert _RANG_STARE.get("galben") and _RANG_STARE.get("rosu"), _RANG_STARE
    assert _RANG_STARE.get("gri") is None, \
        "«gri» a intrat în _RANG_STARE - reevaluează gardul: nu mai e o stare în afara scării de gravitate"
