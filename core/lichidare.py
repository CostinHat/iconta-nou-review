# -*- coding: utf-8 -*-
"""Lichidare/radiere societate - motor PUR (OMFP 897/2015 + L31/1990 art. 227+
+ L85/2014; impozit pe castigul din lichidare = regim dividende, 16% din 2026).
Etape dupa aprobarea lichidarii:
1. valorificare active: vanzare 461 = 7583 + 4427, descarcare 6583 + 28xx = 21x,
   stocuri 4111 = 707 + 4427 si 607 = 371; incasare creante; plata datorii;
2. inchidere TVA/impozite curente; rezultatul lichidarii pe 121;
3. PARTAJ (dupa bilantul de lichidare):
   - restituire capital social: 1012 = 456 (neimpozabil la asociat);
   - rezerve/profituri: 106x/117x/121 = 456 - CASTIG impozabil la asociat
     cu cota de dividend (16% din 2026): 456 = 446;
   - rezerva legala 1061 dedusa fiscal se impoziteaza si la firma (16% profit);
   - plata neta: 456 = 5121."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _cota_dividend(la_data=None):
    """Cota impozit pe castigul din lichidare = regim dividende (PROCENT), period-aware din common.COTE.
    Peticul 16/10 mutat in registru (PAS 0 versionare)."""
    from core import common as _c
    return _c.cota("impozit_dividend", la_data)[0] * 100

def nota_vanzare_activ(pret, valoare_bruta, amortizare_cumulata,
                       cont_imobilizare="2131", cont_amortizare="2813", cota_tva=21):
    """Vanzare in lichidare: 461=7583+4427 + descarcare 6583+28xx=21x."""
    p, vb, am = _d(pret), _d(valoare_bruta), _d(amortizare_cumulata)
    if p <= 0 or vb <= 0 or am < 0 or am > vb:
        raise ValueError("valori invalide")
    tva = (p * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    linii = [("461", "7583", p)]
    if tva > 0:
        linii.append(("461", "4427", tva))
    if am > 0:
        linii.append((cont_amortizare, cont_imobilizare, am))
    if vb - am > 0:
        linii.append(("6583", cont_imobilizare, vb - am))
    return {"linii": linii, "tva": tva}

def partaj(capital_social, rezerve=0, profituri=0, la_data=None):
    """Partajul final: capitalul = neimpozabil; rezerve+profituri = castig
    impozabil cu cota de dividend. Returneaza liniile + impozitul."""
    cs, rz, pf = _d(capital_social), _d(rezerve), _d(profituri)
    if cs < 0 or rz < 0 or pf < 0 or (cs + rz + pf) <= 0:
        raise ValueError("valori invalide")
    cota = _cota_dividend(la_data)
    castig = rz + pf
    impozit = (castig * cota / 100).quantize(B, rounding=ROUND_HALF_UP)
    linii = []
    if cs > 0:
        linii.append(("1012", "456", cs))
    if rz > 0:
        linii.append(("1061", "456", rz))
    if pf > 0:
        linii.append(("1171", "456", pf))
    if impozit > 0:
        linii.append(("456", "446", impozit))
    net = cs + castig - impozit
    linii.append(("456", "5121", net))
    return {"linii": linii, "castig_impozabil": castig, "impozit": impozit,
            "net_asociat": net, "cota": str(cota)}
