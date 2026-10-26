# -*- coding: utf-8 -*-
"""KPI client pentru portal: P&L, cash, creante, datorii din balanta cumulata.

[lotul 13, deficiența 553, comanda Costin 13.1] „Profit −6.075 lei — la rezultat negativ clientul citește «Pierdere» (și e înainte de
impozit).” Rezultatul e acum cel ÎNAINTE de impozit, ca în pachetul lunar (`motor.rezultat`, lot 06.10 pct.15: „Cifra numită «profit» e
profitul înainte de impozit”): grupa 69 („Cheltuieli cu impozitul pe profit și alte impozite”, OMFP 1802/2014) și 79 nu intră în venituri
și cheltuieli — aceeași listă, `motor.GRUPE_IMPOZIT`, nu a doua. `tip` spune felul rezultatului (profit / pierdere / neutru), ca ecranul
să scrie cuvântul, nu un minus.
"""
from core.motor import GRUPE_IMPOZIT


def _suma(randuri, prefixe, camp, fara=()):
    """`camp` = o coloana a balantei, sau „cum_d”/„cum_c” = rulajul cumulat de la 1 ianuarie (`rulaje_cumulate`)."""
    from core.documente_api import rulaje_cumulate
    val = (lambda r: rulaje_cumulate(r, camp[-1])) if camp.startswith("cum_") else (lambda r: r[camp])
    return round(sum(val(r) for r in randuri  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
                     if any(str(r["cont"]).startswith(p) for p in prefixe) and not str(r["cont"]).startswith(tuple(fara))), 2)


def kpi_din_balanta(randuri):
    """randuri: iesirea din documente_api.balanta(). Cumulat de la inceputul anului."""
    venituri = _suma(randuri, ("7",), "cum_c", GRUPE_IMPOZIT) - _suma(randuri, ("7",), "cum_d", GRUPE_IMPOZIT)
    cheltuieli = _suma(randuri, ("6",), "cum_d", GRUPE_IMPOZIT) - _suma(randuri, ("6",), "cum_c", GRUPE_IMPOZIT)
    cash = _suma(randuri, ("531", "512"), "sf_d")
    de_incasat = _suma(randuri, ("411",), "sf_d")
    de_platit = _suma(randuri, ("401",), "sf_c")
    profit = round(venituri - cheltuieli, 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    return {
        "venituri": round(venituri, 2),  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
        "cheltuieli": round(cheltuieli, 2),  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
        "profit": profit,   # rezultatul ÎNAINTE de impozit (numele cheii rămâne, cititorii existenți)
        "tip": "profit" if profit > 0 else ("pierdere" if profit < 0 else "neutru"),
        "cash": cash,
        "de_incasat": de_incasat,
        "de_platit": de_platit,
    }
