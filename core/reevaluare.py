# -*- coding: utf-8 -*-
"""Reevaluare imobilizari (cont 105) - motor PUR (OMFP 1802/2014 pct. 111-116).
Metoda valorii nete: amortizarea cumulata se ELIMINA din valoarea bruta
(28xx = 21x), apoi diferenta pana la valoarea justa:
- CRESTERE: 21x = 105; daca exista pierdere anterioara trecuta pe 655,
  intai 21x = 755 pana la nivelul ei, restul pe 105 (pct. 113);
- SCADERE: intai 105 = 21x pana la soldul rezervei din reevaluare pentru
  acel activ, restul 655 = 21x (pct. 114).
Surplusul realizat se transfera 105 = 1175 la cedare/casare (pct. 109-110)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_reevaluare(valoare_bruta, amortizare_cumulata, valoare_justa,
                    cont_imobilizare, cont_amortizare,
                    sold_105_activ=0, pierdere_655_anterioara=0):
    """Returneaza liniile notei + detalii. valoare_neta = bruta - amortizare."""
    vb, am, vj = _d(valoare_bruta), _d(amortizare_cumulata), _d(valoare_justa)
    s105, p655 = _d(sold_105_activ), _d(pierdere_655_anterioara)
    if vb <= 0 or am < 0 or am > vb or vj < 0:
        raise ValueError("valori invalide")
    vn = vb - am
    linii = []
    if am > 0:  # eliminarea amortizarii cumulate (metoda valorii nete)
        linii.append((cont_amortizare, cont_imobilizare, am))
    dif = vj - vn
    detaliu = {"valoare_neta": vn, "diferenta": dif}
    if dif > 0:
        pe_755 = min(dif, p655)
        pe_105 = dif - pe_755
        if pe_755 > 0:
            linii.append((cont_imobilizare, "755", pe_755))
        if pe_105 > 0:
            linii.append((cont_imobilizare, "105", pe_105))
        detaliu.update({"pe_755": pe_755, "pe_105": pe_105})
    elif dif < 0:
        scadere = -dif
        din_105 = min(scadere, s105)
        pe_655 = scadere - din_105
        if din_105 > 0:
            linii.append(("105", cont_imobilizare, din_105))
        if pe_655 > 0:
            linii.append(("655", cont_imobilizare, pe_655))
        detaliu.update({"din_105": din_105, "pe_655": pe_655})
    return {"linii": linii, **detaliu}

def nota_realizare_surplus(suma):
    """Transfer surplus realizat: 105 = 1175 (la cedare sau pe masura amortizarii)."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    return {"linii": [("105", "1175", s)]}
