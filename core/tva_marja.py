# -*- coding: utf-8 -*-
"""Regim special marja (art. 312 CF, norme pct. 86) - motor PUR.
Marja = pret vanzare - pret cumparare; TVA = marja x cota/(100+cota) (suta marita);
marja negativa -> TVA 0 (se reporteaza in jurnalul special). Pe factura NU se
inscrie TVA distinct; mentiune "regimul marjei - bunuri second-hand"."""
from decimal import Decimal, ROUND_HALF_UP

from core import common as _cmn

def _vanzare_marja_2018(pret_vanzare, pret_cumparare, cota=21):
    pv = Decimal(str(pret_vanzare))
    pc = Decimal(str(pret_cumparare))
    c = Decimal(str(cota))
    if pv <= 0 or pc < 0:
        raise ValueError("preturi invalide")
    marja = pv - pc
    if marja <= 0:
        return {"marja_bruta": marja.quantize(Decimal("0.01")), "tva": Decimal("0.00"),
                "marja_neta": marja.quantize(Decimal("0.01")),
                "nota": "marja negativa/zero - fara TVA, se reporteaza in jurnalul special"}
    tva = (marja * c / (100 + c)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"marja_bruta": marja.quantize(Decimal("0.01")), "tva": tva,
            "marja_neta": (marja - tva).quantize(Decimal("0.01")), "nota": None}


_VARIANTE_VANZARE_MARJA = [
    ("2018-01-01", _vanzare_marja_2018,
     _cmn.Temei("CF", art="312", data_in="2018-01-01", nivel_sursa="REDARE",
                de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def vanzare_marja(pret_vanzare, pret_cumparare, cota=21, la_data=None):
    """Regim special marja (suta marita pe marja, marja negativa -> TVA 0), DISPECER pe la_data.
    Cota vine ca parametru (period-aware la apelant); DISPECERUL versioneaza FORMULA regimului marjei.
    TEMEI: CF art.312 (regim special marja bunuri second-hand; norme pct.86). nivel_sursa: REDARE.
    Versionata in timp: o schimbare a regulii regimului -> varianta datata noua, nu 'if data' in corp."""
    from datetime import date as _dt
    fn, _ = _cmn.alege_varianta(_VARIANTE_VANZARE_MARJA, la_data or _dt.today())
    return fn(pret_vanzare, pret_cumparare, cota)
