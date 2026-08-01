# -*- coding: utf-8 -*-
"""Contracte de munca speciale: zilieri, cenzori, mandat administrator - motor PUR.
Surse: Legea 52/2011 (zilieri) + art. 76(2) lit. g/i CF (mandat/cenzori =
venituri asimilate salariilor).
- ZILIERI: impozit 10% + CAS 25%, FARA CASS, FARA CAM (art. 9^1 L52/2011);
  impozit = 10% x (brut - CAS); declarare D112; remuneratia orara minima =
  salariul minim orar; max 90 zile/an la acelasi beneficiar (120 agricultura);
  nota: 641.zilieri = 421; CAS 421=4315; impozit 421=444; plata 421=5311/5121;
- CENZORI / MANDAT ADMINISTRATOR (fara CIM): CAS 25% + CASS 10% + impozit 10%
  aplicat la (brut - CAS - CASS); FARA CAM (nu exista raport de munca);
  nota: 621 = 421 (colaboratori) + retineri + plata."""
from decimal import Decimal, ROUND_HALF_UP

from core import common as c

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _p(baza, pct):
    return (_d(baza) * Decimal(str(pct)) / 100).quantize(B, rounding=ROUND_HALF_UP)

def _calcul_zilier_2018(brut):
    b = _d(brut)
    if b <= 0:
        raise ValueError("brut invalid")
    cas = _p(b, 25)
    impozit = _p(b - cas, 10)
    return {"brut": b, "cas": cas, "cass": Decimal("0.00"),
            "impozit": impozit, "net": b - cas - impozit}


_VARIANTE_CALCUL_ZILIER = [
    ("2018-01-01", _calcul_zilier_2018,
     c.Temei("Legea", 52, 2011, art="9^1", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def calcul_zilier(brut, la_data=None):
    """Taxe zilier (impozit 10% + CAS 25%, fara CASS/CAM), DISPECER pe la_data.
    TEMEI: Legea 52/2011 art.9^1 (zilieri: impozit 10% + CAS 25%, fara CASS/CAM); impozit pe (brut-CAS).
    nivel_sursa: REDARE. Versionata in timp: o schimbare de regim -> varianta datata noua, nu 'if data'."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_CALCUL_ZILIER, la_data or _dt.today())
    return fn(brut)

def calcul_mandat(brut):
    """Cenzor / administrator cu contract de mandat remunerat."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("brut invalid")
    cas = _p(b, 25)
    cass = _p(b, 10)
    impozit = _p(b - cas - cass, 10)
    return {"brut": b, "cas": cas, "cass": cass,
            "impozit": impozit, "net": b - cas - cass - impozit}

def remuneratie_minima_zilier(salariu_minim, ore=8, ore_luna=Decimal("165.33")):
    """Remuneratia zilnica minima = salariul minim orar x ore."""
    sm = _d(salariu_minim)
    if sm <= 0 or ore <= 0:
        raise ValueError("valori invalide")
    orar = (sm / Decimal(str(ore_luna))).quantize(B, rounding=ROUND_HALF_UP)
    return {"orar_minim": orar, "zi_minima": (orar * ore).quantize(B)}

def nota(brut, fel="zilier", sursa="casa"):
    """Nota completa: cheltuiala + retineri + plata net."""
    if fel == "zilier":
        c = calcul_zilier(brut)
        cont_ch = "641"
    elif fel in ("cenzor", "mandat"):
        c = calcul_mandat(brut)
        cont_ch = "621"
    else:
        raise ValueError("fel: zilier|cenzor|mandat")
    cont_bani = "5311" if sursa == "casa" else "5121"
    linii = [(cont_ch, "421", c["brut"]), ("421", "4315", c["cas"])]
    if c["cass"] > 0:
        linii.append(("421", "4316", c["cass"]))
    linii.append(("421", "444", c["impozit"]))
    linii.append(("421", cont_bani, c["net"]))
    return {"linii": linii, **c}
