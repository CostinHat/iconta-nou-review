# -*- coding: utf-8 -*-
"""Deconturi de deplasare si diurna - motor PUR.
Surse: art. 76(2)k + (4^1) CF, HG 714/2018 (intern 23 lei/zi bugetar),
HG 518/1995 (extern per tara, ex. 35 EUR).
Plafon neimpozabil pe zi = min(2,5 x diurna bugetara;
3 x salariu_baza / zile_lucratoare_luna). Excedentul = venit salarial
(impozit + CAS + CASS, se declara in D112 rd. 8.2.1).
Contabil: avans spre decontare 542 = 5311/5121; decont: 625 = 542
(diurna + transport + cazare pe justificative); diferenta restituita
5311 = 542; diurna impozabila trece prin stat (641)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
DIURNA_INTERNA_BUGETAR = Decimal("23")  # HG 714/2018 (Ordinul 1235/2023)

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def plafon_diurna(diurna_acordata_pe_zi, zile, salariu_baza, zile_lucratoare_luna,
                  diurna_bugetara=None, curs=1):
    """Returneaza {plafon_zi, neimpozabil, impozabil}. diurna_bugetara: 23 lei
    intern (implicit) sau valoarea HG 518/1995 pt. tara (in valuta, cu curs)."""
    da, sb = _d(diurna_acordata_pe_zi), _d(salariu_baza)
    z, zl = int(zile), int(zile_lucratoare_luna)
    if da <= 0 or z <= 0 or sb <= 0 or zl <= 0:
        raise ValueError("valori invalide")
    bug = _d(diurna_bugetara if diurna_bugetara is not None else DIURNA_INTERNA_BUGETAR)
    p1 = (bug * Decimal("2.5") * Decimal(str(curs))).quantize(B, rounding=ROUND_HALF_UP)
    p2 = (sb * 3 / zl).quantize(B, rounding=ROUND_HALF_UP)
    plafon_zi = min(p1, p2)
    total = (da * z).quantize(B)
    neimp = (min(da, plafon_zi) * z).quantize(B)
    return {"plafon_zi": plafon_zi, "limita_2_5x": p1, "limita_3_salarii": p2,
            "total_acordat": total, "neimpozabil": neimp,
            "impozabil": total - neimp}

def nota_avans(suma, sursa="casa"):
    """Avans spre decontare: 542 = 5311/5121."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    return {"linii": [("542", "5311" if sursa == "casa" else "5121", s)]}

def nota_decont(avans, diurna=0, transport=0, cazare=0, cota_tva=0, sursa="casa"):
    """Decont: 625 = 542 (+4426 pe cazare/transport cu factura daca cota>0);
    diferenta: daca cheltuieli < avans -> restituire rest; daca > -> plata diferentei."""
    av = _d(avans)
    d, t, c = _d(diurna), _d(transport), _d(cazare)
    if av < 0 or d < 0 or t < 0 or c < 0 or (d + t + c) <= 0:
        raise ValueError("valori invalide")
    cont_banii = "5311" if sursa == "casa" else "5121"
    tva = (Decimal(str(cota_tva)) / 100 * (t + c)).quantize(B, rounding=ROUND_HALF_UP)
    total = d + t + c + tva
    linii = [("625", "542", d + t + c)]
    if tva > 0:
        linii.append(("4426", "542", tva))
    dif = av - total
    if dif > 0:
        linii.append((cont_banii, "542", dif))       # restituire rest
    elif dif < 0:
        linii.append(("542", cont_banii, -dif))      # plata diferentei
    return {"linii": linii, "total_cheltuieli": total, "diferenta": dif}
