# -*- coding: utf-8 -*-
"""Regim special agentii de turism (art. 311 CF) - motor PUR. Acopera:
- regim special (alin. 2-4): marja = incasat - costuri (cu TVA), suta marita;
  fara drept de deducere (alin. 6), fara TVA distinct pe factura (alin. 8);
- split UE/non-UE (alin. 5): partea din marja aferenta costurilor non-UE e scutita;
- regim normal (alin. 10-11): permis DOAR client PJ + toate componentele in RO;
  fiecare componenta la cota ei, baza include marja alocata;
- intermediar (alin. 9 + art. 286 al. 4 lit. e): baza = comisionul, TVA normal."""
from decimal import Decimal, ROUND_HALF_UP

from core import common as _cmn

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x))

def determina_regim(calitate_client, locuri, optiune_normal=False, intermediar=False):
    """calitate_client: 'PF'|'PJ'; locuri: lista din {'RO','UE','NONUE'}.
    Returneaza 'intermediar'|'normal'|'special'. Alin. 10: normal doar PJ + toate RO."""
    if intermediar:
        return "intermediar"
    if optiune_normal:
        if calitate_client != "PJ":
            raise ValueError("regim normal interzis: calator persoana fizica (art. 311 al. 10 lit. a)")
        if any(l != "RO" for l in locuri):
            raise ValueError("regim normal interzis: componente in afara Romaniei (art. 311 al. 10 lit. b)")
        return "normal"
    return "special"

def _marja_turism_special_2018(incasat, cost_ue, cost_non_ue=0, cota=21):
    """Marja = incasat - (cost_ue + cost_non_ue). Partea aferenta non-UE scutita
    proportional cu costurile (alin. 5). TVA suta marita pe marja taxabila."""
    inc, cue, cnon, c = _d(incasat), _d(cost_ue), _d(cost_non_ue), _d(cota)
    if inc <= 0 or cue < 0 or cnon < 0:
        raise ValueError("sume invalide")
    cost_total = cue + cnon
    marja = inc - cost_total
    if marja <= 0:
        return {"marja_bruta": marja.quantize(B), "marja_scutita": Decimal("0.00"),
                "marja_taxabila": Decimal("0.00"), "tva": Decimal("0.00"),
                "marja_neta": marja.quantize(B),
                "nota": "marja negativa/zero - fara TVA, se reporteaza in jurnalul special"}
    coef = (cnon / cost_total) if cost_total > 0 else Decimal("0")
    marja_scutita = (marja * coef).quantize(B, rounding=ROUND_HALF_UP)
    marja_taxabila = marja - marja_scutita
    tva = (marja_taxabila * c / (100 + c)).quantize(B, rounding=ROUND_HALF_UP)
    return {"marja_bruta": marja.quantize(B), "marja_scutita": marja_scutita,
            "marja_taxabila": marja_taxabila.quantize(B), "tva": tva,
            "marja_neta": (marja - tva).quantize(B), "nota": None}


_VARIANTE_MARJA_TURISM = [
    ("2018-01-01", _marja_turism_special_2018,
     _cmn.Temei("CF", art="311", data_in="2018-01-01", nivel_sursa="REDARE",
                de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def marja_turism_special(incasat, cost_ue, cost_non_ue=0, cota=21, la_data=None):
    """Regim special agentii de turism (marja + scutire proportionala non-UE), DISPECER pe la_data.
    Cota vine ca parametru (period-aware la apelant); dispecerul versioneaza FORMULA (suta marita + split
    UE/non-UE alin.5). TEMEI: CF art.311 (regim special agentii turism; alin.5 scutire non-UE; alin.2-4
    suta marita). nivel_sursa: REDARE. Versionata in timp: o schimbare a regulii -> varianta datata noua."""
    from datetime import date as _dt
    fn, _ = _cmn.alege_varianta(_VARIANTE_MARJA_TURISM, la_data or _dt.today())
    return fn(incasat, cost_ue, cost_non_ue, cota)

def marja_turism_normal(componente):
    """componente: [{descriere?, baza, cota}] - baza include marja alocata (alin. 11).
    Returneaza TVA per componenta + totaluri. Agentia are drept de deducere pe achizitii."""
    if not componente:
        raise ValueError("lista componente goala")
    out, tb, tt = [], Decimal("0"), Decimal("0")
    for comp in componente:
        baza, c = _d(comp["baza"]), _d(comp.get("cota", 21))
        if baza <= 0 or c < 0:
            raise ValueError("componenta invalida")
        tva = (baza * c / 100).quantize(B, rounding=ROUND_HALF_UP)
        out.append({"descriere": comp.get("descriere", ""), "baza": baza.quantize(B),
                    "cota": c, "tva": tva})
        tb += baza; tt += tva
    return {"componente": out, "total_baza": tb.quantize(B), "total_tva": tt.quantize(B),
            "total_factura": (tb + tt).quantize(B)}

def comision_intermediar(comision, cota=21, tva_inclus=False):
    """Intermediar (alin. 9): baza = comisionul. Sumele colectate in numele tertilor
    nu sunt venit (OMFP 1802 pct. 432)."""
    com, c = _d(comision), _d(cota)
    if com <= 0:
        raise ValueError("comision invalid")
    if tva_inclus:
        tva = (com * c / (100 + c)).quantize(B, rounding=ROUND_HALF_UP)
        baza = com - tva
    else:
        baza = com
        tva = (com * c / 100).quantize(B, rounding=ROUND_HALF_UP)
    return {"baza": baza.quantize(B), "tva": tva, "total": (baza + tva).quantize(B)}
