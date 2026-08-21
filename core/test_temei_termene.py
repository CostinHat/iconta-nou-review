# -*- coding: utf-8 -*-
"""GARD (R4, 20.08.2026 — refăcut 21.08): fiecare termen de depunere își poartă actul, ca DATE.

DECIZIA (Costin): termenele sunt constante fiscale ca oricare altele — temeiul se atașează PER TIP.
Argumentul care închide „25 e notoriu": notorietatea e o proprietate a CUNOAȘTERII, nu a valorii.
Termenele s-au schimbat de două ori în viața aplicației și NICIUNA n-a fost prinsă de un test:
scadența D101 era 25.03 hardcodat (marca fals restanțieri firmele care depuneau apr-iun), iar ziua 30
inexistentă în februarie a ieșit în timpul cablării D394.

DE CE E REFĂCUT — două defecte ale primei versiuni, amândouă găsite pe 21.08:

  1. **Regexul lui nu putea potrivi NIMIC.** Începea cu un octet 0x08 (backspace) în loc de `\\b` —
     probabil un `\\b` interpretat de shell la scrierea fișierului. Deci `xfail(strict=True)` trecea
     mereu ca „încă nerezolvat", indiferent câtă muncă s-ar fi făcut. Un gard care nu poate deveni
     verde nu e o datorie, e o promisiune imposibilă.
  2. **Citea PROXIMITATE în proză.** După reparare, o notă „unde se caută pentru cele nesursate" a
     făcut toate cele 9 tipuri să pară sursate, fiindcă numele lor stătea lângă un act. Proximitatea
     nu e atribuire — aceeași lecție ca la clasa E din scanul de constante.

Acum citește un REGISTRU (`scadente.TEMEI_TERMEN`) și verifică citatul VERBATIM în corpus. Clichet:
numărul de tipuri sursate nu mai scade.
"""
import os
import re
import unicodedata

import pytest

from core import scadente

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# tipurile care primesc un termen prin `_data_nominala`; `None` = regula implicită (ziua 25)
TIPURI = ["d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406"]

# Instalat 21.08.2026: D300, D301, D390 sursate verbatim. Se RIDICĂ pe măsură ce se sursează restul.
SURSATE_BASELINE = 3


def _norm(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _sursate():
    """Tipurile al căror citat se GĂSEȘTE în documentul indicat. Nu «are o intrare» — se verifică."""
    ok = []
    for tip, (act, url, citat) in sorted(scadente.TEMEI_TERMEN.items()):
        p = os.path.join(_RAD, url)
        if not (act and citat and os.path.exists(p)):
            continue
        doc = _norm(open(p, encoding="utf-8", errors="replace").read())
        if _norm(citat) in doc:
            ok.append(tip)
    return ok


def test_gardul_vede_modulul():
    """Anti-vacuu: dacă `scadente.py` se mută sau se golește, testele de mai jos ar trece pe gol."""
    s = open(os.path.join(_RAD, "core", "scadente.py"), encoding="utf-8").read()
    assert "_data_nominala" in s and "_ZIUA" in s, "scadente.py nu mai are forma așteptată"
    assert len(TIPURI) >= 8 and scadente.TEMEI_TERMEN, "registrul de temeiuri e gol"


def test_citarile_existente_sunt_REALE(inv=None):
    """Miezul care lipsea: nu «există o intrare», ci citatul chiar se găsește în actul indicat.
    Fără asta, registrul ar fi doar o listă de afirmații despre acte."""
    rele = []
    for tip, (act, url, citat) in sorted(scadente.TEMEI_TERMEN.items()):
        p = os.path.join(_RAD, url)
        if not os.path.exists(p):
            rele.append("%s: fișierul %s lipsește din corpus" % (tip, url))
            continue
        doc = _norm(open(p, encoding="utf-8", errors="replace").read())
        if _norm(citat) not in doc:
            rele.append("%s: citatul nu se găsește în %s" % (tip, url))
    assert not rele, (
        "temeiuri de termen care nu se verifică la sursă:\n  " + "\n  ".join(rele)
        + "\n\nCitatul se ia VERBATIM din corpus. Dacă actul s-a schimbat, se schimbă și citatul — "
        "o referință care nu mai aterizează e mai rea decât niciuna.")


def test_numarul_de_termene_sursate_nu_scade():
    """Clichet. R4 e o datorie care se ARDE per tip, nu una binară — prima versiune era binară și,
    fiind și ruptă, n-avea cum să cadă niciodată."""
    n = len(_sursate())
    assert n >= SURSATE_BASELINE, (
        "termene sursate: %d < %d. O citare s-a pierdut sau nu mai aterizează." % (n, SURSATE_BASELINE))


def test_clichetul_nu_e_stat():
    n = len(_sursate())
    assert n <= SURSATE_BASELINE, (
        "sunt %d termene sursate, pragul e %d — ridică SURSATE_BASELINE, altfel câștigul se poate "
        "pierde tăcut." % (n, SURSATE_BASELINE))


def test_datoria_ramasa_e_numita():
    """Ce NU e sursat trebuie să se vadă, nu să se topească într-un procent."""
    lipsa = [t for t in TIPURI if t not in _sursate()]
    assert lipsa, "toate tipurile sunt sursate — ridică pragul și șterge testul ăsta"
    assert set(lipsa) == {"d100", "d101", "d112", "d205", "d394", "d406"}, (
        "s-a schimbat lista datoriei rămase: %s. Actualizeaz-o odată cu pragul." % sorted(lipsa))


def test_potrivirea_nu_e_permisiva():
    """Contra-direcția: un fragment scurt nu trebuie să treacă drept citat, altfel clichetul se poate
    ridica scriind „art." în registru."""
    doc = _norm(open(os.path.join(_RAD, "anaf_surse", "opanaf_705_2020_d390.txt"),
                     encoding="utf-8", errors="replace").read())
    assert _norm("se depune lunar, până la data de 25 inclusiv") in doc
    assert _norm("această frază nu există în ordinul acela") not in doc


@pytest.mark.parametrize("tip", sorted(scadente.TEMEI_TERMEN))
def test_fiecare_intrare_poarta_cele_trei_campuri(tip):
    act, url, citat = scadente.TEMEI_TERMEN[tip]
    assert act and url and citat, "intrare incompletă pentru %s" % tip
    assert url.startswith("anaf_surse/"), "temeiul trebuie să trimită în corpus, nu în altă parte"
    assert len(_norm(citat)) > 25, "citat prea scurt ca să fie verificabil: %r" % citat
