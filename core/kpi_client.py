# -*- coding: utf-8 -*-
"""KPI client pentru portal: P&L, cash, creante, datorii din balanta cumulata."""


def _suma(randuri, prefixe, camp):
    """`camp` = o coloana a balantei, sau „cum_d”/„cum_c” = rulajul cumulat de la 1 ianuarie (`rulaje_cumulate`)."""
    from core.documente_api import rulaje_cumulate
    val = (lambda r: rulaje_cumulate(r, camp[-1])) if camp.startswith("cum_") else (lambda r: r[camp])
    return round(sum(val(r) for r in randuri
                     if any(str(r["cont"]).startswith(p) for p in prefixe)), 2)


def kpi_din_balanta(randuri):
    """randuri: iesirea din documente_api.balanta(). Cumulat de la inceputul anului."""
    venituri = _suma(randuri, ("7",), "cum_c") - _suma(randuri, ("7",), "cum_d")
    cheltuieli = _suma(randuri, ("6",), "cum_d") - _suma(randuri, ("6",), "cum_c")
    cash = _suma(randuri, ("531", "512"), "sf_d")
    de_incasat = _suma(randuri, ("411",), "sf_d")
    de_platit = _suma(randuri, ("401",), "sf_c")
    return {
        "venituri": round(venituri, 2),
        "cheltuieli": round(cheltuieli, 2),
        "profit": round(venituri - cheltuieli, 2),
        "cash": cash,
        "de_incasat": de_incasat,
        "de_platit": de_platit,
    }
