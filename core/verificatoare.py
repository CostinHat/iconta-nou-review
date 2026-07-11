"""
core/verificatoare.py — verificatoare de coerență contabilă. Calcul PUR, fără DB.
Generație nouă: fiecare eșec întoarce o PROBLEMĂ cu justificare (cod/mesaj/temei/nivel).

Surse: OMFP 1802/2014 (partidă dublă, balanță, decont TVA); cota TVA din common (cu dată).
"""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "verificatoare"


# ============================================================
#  ECHILIBRU NOTĂ (partidă dublă) — BLOCANT
# ============================================================
def echilibru_nota(note):
    """
    Notă simplă {debit, credit, suma} (mereu echilibrată) sau listă de linii
    {cont, debit?, credit?}. Întoarce common.ok() sau o problemă BLOCANT.
    """
    if isinstance(note, dict) and "debit" in note and "credit" in note:
        return c.ok()

    deb = cre = Decimal(0)
    for n in note:
        if "debit" in n and "credit" in n and "suma" in n:
            deb += _dec(n["suma"]); cre += _dec(n["suma"])
        else:
            deb += _dec(n.get("debit", 0))
            cre += _dec(n.get("credit", 0))
    if _q(deb) != _q(cre):
        return c.problema("NOTA_NEECHILIBRATA", nivel=c.BLOCANT,
                          debit=_q(deb), credit=_q(cre))
    return c.ok()


# ============================================================
#  BALANȚĂ
# ============================================================
def balanta(note, solduri_initiale=None):
    rulaj_d = defaultdict(Decimal)
    rulaj_c = defaultdict(Decimal)
    for n in note:
        s = _dec(n["suma"])
        rulaj_d[n["debit"]] += s
        rulaj_c[n["credit"]] += s

    si = {k: _dec(v) for k, v in (solduri_initiale or {}).items()}
    conturi = set(rulaj_d) | set(rulaj_c) | set(si)
    rez = {}
    for ct in sorted(conturi):
        sold = si.get(ct, Decimal(0)) + rulaj_d[ct] - rulaj_c[ct]
        rez[ct] = {"debit": _q(rulaj_d[ct]), "credit": _q(rulaj_c[ct]), "sold": _q(sold)}
    return rez


def verifica_balanta(bal):
    """Egalitatea balanței: total sume debitoare = total sume creditoare. BLOCANT."""
    td = sum((v["debit"] for v in bal.values()), Decimal(0))
    tc = sum((v["credit"] for v in bal.values()), Decimal(0))
    if _q(td) != _q(tc):
        return c.problema("BALANTA_INEGALA", nivel=c.BLOCANT,
                          debit=_q(td), credit=_q(tc))
    # echilibru_si_v1: si soldurile trebuie sa se inchida (SI debitor = SI creditor)
    ts = sum((v["sold"] for v in bal.values()), Decimal(0))
    if _q(ts) != 0:
        return c.problema("BALANTA_INEGALA", nivel=c.BLOCANT,
                          debit=_q(td), credit=_q(tc), diferenta_solduri=_q(ts))
    return c.ok()


# ============================================================
#  COERENȚĂ TVA
# ============================================================
def coerenta_tva(tva_colectata, tva_deductibila):
    """Decont: 4427 > 4426 -> de plată (4423); altfel de recuperat (4424)."""
    col = _dec(tva_colectata)
    ded = _dec(tva_deductibila)
    dif = col - ded
    nota = {"debit": "4427", "credit": "4426", "suma": _q(min(col, ded)),
            "modul": MODUL, "reguli": REGULI}
    if dif >= 0:
        return {"rezultat": "de_plata", "cont": "4423", "suma": _q(dif), "nota": nota}
    return {"rezultat": "de_recuperat", "cont": "4424", "suma": _q(-dif), "nota": nota}


def verifica_tva_pe_cota(baza, tva, la_data=None):
    """
    Verifică TVA = bază × cota standard valabilă LA DATA tranzacției.
    Prinde greșeli de perioadă (19% pe o tranzacție de după 01.08.2025). BLOCANT.
    """
    cota, temei = c.cota("tva_standard", la_data)
    asteptat = _q(_dec(baza) * cota)
    if _q(tva) != asteptat:
        cota_pct = int(cota * 100)
        return c.problema("TVA_COTA_GRESITA", nivel=c.BLOCANT,
                          baza=_q(baza), cota_pct=cota_pct,
                          gasit=_q(tva), asteptat=asteptat,
                          diferenta=_q(_dec(tva) - asteptat))
    return c.ok()


# ============================================================
#  COERENȚĂ TREZORERIE
# ============================================================
def coerenta_d205_457(suma_d205, suma_457):
    """Compara suma bruta declarata in D205 (tip_venit=08, dividende) cu
    suma bruta repartizata in contabilitate (1171->457) pentru acelasi an.
    Diferenta poate insemna dividende nedeclarate sau postari lipsa."""
    d = _dec(suma_d205)
    s457 = _dec(suma_457)
    dif = d - s457
    return {"suma_d205": _q(d), "suma_457": _q(s457), "diferenta": _q(dif),
            "coerent": dif == 0}
def verifica_trezorerie(bal, conturi=("5121", "5124", "5311", "5314")):
    """Conturile de trezorerie nu pot avea sold creditor. Întoarce listă de probleme."""
    probleme = []
    for ct in conturi:
        if ct in bal and bal[ct]["sold"] < 0:
            probleme.append(c.problema("TREZORERIE_NEGATIVA", nivel=c.BLOCANT,
                                       cont=ct, sold=bal[ct]["sold"]))
    return probleme
