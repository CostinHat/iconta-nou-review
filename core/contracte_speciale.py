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
    """2018-01-01 .. 2019-04-30: DOAR impozit 10%% pe brut integral. Zilierii NU datorau CAS
    (exceptati explicit prin CF art.142 lit.t) si NU datoreaza CASS (nu-s in art.157). CAS pe zilieri
    a fost introdus abia de OUG 26/2019 (CF art.139(1) lit.s), in vigoare 01.05.2019."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("Salariul brut trebuie să fie un număr pozitiv.")
    impozit = _p(b, 10)
    return {"brut": b, "cas": Decimal("0.00"), "cass": Decimal("0.00"),
            "impozit": impozit, "net": b - impozit}


def _calcul_zilier_2019(brut):
    """De la 01.05.2019 (OUG 26/2019): impozit 10%% pe (brut - CAS) + CAS 25%%, fara CASS/CAM. Zilierii
    intra in baza CAS (CF art.139(1) lit.s + Legea 52/2011 art.9^1); exceptarea art.142 lit.t abrogata,
    ambele de OUG 26/2019 la 01.05.2019."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("Salariul brut trebuie să fie un număr pozitiv.")
    cas = _p(b, 25)
    impozit = _p(b - cas, 10)
    return {"brut": b, "cas": cas, "cass": Decimal("0.00"),
            "impozit": impozit, "net": b - cas - impozit}


# PERIOD-AWARE (verificat la sursa 03.08.2026, /tmp/cf.txt): CAS pe zilieri exista doar de la 01.05.2019
# (OUG 26/2019). Pana atunci = doar impozit 10%%. Aplicarea CAS retroactiv la 2018 era neconformitate.
_VARIANTE_CALCUL_ZILIER = [
    ("2019-05-01", _calcul_zilier_2019,
     c.Temei("OUG", 26, 2019, art="139", alin="1", lit="s", data_in="2019-05-01", nivel_sursa="REDARE",
             de_cine="Code+cercetare", verificat_la="2026-08-03",
             lant_acte="OUG 26/2019 (in vigoare 01.05.2019): zilieri in baza CAS (CF art.139(1) lit.s + Legea 52/2011 art.9^1); impozit 10% pe brut-CAS, fara CASS/CAM")),
    ("2018-01-01", _calcul_zilier_2018,
     c.Temei("Legea", 227, 2015, art="76", alin="2", lit="r", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code+cercetare", verificat_la="2026-08-03",
             lant_acte="pana la 01.05.2019: zilier = doar impozit 10% (venit asimilat salariilor CF art.76(2) lit.r); exceptat de CAS prin CF art.142 lit.t (abrogat de OUG 26/2019)")),
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
        raise ValueError("Salariul brut trebuie să fie un număr pozitiv.")
    cas = _p(b, 25)
    cass = _p(b, 10)
    impozit = _p(b - cas - cass, 10)
    return {"brut": b, "cas": cas, "cass": cass,
            "impozit": impozit, "net": b - cas - cass - impozit}

def remuneratie_minima_zilier(salariu_minim, ore=8, ore_luna=Decimal("165.33")):
    """Remuneratia zilnica minima = salariul minim orar x ore."""
    sm = _d(salariu_minim)
    if sm <= 0 or ore <= 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    orar = (sm / Decimal(str(ore_luna))).quantize(B, rounding=ROUND_HALF_UP)
    return {"orar_minim": orar, "zi_minima": (orar * ore).quantize(B)}

def nota(brut, fel="zilier", sursa="casa", la_data=None):
    """Nota completa: cheltuiala + retineri + plata net.

    `la_data` = DATA NOTEI. Fara ea, `calcul_zilier` cadea pe `date.today()`, deci o nota inregistrata
    azi pentru o luna trecuta primea varianta de formula de AZI — o cifra valida si falsa (interdictia
    **3**). Ruta care cheama functia avea deja data in cerere (`corp["data"]`, folosita pentru
    „luna deschisa") si n-o trimitea mai departe.

    Variabila locala s-a redenumit `rez`: se numea `c` si umbrea aliasul modulului `common`, deci
    normalizarea datei n-ar fi avut de unde sa fie chemata.
    """
    _ld = c._ca_data(la_data) if la_data else None
    if fel == "zilier":
        rez = calcul_zilier(brut, _ld)
        cont_ch = "641"
    elif fel in ("cenzor", "mandat"):
        rez = calcul_mandat(brut)   # fara varianta datata azi; cand va avea una, primeste `_ld`
        cont_ch = "621"
    else:
        raise ValueError("fel: zilier|cenzor|mandat")
    cont_bani = "5311" if sursa == "casa" else "5121"
    linii = [(cont_ch, "421", rez["brut"]), ("421", "4315", rez["cas"])]
    if rez["cass"] > 0:
        linii.append(("421", "4316", rez["cass"]))
    linii.append(("421", "444", rez["impozit"]))
    linii.append(("421", cont_bani, rez["net"]))
    return {"linii": linii, **rez}
