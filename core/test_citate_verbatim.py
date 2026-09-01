# -*- coding: utf-8 -*-
"""CLICHET CARE CREȘTE (21.08.2026): numărul de citări verificabile mecanic nu mai scade.

Gardul de temeiuri verifică azi că citarea ATERIZEAZĂ pe un document din corpus. Limita lui, scrisă
pe față: nu verifică dacă actul spune ce pretinzi. Datoria din 30.07 o numește — opt mențiuni
canonizate fără reverificare, unde *canonizarea a făcut o regulă greșită să arate corect*.

DE CE CREȘTE, nu scade. Calibrat pe cele 34 de citări din registrul de cote (toate la nivel MO):
10 se găsesc verbatim, 24 nu — dar cele 24 NU sunt greșite, sunt de altă formă (parafrază cu
localizator: „art. II pct.42 modifică art.291 CF: cota standard 21%"), uneori mai utilă decât un
citat brut. O regulă „toate verbatim" ar fi cerut rescrierea a 24 de citări corecte.

Deci se păzește ce s-a CÂȘTIGAT: o citare nouă scrisă verbatim ridică pragul; una rescrisă din
verbatim în parafrază îl coboară — și pică.

CE NU POATE SPUNE (declarat, ca tăcerea să nu se citească drept acoperire): când un citat nu se
găsește, cauza poate fi (1) parafrază, (2) altă consolidare a actului în corpus, (3) citat GREȘIT.
Scanul nu le deosebește. Numărul e o măsură, nu un verdict — iar un gard care ar acuza corpusul s-ar
dezactiva singur.
"""
import pytest

from core import scan_citate

# Instalat 21.08.2026. Se RIDICĂ pe măsură ce citările devin verificabile. Nu se coboară.
VERBATIM_BASELINE = 11


@pytest.fixture(scope="module")
def inv():
    return scan_citate.inventar()


def test_citarile_verificabile_nu_scad(inv):
    """Miezul. O citare care era verbatim și devine parafrază pierde tăcut singura verificare care
    spune că actul chiar zice ce pretindem."""
    n = sum(1 for _c, _t, v in inv if v is True)
    assert n >= VERBATIM_BASELINE, (
        "citări verificabile mecanic: %d < %d. O citare verbatim a devenit parafrază, sau documentul "
        "din corpus s-a schimbat. Dacă e intenționat, coboară VERBATIM_BASELINE cu motivul scris — "
        "dar întâi întreabă-te dacă nu cumva citatul era greșit." % (n, VERBATIM_BASELINE))


def test_clichetul_nu_e_stat(inv):
    """Anti-datorie-stătută, ca la clichetul constantelor: ce s-a câștigat se ridică în prag."""
    n = sum(1 for _c, _t, v in inv if v is True)
    assert n <= VERBATIM_BASELINE + 4, (
        "sunt %d citări verbatim, pragul e %d — ridică VERBATIM_BASELINE, altfel câștigul se poate "
        "pierde tăcut." % (n, VERBATIM_BASELINE))


def test_fiecare_citare_are_text_si_url(inv):
    """Fără astea două, verificarea nici nu se poate încerca — iar `None` ar dilua măsura."""
    fara = ["%s (%s)" % (c, t) for c, t, v in inv if v is None]
    assert not fara, (
        "citări fără `text_citat` sau fără `url` către corpus, ori cu fișier lipsă: %s" % fara)


def test_scanul_chiar_vede_citarile(inv):
    """Anti-vacuu pe domeniu: dacă `common` se reorganizează și culegerea se golește, clichetul ar
    trece pe gol raportând verde despre o lume pe care n-o citește."""
    assert len(inv) >= 30, "prea puține citări văzute (%d) — verifică `scan_citate._temeiuri`" % len(inv)
    assert any(v is True for _c, _t, v in inv), "niciun citat verbatim — potrivirea s-a rupt"
    assert any(v is False for _c, _t, v in inv), (
        "TOATE citările trec — fie s-a rezolvat totul (ridică pragul), fie potrivirea a devenit "
        "prea permisivă și nu mai discriminează")


def test_potrivirea_nu_e_permisiva():
    """Contra-direcția, legată: un fragment scurt sau un localizator NU trebuie să treacă drept citat.
    Fără asta, potrivirea s-ar putea slăbi până devine tautologică."""
    class _T:
        text_citat = "art. 291"        # doar localizator, sub pragul de 25 de caractere normalizate
        url = "anaf_surse/legea_141_2025_consolidat.html"
    assert scan_citate._verbatim(_T()) is False


def test_normalizarea_ignora_diacritice_si_marcaj():
    """Documentele din corpus sunt HTML cu diacritice; citatele se scriu în text curat."""
    assert scan_citate._norm("<p>Cotă redusă&nbsp;de 11%</p>") == "cota redusa nbsp de 11"
