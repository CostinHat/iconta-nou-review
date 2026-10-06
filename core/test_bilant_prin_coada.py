# -*- coding: utf-8 -*-
"""GARD — bilanțul trece prin coadă: pregătit → validat → depus, cu drepturile declarațiilor (decizia Costin 07.10.2026, C11).

Înainte: ecranul Bilanț valida la ANAF și descărca XML-ul; bilanțul nu intra în coadă, nu avea patru ochi, nu se persista ca
depus. Acum S1005/S1003 sunt tipuri ale dispecerului (`declaratii_api.SITUATII_FINANCIARE`), deci coada, poarta validatorului, aprobarea,
depunerea și persistarea sunt cele ale oricărei declarații; intrarea rămâne ecranul Bilanț (nu și selectorul generic).
CE FACE IMPOSIBIL: bilanțul scos din dispecer (deci din coadă) sau un ecran Bilanț care trimite pe alt drum decât cel comun.
"""
import os
import re

from core import declaratii_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_bilantul_e_declaratie_a_dispecerului():
    """MUTAȚIE: „s1003” scos din SITUATII_FINANCIARE -> pică."""
    assert (declaratii_api.periodicitate("s1005"), declaratii_api.periodicitate("s1003")) == ("anual", "anual")
    assert set(declaratii_api.SITUATII_FINANCIARE) == {"s1005", "s1003"}
    # nu sunt declarații fiscale: nici în lista celor 50, nici în selectorul generic (intrarea e ecranul Bilanț)
    assert not ({"s1005", "s1003"} & (set(declaratii_api.DECLARATII) | set(declaratii_api.tipuri())))


def test_ecranul_bilant_trimite_pe_drumul_comun_al_cozii():
    src = open(os.path.join(RAD, "static/js/ecrane/firme.js"), encoding="utf-8").read()
    bloc = src[src.index("async function ecranBilant("):src.index("export async function ecranStocuri(")]
    assert re.search(r'id="bl-coada" data-actiune="POST /coada"', bloc)
    assert re.search(r"await trimiteInCoada\(zona, \{ tenant_id: t\.id, tip: tip\(\), an:", bloc)
    assert not re.search(r'api\.post\("/coada"', bloc)               # nu un al doilea drum, construit pe loc


def test_termenul_bilantului_e_cel_din_lege():
    """Legea 82/1991 art.36 alin.(1) lit.a): „… până la data de 31 mai inclusiv a exercițiului financiar următor celui de
    raportare”; alin.(1^1): zi nelucrătoare -> prima zi lucrătoare următoare. 31.05.2026 = duminică, 01.06.2026 = Rusalii /
    Ziua Copilului -> 02.06.2026. MUTAȚIE: 31 mai -> 30 aprilie -> pică."""
    from core import scadente
    assert scadente.scadenta("s1003", 2025) == scadente.scadenta("s1005", 2025) == "02.06.2026"
    assert scadente.scadenta("s1005", 2026) == "31.05.2027"      # luni
