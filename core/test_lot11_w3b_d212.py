# -*- coding: utf-8 -*-
"""[lotul 11, subagentul w3b, deficiența 440 pe server — comanda Costin 11.1 pct.16, verbatim] „toate erorile apar deodată, fiecare cu
textul ei”. D212 (B36 din lista U0): generarea se oprea la PRIMA secțiune greșită (venit / venit din străinătate / activitate pe normă),
iar datele contribuabilului (numele, adresa, CNP-ul — `erori_generare`) nu se mai verificau deloc; contabilul corecta o secțiune, genera
din nou, afla de următoarea. Acum: toate motivele, numerotate, dintr-o trecere; un singur motiv rămâne fraza lui de până acum.

Temei: N/A — forma refuzului. Regulile secțiunilor (OPANAF 2736/2025, CF) rămân în `cap11_categorie` / `cap12_norma` / `cap14_sectiune`,
neatinse; testul nu le reafirmă.
"""
import pytest

from core import d212
from core.common import Perioada

CNP_BUN = "1800101221144"   # verificat cu algoritmul oficial (CLAUDE.md „Date de test”); același ca în core/test_d212_cap12.py
CNP = "1800101221145"       # același, cu cifra de control greșită (4 -> 5): invalid intenționat
AN = 2025


def test_cnp_urile_de_proba_verificate():
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(CNP_BUN[i]) * ch[i] for i in range(12)) % 11
    assert str(1 if c == 10 else c) == CNP_BUN[12] and CNP[:12] == CNP_BUN[:12] and CNP[12] != CNP_BUN[12]


def test_b36_toate_motivele_d212_deodata():
    """Activitatea 1 cu două greșeli independente (norma 0, forma de organizare 3), activitatea 2 cu norma ajustată negativă, CNP invalid,
    numele lipsă: cinci motive, numerotate, fiecare cu textul lui. MUTAȚII: `raise ValueError(...)` repus în bucla activităților (forma
    veche) -> numai „Activitatea 1” -> pică; `motive.append` al normei înlocuit cu `raise` în `cap12_norma` -> forma de organizare
    lipsește -> pică."""
    with pytest.raises(ValueError) as e:
        d212.genereaza(None, None, Perioada(an=AN), {"cif": CNP, "nume_c": "", "adresa_c": "Bucuresti Sector 1",
                                                     "norma": [{"norma": 0, "forma_org": 3}, {"norma": 1000, "norma_ajustata": -5}]})
    m = str(e.value)
    assert m.startswith("D212 nu se poate genera — 5 motive; rezolvă-le pe toate, apoi generează din nou.\n"), m   # 440: toate deodată
    randuri = m.split("\n")[1:]
    assert [r.split(" — ")[0] for r in randuri] == ["1. Activitatea 1", "2. Activitatea 1", "3. Activitatea 2",
                                                    "4. Lipsă nume/denumire contribuabil (nume_c).",
                                                    "5. CNP contribuabil (cif) invalid (13 cifre + cifra de control)."], m
    assert randuri[:3] == ["1. Activitatea 1 — D212 normă: norma anuală de venit (rd.7) lipsește — se ia din lista DGRFP pentru locul "
                           "activității.", "2. Activitatea 1 — D212 normă: forma de organizare 3 — 1 individual, 2 asociere.",
                           "3. Activitatea 2 — D212 normă: norma ajustată (rd.8) nu poate fi negativă."], m   # fiecare cu textul lui


def test_b36_un_singur_motiv_ramane_fraza_lui():
    """Contractul de până acum, pentru un singur motiv (`core/test_d212_cap12.py::test_eroarea_numeste_activitatea`)."""
    with pytest.raises(ValueError) as e:
        d212.genereaza(None, None, Perioada(an=AN), {"cif": CNP_BUN, "nume_c": "POPESCU ION", "adresa_c": "Bucuresti",
                                                     "norma": [{"norma": 1000}, {"norma": 0}]})
    assert str(e.value).startswith("Activitatea 2 — D212 normă: norma anuală de venit (rd.7) lipsește"), str(e.value)
