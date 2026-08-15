# -*- coding: utf-8 -*-
"""Stocuri — metoda cantitativ-valorică, evaluare la CMP (cost mediu ponderat).
OMFP 1802/2014 pct. 96: CMP se recalculează după fiecare intrare.

Fișa de magazie: intrări/ieșiri cronologice per articol.
Ieșire: valoare = cantitate * CMP curent. Nota: 607=371 (marfa) / 601=301 (materii prime).
"""
from decimal import Decimal, ROUND_HALF_UP

MODUL = "stocuri_cv"
REGULI = "2026.1"
TEMEI_CMP = "OMFP 1802/2014 pct. 96 - cost mediu ponderat"


def _d(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))


def _q(v):
    return _d(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _q4(v):
    return _d(v).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def fisa_magazie(miscari, stoc_initial=None):
    """miscari: [{tip: 'intrare'|'iesire', cantitate, pret_unitar? (doar la intrare),
    data, document?}] in ordine cronologica.
    stoc_initial: {cantitate, valoare} sau None.
    Intoarce liniile fisei cu sold cantitate/valoare/CMP dupa fiecare miscare.
    Ridica ValueError la iesire peste stoc."""
    cant = _d((stoc_initial or {}).get("cantitate", 0))
    val = _d((stoc_initial or {}).get("valoare", 0))
    out = []
    for m in miscari:
        c = _d(m["cantitate"])
        if c <= 0:
            raise ValueError(f"cantitate invalida: {m}")
        if m["tip"] == "intrare":
            v = _q(c * _d(m["pret_unitar"]))
            cant += c
            val += v
        elif m["tip"] == "iesire":
            if c > cant:
                raise ValueError(f"iesire {c} peste stocul {cant} la {m.get('data')}")
            cmp_curent = val / cant  # cant > 0 garantat de conditia de mai sus
            v = _q(c * cmp_curent)
            cant -= c
            val = _q(val - v) if cant > 0 else Decimal("0.00")
            if cant == 0:
                val = Decimal("0.00")
        else:
            raise ValueError(f"tip necunoscut: {m['tip']!r}")
        out.append({**m, "valoare": _q(v), "sold_cantitate": cant,
                    "sold_valoare": _q(val),
                    "cmp": _q4(val / cant) if cant > 0 else None})
    return out


def valoare_iesire(miscari, stoc_initial, cantitate):
    """Valoarea unei iesiri noi de `cantitate`, la CMP-ul rezultat din istoric.
    Intoarce {cantitate, cmp, valoare, temei}."""
    fisa = fisa_magazie(miscari, stoc_initial)
    if fisa:
        cant, val = fisa[-1]["sold_cantitate"], _d(fisa[-1]["sold_valoare"])
    else:
        cant = _d((stoc_initial or {}).get("cantitate", 0))
        val = _d((stoc_initial or {}).get("valoare", 0))
    c = _d(cantitate)
    if c <= 0:
        raise ValueError("cantitate invalidă")
    if c > cant:
        raise ValueError(f"iesire {c} peste stocul {cant}")
    cmp_curent = val / cant
    return {"cantitate": c, "cmp": _q4(cmp_curent), "valoare": _q(c * cmp_curent),
            "temei": TEMEI_CMP, "modul": MODUL, "reguli": REGULI}
