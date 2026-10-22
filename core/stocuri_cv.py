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


def _c(x, um):
    """Cantitatea în mesajul către contabil: formatul românesc și unitatea de măsură („1.000 buc”, „1,5 kg”), nu `Decimal`-ul coloanei
    NUMERIC(12,3) („139.000” se citea 139 de mii). [lotul 10, comanda 10.2 pct.8d] „La ieșirea peste stoc mesajul e «iesire 1000 peste
    stocul 139.000»: fără diacritice, iar «139.000» se citește 139 de mii. Corect: «Ieșire de 1.000 buc peste stocul de 139 buc».”"""
    from core import pdf_util
    return pdf_util.cantitate(x, um)


def _la(d):
    """„ la 20.10.2026” — data mișcării, în forma românească (DS cap.4); nimic dacă mișcarea n-o poartă."""
    from core import pdf_util
    return (" la %s" % pdf_util.data_ro(d)) if d not in (None, "") else ""


def mesaj_peste_stoc(cantitate, stoc, um="", data=None):
    """Refuzul ieșirii peste stoc, în cuvintele contabilului (sursa unică: fișa, ieșirea nouă, rețeta, transferul)."""
    return "Ieșire de %s peste stocul de %s%s" % (_c(cantitate, um), _c(stoc, um), _la(data))


def fisa_magazie(miscari, stoc_initial=None, um=""):
    """miscari: [{tip: 'intrare'|'iesire'|'ajustare' (de valoare, cantitate 0, `valoare`), cantitate, pret_unitar? (doar la intrare),
    data, document?}] in ordine cronologica.
    stoc_initial: {cantitate, valoare} sau None.
    um: unitatea de măsură a articolului — numai pentru mesajele de refuz (cantitatea „1.000 buc”).
    Intoarce liniile fisei cu sold cantitate/valoare/CMP dupa fiecare miscare.
    Ridica ValueError la iesire peste stoc."""
    cant = _d((stoc_initial or {}).get("cantitate", 0))
    val = _d((stoc_initial or {}).get("valoare", 0))
    out = []
    for m in miscari:
        c = _d(m["cantitate"])
        if c < 0 and m.get("anuleaza_id") and m["tip"] in ("intrare", "iesire"):
            # [retest 07.10 R1] STORNAREA ÎN ROȘU a unei mișcări (documentul ei a fost respins): aceeași mișcare cu semnul minus și
            # cu VALOAREA ei originală, nu la CMP-ul de acum. OMFP 1802/2014 pct.69: „Înregistrarea stornării unei operațiuni
            # contabile aferente exercițiului financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii
            # inițiale (stornare în roșu), fie prin înregistrarea inversă a acesteia (stornare în negru)”. CMP-ul se recalculează
            # din soldul rămas.
            v = _q(m["valoare"])
            if m["tip"] == "intrare":
                if cant + c < 0:
                    raise ValueError("Stornarea intrării de %s peste stocul de %s%s" % (_c(-c, um), _c(cant, um), _la(m.get("data"))))
                cant += c
                val += v
            else:
                cant -= c
                val -= v
            if cant == 0:
                val = Decimal("0.00")
            out.append({**m, "valoare": v, "sold_cantitate": cant, "sold_valoare": _q(val),
                        "cmp": _q4(val / cant) if cant > 0 else None})
            continue
        if m["tip"] == "ajustare":
            # [08.10.2026, decizia Costin §6 pct.2] DIFERENȚA DE PREȚ dintre NIR-ul „fără factură” și factura legată: o mișcare de
            # VALOARE (cantitate 0), în perioada facturii; CMP-ul se recalculează din soldul de după ea. Pe stoc zero nu are pe ce sta
            # (apelantul o duce atunci pe 607, nu în fișă).
            if c != 0:
                raise ValueError("Ajustarea de valoare%s nu poate avea cantitate (are %s): ea schimbă numai valoarea stocului" % (_la(m.get("data")), _c(c, um)))
            if cant <= 0:
                raise ValueError("Ajustarea de valoare nu are pe ce stoc să se aplice: stocul e zero%s" % _la(m.get("data")))
            v = _q(m["valoare"])
            val += v
            out.append({**m, "valoare": v, "sold_cantitate": cant, "sold_valoare": _q(val), "cmp": _q4(val / cant)})
            continue
        if c <= 0:
            raise ValueError("Cantitatea mișcării de stoc trebuie să fie mai mare ca zero (are %s%s)" % (_c(c, um), _la(m.get("data"))))
        if m["tip"] == "intrare":
            v = _q(c * _d(m["pret_unitar"]))
            cant += c
            val += v
        elif m["tip"] == "iesire":
            if c > cant:
                raise ValueError(mesaj_peste_stoc(c, cant, um, m.get("data")))
            cmp_curent = val / cant  # cant > 0 garantat de conditia de mai sus
            v = _q(c * cmp_curent)
            cant -= c
            val = _q(val - v) if cant > 0 else Decimal("0.00")
            if cant == 0:
                val = Decimal("0.00")
        else:
            raise ValueError("Tipul mișcării de stoc nu e cunoscut: %r" % m["tip"])
        out.append({**m, "valoare": _q(v), "sold_cantitate": cant,
                    "sold_valoare": _q(val),
                    "cmp": _q4(val / cant) if cant > 0 else None})
    return out


def valoare_iesire(miscari, stoc_initial, cantitate, um=""):
    """Valoarea unei iesiri noi de `cantitate`, la CMP-ul rezultat din istoric.
    Intoarce {cantitate, cmp, valoare, temei}. `um` numai pentru refuz („Ieșire de 1.000 buc peste stocul de 139 buc”)."""
    fisa = fisa_magazie(miscari, stoc_initial, um)
    if fisa:
        cant, val = fisa[-1]["sold_cantitate"], _d(fisa[-1]["sold_valoare"])
    else:
        cant = _d((stoc_initial or {}).get("cantitate", 0))
        val = _d((stoc_initial or {}).get("valoare", 0))
    c = _d(cantitate)
    if c <= 0:
        raise ValueError("Cantitatea ieșirii trebuie să fie mai mare ca zero (are %s)" % _c(c, um))
    if c > cant:
        raise ValueError(mesaj_peste_stoc(c, cant, um))
    cmp_curent = val / cant
    return {"cantitate": c, "cmp": _q4(cmp_curent), "valoare": _q(c * cmp_curent),
            "temei": TEMEI_CMP, "modul": MODUL, "reguli": REGULI}
