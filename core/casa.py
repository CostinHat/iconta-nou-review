"""
core/casa.py — casierie + avansuri de trezorerie. Calcul PUR, fără DB.
Generație nouă: contract de justificare + cote cu valabilitate + note cu urmă.

Surse oficiale (verificate):
- Plafoane numerar: Legea 70/2015 (actualizată Legea 239/2025, în vigoare 01.01.2026)
- Plan de conturi + monografii: OMFP 1802/2014
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date
from decimal import Decimal

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "casa"

# Plafoane care nu sunt încă în common.COTE (specifice casei) — cu temei.
PLAFON_SOLD_ZI_CC = Decimal("500000")      # cash & carry / super / hiper
PLAFON_INCASARE_PJ = Decimal("5000")
PLAFON_INCASARE_PJ_CC = Decimal("10000")
PLAFON_PLATA_PJ = Decimal("5000")
PLAFON_PLATA_PJ_TOTAL = Decimal("10000")
PLAFON_PF = Decimal("10000")


def _urma(temei=None):
    """Eticheta care însoțește fiecare notă: de unde a ieșit cifra."""
    u = {"modul": MODUL, "reguli": REGULI}
    if temei:
        u["temei"] = temei
    return u


def _stoc_initial(x):
    return _dec(x)


# ============================================================
#  REGISTRU DE CASĂ — sold rulant
# ============================================================
def registru_casa(operatiuni, sold_initial=0):
    sold = _dec(sold_initial)
    out = []
    for op in operatiuni:
        suma = _dec(op["suma"])
        if op["tip"] == "incasare":
            sold += suma
        elif op["tip"] == "plata":
            sold -= suma
        else:
            raise ValueError(f"tip necunoscut: {op['tip']!r}")
        out.append({**op, "sold": _q(sold)})
    return out


def sold_final(operatiuni, sold_initial=0):
    reg = registru_casa(operatiuni, sold_initial)
    return reg[-1]["sold"] if reg else _q(sold_initial)


# ============================================================
#  VERIFICARE PLAFOANE — întoarce PROBLEME cu justificare, nu liste seci
# ============================================================
def verifica_plafon(operatiuni, sold_initial=0, cash_and_carry=False, la_data=None):
    """
    Întoarce listă de probleme (common.problema): fiecare cu cod/mesaj/temei/nivel.
    Plafoanele numerar sunt AVERTISMENT (legale, dar risc la control), nu blocante.
    """
    probleme = []
    plafon_sold_std, temei_sold = c.cota("plafon_sold_casa", la_data)
    plafon_sold = PLAFON_SOLD_ZI_CC if cash_and_carry else plafon_sold_std
    plafon_inc_pj = PLAFON_INCASARE_PJ_CC if cash_and_carry else PLAFON_INCASARE_PJ
    plafon_avans, temei_avans = c.cota("plafon_avans_decontare", la_data)

    # sold la sfârșitul fiecărei zile
    sold_zi = {}
    for r in registru_casa(operatiuni, sold_initial):
        sold_zi[r["data"]] = r["sold"]
    for zi, s in sold_zi.items():
        if s > plafon_sold:
            probleme.append(c.problema("PLAFON_SOLD_CASA", nivel=c.AVERTISMENT,
                                       zi=zi, gasit=_q(s), asteptat=_q(plafon_sold)))

    # agregate pe zi / partener
    zile = defaultdict(list)
    for op in operatiuni:
        zile[op["data"]].append(op)

    for zi, ops in zile.items():
        inc_pj = defaultdict(Decimal)
        plata_pj = defaultdict(Decimal)
        plata_pj_total = Decimal(0)
        pf_inc = defaultdict(Decimal)
        pf_plata = defaultdict(Decimal)
        avans = defaultdict(Decimal)

        for op in ops:
            scop = op.get("scop", "")
            if scop in ("ridicare_banca", "depunere_banca"):
                continue
            suma = _dec(op["suma"])
            part = op.get("partener", "?")
            if scop == "avans":
                if op["tip"] == "plata":
                    avans[part] += suma
                continue
            if op.get("partener_tip", "pj") == "pf":
                (pf_inc if op["tip"] == "incasare" else pf_plata)[part] += suma
            else:
                if op["tip"] == "incasare":
                    inc_pj[part] += suma
                else:
                    plata_pj[part] += suma
                    plata_pj_total += suma

        for p, s in inc_pj.items():
            if s > plafon_inc_pj:
                probleme.append(c.problema("PLAFON_INCASARE_PJ", nivel=c.AVERTISMENT,
                                           partener=p, gasit=_q(s), asteptat=_q(plafon_inc_pj)))
        for p, s in plata_pj.items():
            if s > PLAFON_PLATA_PJ:
                probleme.append(c.problema("PLAFON_PLATA_PJ", nivel=c.AVERTISMENT,
                                           partener=p, gasit=_q(s), asteptat=_q(PLAFON_PLATA_PJ)))
        if plata_pj_total > PLAFON_PLATA_PJ_TOTAL:
            probleme.append(c.problema("PLAFON_PLATA_PJ_TOTAL", nivel=c.AVERTISMENT,
                                       zi=zi, gasit=_q(plata_pj_total), asteptat=_q(PLAFON_PLATA_PJ_TOTAL)))
        for p, s in pf_inc.items():
            if s > PLAFON_PF:
                probleme.append(c.problema("PLAFON_PF", nivel=c.AVERTISMENT,
                                           partener=p, gasit=_q(s), asteptat=_q(PLAFON_PF)))
        for p, s in pf_plata.items():
            if s > PLAFON_PF:
                probleme.append(c.problema("PLAFON_PF", nivel=c.AVERTISMENT,
                                           partener=p, gasit=_q(s), asteptat=_q(PLAFON_PF)))
        for p, s in avans.items():
            if s > plafon_avans:
                probleme.append(c.problema("PLAFON_AVANS", nivel=c.AVERTISMENT,
                                           partener=p, gasit=_q(s), asteptat=_q(plafon_avans)))
    return probleme


# ============================================================
#  MONOGRAFII CASĂ — note cu urmă
# ============================================================
def _nota(debit, credit, suma, temei=None):
    return {"debit": debit, "credit": credit, "suma": _q(suma), **_urma(temei)}


def regula_cont_casa(op):
    scop = op.get("scop", "")
    tip = op["tip"]
    suma = _q(op["suma"])
    casa = "5314" if op.get("valuta") else "5311"
    banca = "5124" if op.get("valuta") else "5121"

    if scop == "client" and tip == "incasare":
        return _nota(casa, "4111", suma)
    if scop == "furnizor" and tip == "plata":
        return _nota("401", casa, suma)
    if scop == "ridicare_banca":
        return [_nota(casa, "581", suma), _nota("581", banca, suma)]
    if scop == "depunere_banca":
        return [_nota("581", casa, suma), _nota(banca, "581", suma)]
    raise ValueError(f"scop/tip nesuportat: scop={scop!r} tip={tip!r}")


# ============================================================
#  AVANSURI DE TREZORERIE (cont 542)
# ============================================================
def avans_acordare(suma, valuta=False):
    return _nota("542", "5314" if valuta else "5311", suma)


def avans_restituire(suma, valuta=False):
    return _nota("5314" if valuta else "5311", "542", suma)


def avans_deconteaza(avans, linii):
    note = []
    decontat = Decimal(0)
    for l in linii:
        baza = _dec(l["suma"])
        note.append(_nota(l["cont"], "542", baza))
        decontat += baza
        if l.get("tva"):
            tva = _dec(l["tva"])
            note.append(_nota("4426", "542", tva))
            decontat += tva
    rest = _dec(avans) - decontat
    return {"note": note, "decontat": _q(decontat), "rest_de_restituit": _q(rest)}


def avans_sold(miscari):
    sold = defaultdict(Decimal)
    for m in miscari:
        s = _dec(m["suma"])
        if m["tip"] == "acordare":
            sold[m["persoana"]] += s
        elif m["tip"] in ("decontare", "restituire"):
            sold[m["persoana"]] -= s
        else:
            raise ValueError(f"tip mișcare necunoscut: {m['tip']!r}")
    return {p: _q(s) for p, s in sold.items()}


def reclasificare_bilant(avansuri_nedecontate):
    note = []
    for a in avansuri_nedecontate:
        cont = "4282" if a["tip"] == "personal" else "461"
        note.append(_nota(cont, "542", a["suma"],
                          temei="OMFP 1802/2014 pct. 302/306"))
    return note
