# -*- coding: utf-8 -*-
"""GOLDEN pe EFECT: ce cifră iese pe căile reparate la R26, nu ce cotă a intrat.

DE CE EXISTĂ. `test_cota_fara_default.py` verifică forma (defaultul a dispărut) și refuzul (calea fără
cotă ridică). Nici una nu spune **ce cifră iese**. Costin, 23.08.2026: *„o cotă corectă care nu e
verificată nu e reparată, e mutată. […] Nu «ce cotă a folosit», ci ce iese: cifra finală, pe date care
exercită calea."*

CARE TREI CĂI, și de ce astea. Nu există „trei căi vii" — măsurat, **una singură** era vie
(`nota_decont`). Le-am ales pe cele trei unde cota **schimbă cifra finală în feluri diferite**:

  1. `deconturi.nota_decont` — **singura cale VIE**. Cota decide dacă apare linia `4426` (TVA
     deductibilă) și cu ce sumă. Aici tăcerea ȘTERGEA o deducere.
  2. `taxare_inversa.tva_beneficiar` — cota apare de DOUĂ ori, colectată și deductibilă (4426=4427);
     o cotă greșită se duce în amândouă și se anulează în total, dar **nu** în declarație.
  3. `tva_marja.vanzare_marja` — cota se aplică pe **marjă**, nu pe preț, prin sutimea mărită; e
     singura dintre cele trei unde formula însăși depinde de cotă, iar funcția e **versionată pe dată**.

CE NU FACE: nu acoperă toate cele 26 de funcții reparate — celelalte 23 sunt latente (niciun apelant nu
lăsa defaultul să lucreze) și au deja golden-uri pe cotă explicită în suitele lor.
"""
from datetime import date
from decimal import Decimal

import pytest

from core import deconturi, taxare_inversa, tva_marja


# ─────────────────────────────────────────── 1. decontul: calea VIE
def test_decontul_cu_cazare_pe_factura_DEDUCE_tva():
    """Cazare 400 + transport 200 la 21% → TVA deductibilă 126,00, pe linia 4426.
    Ăsta e exact efectul pe care tăcerea îl ștergea."""
    r = deconturi.nota_decont(1000, diurna=287.50, transport=200, cazare=400, cota_tva=21)
    linii = {(d, c): s for d, c, s in r["linii"]}
    assert linii[("4426", "542")] == Decimal("126.00")          # 21% × (200+400)
    assert linii[("625", "542")] == Decimal("887.50")           # cheltuiala, fara TVA
    assert r["total_cheltuieli"] == Decimal("1013.50")          # 887,50 + 126,00
    assert r["diferenta"] == Decimal("-13.50")                  # avans 1000 < total


def test_decontul_cu_cota_ZERO_nu_deduce_nimic_si_o_arata():
    """`0` rămâne răspuns bun — dar DECLARAT. Diferența față de tăcere: aici e o alegere."""
    r = deconturi.nota_decont(1000, diurna=287.50, transport=200, cazare=400, cota_tva=0)
    conturi = {d for d, _c, _s in r["linii"]}
    assert "4426" not in conturi, "cotă 0 nu produce TVA deductibilă"
    assert r["total_cheltuieli"] == Decimal("887.50")
    assert r["diferenta"] == Decimal("112.50")                  # rest de restituit


def test_DIFERENTA_dintre_cele_doua_e_chiar_TVA_pierduta():
    """Măsura defectului, ca cifră: ce se pierdea când ruta punea tăcut 0."""
    cu = deconturi.nota_decont(1000, diurna=287.50, transport=200, cazare=400, cota_tva=21)
    fara = deconturi.nota_decont(1000, diurna=287.50, transport=200, cazare=400, cota_tva=0)
    assert cu["total_cheltuieli"] - fara["total_cheltuieli"] == Decimal("126.00")


@pytest.mark.parametrize("cota,tva", [(21, Decimal("126.00")), (11, Decimal("66.00")),
                                      (19, Decimal("114.00")), (0, Decimal("0.00"))])
def test_decontul_urmeaza_cota_data_nu_una_fixa(cota, tva):
    """Calea chiar folosește cota primită — pe patru cote, inclusiv cea istorică de 19%."""
    r = deconturi.nota_decont(2000, diurna=0, transport=200, cazare=400, cota_tva=cota)
    linii = {(d, c): s for d, c, s in r["linii"]}
    assert linii.get(("4426", "542"), Decimal("0.00")) == tva


# ─────────────────────────────────────────── 2. taxarea inversă
@pytest.mark.parametrize("cota,asteptat", [(21, Decimal("2100.00")), (19, Decimal("1900.00")),
                                           (11, Decimal("1100.00"))])
def test_taxarea_inversa_da_cifra_pe_cota_data(cota, asteptat):
    """4426 = 4427 pe aceeași sumă: o cotă greșită se anulează în total, dar NU în declarație —
    de-aia cifra contează chiar dacă efectul net e zero."""
    assert taxare_inversa.tva_beneficiar(10000, cota) == asteptat


def test_taxarea_inversa_rotunjeste_la_ban():
    assert taxare_inversa.tva_beneficiar(333.33, 21) == Decimal("70.00")


# ─────────────────────────────────────────── 3. marja: cota intră în FORMULĂ
def test_marja_aplica_suta_marita_nu_cota_pe_pret():
    """Vânzare 1000, cumpărare 600 → marjă brută 400; TVA = 400 × 21/121 = 69,42, nu 21% din 1000."""
    r = tva_marja.vanzare_marja(1000, 600, 21, la_data=date(2026, 6, 1))
    assert r["tva"] == Decimal("69.42")
    assert r["tva"] != Decimal("210.00"), "cota s-a aplicat pe preț, nu pe marjă"


def test_marja_pe_cota_istorica_da_ALTA_cifra():
    """Aceeași marjă, cota de dinainte de 01.08.2025: 400 × 19/119 = 63,87. Dacă cele două ar fi
    egale, cota n-ar ajunge în formulă — exact defectul pe care îl păzim."""
    azi = tva_marja.vanzare_marja(1000, 600, 21, la_data=date(2026, 6, 1))
    vechi = tva_marja.vanzare_marja(1000, 600, 19, la_data=date(2026, 6, 1))
    assert vechi["tva"] == Decimal("63.87")
    assert azi["tva"] != vechi["tva"]


def test_marja_negativa_nu_produce_tva():
    r = tva_marja.vanzare_marja(600, 1000, 21, la_data=date(2026, 6, 1))
    assert r["tva"] == Decimal("0.00")
