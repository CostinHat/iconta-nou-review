# -*- coding: utf-8 -*-
"""GARDĂ pentru partea deschisă a interdicției 58 — conflictele NEÎNREGISTRATE între surse.

Prima măsurătoare a lui 58 a dat 0 conflicte nedecise, dar vedea doar ce era deja în
`registru_interpretari`. Scanul de aici caută **locurile unde s-a putut alege**: unde o citare legală
și o autoritate de nivel inferior (structura ANAF, validatorul, XSD-ul, jar-ul) apar în același bloc
de proză. Acolo cineva a ales, fie că a scris-o sau nu.

CALIBRARE, și a fost instructivă: cazul cunoscut — **podeaua part-time** — E GĂSIT, în
`d112_reconciliere.reconciliaza`, cu fragmentul *„OUG 156/2024 art.LXVI alin.(5) = OUG 89/2025
art.III: derogarea REDEFINEȘTE nivelul, 3750 în S1 / 4125 în S2"*. **Prima formă a verificării mele
îl declara RATAT**, fiindcă îl căuta după „art.146"/„168" — articolele din enunțul interdicției — pe
când decizia citează actele care fac derogarea. Verificarea era prea îngustă, nu scanul. De aceea
testul de mai jos pinează **locul**, nu cuvintele.

CE NU E, declarat: cele două surse se pot întâlni fără să se contrazică — codul poate cita legea
pentru regulă și structura pentru FORMATUL raportării. Cifra e o listă de **citit**, nu de defecte.
"""
import pytest

from core import scan_conflicte_sursa as sc


@pytest.fixture(scope="module")
def cand():
    return sc.candidati()


def test_cazul_cunoscut_podeaua_part_time(cand):
    """CAZ CUNOSCUT. Locul unde s-a ales între structura publicată și textul legii."""
    locuri = {(f, n) for f, n, _fr in cand}
    assert ("d112_reconciliere.py", "reconciliaza") in locuri, (
        "locul deciziei despre podeaua part-time nu mai e găsit — scanul nu poate pretinde că vede "
        "conflicte necunoscute dacă îl ratează pe singurul cunoscut. Găsite: %s"
        % sorted(x for x in locuri if x[0].startswith("d112")))


def test_gaseste_ambele_surse_nu_doar_una(cand):
    """Discriminatorul cere AMBELE. Un bloc cu doar lege, sau doar validator, nu e candidat."""
    doar_lege = "art. 291 din Codul fiscal, cota standard"
    doar_inferior = "structura ANAF cere campul in format ZZ.LL.AAAA"
    amandoua = "art. 146 alin.(5^6) CF, dar structura D112 v7 pune diminuarea in formula"
    assert not (sc._LEGAL.search(doar_inferior) and sc._INFERIOR.search(doar_inferior))
    assert not (sc._LEGAL.search(doar_lege) and sc._INFERIOR.search(doar_lege))
    assert sc._LEGAL.search(amandoua) and sc._INFERIOR.search(amandoua)


def test_lista_nu_e_vida_si_nu_e_totul(cand):
    """ANTI-VACUU în ambele direcții: o listă goală ar însemna că discriminatorul s-a rupt; una
    uriașă, că prinde orice fișier fiscal."""
    assert len(cand) >= 10, "doar %d candidați — discriminatorul s-a rupt" % len(cand)
    assert len(cand) <= 200, "%d candidați — discriminatorul a devenit prea larg" % len(cand)


def test_registrul_de_interpretari_ramane_populat():
    """Conflictele DECISE trăiesc într-un registru; dacă acela se golește, «0 nedecise» devine vid."""
    assert len(sc.decise()) >= 2, "registrul de interpretări s-a golit — 58 n-ar mai avea reper"
