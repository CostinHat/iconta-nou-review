# -*- coding: utf-8 -*-
"""core/sume_lei.py — conversia in lei a unei facturi, intr-un SINGUR loc.

DE CE (A1, runda a doua de audit, 17.09.2026). `total_lei/tva_lei/curs_bnr` existau pe factura si se
scriau la emitere, dar niciun generator de declaratie nu le citea: D300 (`_segmente`), D394, D390,
D406 si contarea luau `cantitate x pret_unitar` si `total/tva` — sumele IN VALUTA. O factura de
1.000 EUR intra in decont ca 1.000 lei. Validatorul trecea (raportul TVA/baza e corect), a doua cale
de reconciliere si controlul incrucisat la fel — fiindca toate citeau aceeasi sursa cu aceeasi
greseala. Masurat: `calcul_d300` cu o factura EUR curs 5 dadea R9_1=1000 in loc de 5000.

REGULA, de-acum: **nicio cifra nu intra intr-o declaratie sau intr-o nota fara sa treaca prin curs.**
Cursul sta pe document, inghetat la introducere (RON are cursul 1 prin lege). O factura in valuta
FARA curs nu se poate exprima in lei — si atunci NU se ghiceste 1 (asta e chiar greseala), ci se
ridica `LipsaCurs`, iar apelantul o EXCLUDE din declaratie si o semnaleaza. E a treia stare, nu un
implicit (interdictia 32: un necunoscut nu se rotunjeste la „stiu ca nu"): valoare / RON=1 / necunoscut.

CINE APELEAZA (sursa unica; a doua conversie ar fi inceputul unei divergente):
  - `core/d300.py` (`_segmente`, `calcul_d300` exclude+semnaleaza)
  - `core/d394.py` (`pull`), `core/d390.py` (`_facturi_ic`), `core/d406.py` (liniile SAF-T)
  - `core/contare_facturi.py` (nota 4426/4427/4111/401 — cartea in lei)
Poarta la introducere: `core/facturi_api.py` scrie total_lei/curs_bnr la creare (RON->1), iar contarea
REFUZA o factura in valuta fara curs.
"""
from __future__ import annotations
from decimal import Decimal


class LipsaCurs(Exception):
    """Factura in valuta fara `curs_bnr` — nu se poate exprima in lei fara sa inventezi cursul."""

    def __init__(self, factura_id=None, moneda=None):
        self.factura_id = factura_id
        self.moneda = moneda
        super().__init__(
            "factura #%s în %s nu are curs BNR: nu se poate conta și nu poate intra într-o "
            "declarație în lei (Cod fiscal art. 290)." % (factura_id, moneda or "?"))


def e_ron(moneda) -> bool:
    return (str(moneda or "RON").strip().upper() or "RON") == "RON"


def curs_factura(f) -> Decimal:
    """Cursul unei facturi ca `Decimal`. RON -> 1. Valuta cu `curs_bnr` -> acel curs.
    Valuta FARA curs -> `LipsaCurs` (nu se ghiceste 1)."""
    c = f.get("curs_bnr")
    if c is not None:
        return Decimal(str(c))
    if e_ron(f.get("moneda")):
        return Decimal(1)
    raise LipsaCurs(f.get("id") or f.get("factura_id"), f.get("moneda"))


def baza_lei(cantitate, pret_unitar, curs) -> Decimal:
    """Baza unei linii, in lei: cantitate x pret x curs. FARA rotunjire aici — rotunjirea e a
    apelantului (D300 pe cota, contarea pe nota, D406 pe linie), o singura data, la capat."""
    return Decimal(str(cantitate)) * Decimal(str(pret_unitar)) * Decimal(curs)


def antet_lei(f):
    """(total_lei, tva_lei) al facturii, ca `Decimal`. Daca cele doua coloane sunt populate, ele
    sunt autoritatea (calculate o data la creare). Altfel, daca cursul se stie, se deriva din
    total/tva x curs. Valuta fara curs -> `LipsaCurs`."""
    tl = f.get("total_lei")
    vl = f.get("tva_lei")
    if tl is not None and vl is not None:
        return Decimal(str(tl)), Decimal(str(vl))
    curs = curs_factura(f)
    return (Decimal(str(f.get("total") or 0)) * curs,
            Decimal(str(f.get("tva") or 0)) * curs)
