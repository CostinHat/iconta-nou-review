# -*- coding: utf-8 -*-
"""Lotul 12, pachetul firme1 — Raport Z: 474.

474 (Costin, comanda 12.1): „Raport Z: Z validat cu descărcare parțială din stoc, fără avertisment.” Z-ul n-are articole (casa de marcat nu
le dă), deci aplicația nu poate ști dacă descărcarea e completă: înainte de validare ecranul pune față în față vânzarea fără TVA a Z-ului
și costul mărfii descărcate (cu adaosul care ar rezulta) și cere confirmarea (`z_descarcare.avertisment_descarcare`). Temei: N/A — regulă de
produs (CLAUDE.md §9: nimic care poate induce în eroare); evaluarea ieșirilor la cost: OMFP 1802/2014 pct.287 (în antetul modulului).
"""
import re
from decimal import Decimal

from core import z_descarcare as _zd


def _bucati(text):
    """Membrii frazelor textului, întregi (despărțiți de „, ” „; ” „: ” „ — ” și de sfârșitul propoziției; „12,50” rămâne o sumă). Textul e
    lucrul verificat (474: ce i se spune contabilului), deci se citește pe bucățile lui, nu prin „șirul apare undeva”."""
    return [b.strip() for b in re.split(r"[,;:](?=\s)|\.(?=\s|$)|\s—\s", text) if b.strip()]


def test_474_avertismentul_spune_cifrele_si_adaosul():
    t = _zd.avertisment_descarcare(Decimal("200.00"), Decimal("12.50"), 1)
    assert t.startswith("Ai descărcat din stoc 1 ieșire la cost 12,50 lei, pentru vânzări de 200,00 lei fără TVA pe acest Z (adaos 1500%)."), t
    b = _bucati(t)
    i = b.index("dacă au mai ieșit și alte articole")
    assert b[i + 1] == "descarcă-le înainte de validare", b


def test_474_costul_peste_vanzare_se_spune_separat():
    t = _zd.avertisment_descarcare(Decimal("100.00"), Decimal("150.00"), 2)
    assert _bucati(t)[:3] == ["Ai descărcat din stoc 2 ieșiri la cost 150,00 lei", "pentru vânzări de 100,00 lei fără TVA pe acest Z",
                              "costul mărfii descărcate e MAI MARE decât vânzarea"], t


def test_474_fara_iesiri_niciun_avertisment():
    assert _zd.avertisment_descarcare(Decimal("100.00"), Decimal("0"), 0) is None
    t = _zd.avertisment_descarcare(Decimal("100.00"), Decimal("0"), 1)
    assert _bucati(t)[-1] == "verifică dacă ai descărcat tot", t
