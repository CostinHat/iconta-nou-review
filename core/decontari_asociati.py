# -*- coding: utf-8 -*-
"""Decontari asociati (455/456/457/463) - motor PUR.
Surse: Legea 31/1990 art. 67 (dividende trimestriale), OMFP 3067/2018
(cont 463, pct. 423^1-423^2 OMFP 1802), impozit dividende 16% pentru
distribuiri incepand cu 01.01.2026 (Legea 141/2025; 10% anterior).
- dividende ANUALE: 1171=457 brut; impozit 457=446; plata net 457=5121;
- dividende INTERIMARE: 463=456 brut; impozit 456=446; plata net 456=5121;
  regularizare dupa aprobarea situatiilor anuale: 1171=457 + 457=463;
  exces (interimar > anual): NU se inregistreaza la regularizare; restituirea de la asociat (NETUL incasat) si
  impozitul recuperat de la buget se inregistreaza la INCASARE: 5121=463 (nota_restituire_dividend);
- imprumut DE LA asociat (4551): primire 5121=4551; restituire 4551=5121;
  dobanda 666=4551 + impozit 10% pe venitul din dobanda PF retinut 4551=446."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from core.common import nomenclator_cerut

B = Decimal("0.01")


def cota_dividend(la_data=None):
    """Cota impozit pe dividende (PROCENT), period-aware din common.COTE. Peticul 'if ref>=2026 else 10'
    (16/10) mutat in registru (PAS 0 versionare, regula 0a: eliminare, nu petic). Vezi common.COTE."""
    from core import common as _c
    return _c.cota("impozit_dividend", la_data)[0] * 100

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _imp(brut, cota):
    return (_d(brut) * cota / 100).quantize(B, rounding=ROUND_HALF_UP)

def nota_dividend(brut, la_data=None, interimar=False, cu_plata=True):
    """Repartizare + impozit + (optional) plata. Anual: 1171/457; interimar: 463/456."""
    b = _d(brut)
    if b <= 0:
        raise ValueError("Dividendul brut trebuie să fie un număr pozitiv.")
    cota = cota_dividend(la_data)
    imp = _imp(b, cota)
    net = b - imp
    if interimar:
        linii = [("463", "456", b), ("456", "446", imp)]
        if cu_plata:
            linii.append(("456", "5121", net))
    else:
        linii = [("1171", "457", b), ("457", "446", imp)]
        if cu_plata:
            linii.append(("457", "5121", net))
    return {"linii": linii, "impozit": imp, "net": net, "cota": str(cota)}

def nota_regularizare_interimar(total_interimar, dividend_anual_aprobat, impozit_interimar=None):
    """Dupa aprobarea situatiilor anuale: 1171=457 anual + compensare 457=463 (OMFP 1802/2014 pct.423^2).

    [Lot 19 defect 9, 03.10.2026] Excesul (interimar > anual) NU mai intra in nota de regularizare. Inainte, nota
    purta 5121=463 la BRUT, datata la aprobare: o incasare care nu avusese loc, si mai mare decat cea posibila —
    asociatul a primit NETUL, deci restituie netul. OMFP 1802/2014, functiunea contului 463 (introdusa prin OMFP
    3067/2018): „În creditul contului 463 ... se înregistrează: – suma dividendelor repartizate în cursul exercițiului
    financiar și regularizate pe seama dividendelor anuale (457); – sumele încasate reprezentând restituiri de
    dividende datorate, conform legii (512, 531).” Deci: credit 463 din 512 la INCASARE, cu suma incasata.

    Impozitul aferent excesului se calculeaza din impozitul EFECTIV retinut pe interimare (`impozit_interimar`),
    proportional cu excesul — nu cu cota datei de regularizare (cota se schimba intre ani: 10% 2025, 16% 2026).
    INTERPRETARE CU TEMEI: impozitul ramane in debitul 463 pana il restituie bugetul (CPF art.170^1 alin.(1):
    declaratie de regularizare/cerere de restituire „după restituirea de către asociați”), iar la incasare se
    inchide tot cu 5121=463 — singura corespondenta creditoare a lui 463 in afara de 457. Alternativa respinsa:
    446=463 (functiunea lui 446 nu are aceasta corespondenta debitoare). De reconfirmat daca apare o norma care
    transeaza inregistrarea creantei asupra bugetului."""
    ti, da = _d(total_interimar), _d(dividend_anual_aprobat)
    if ti <= 0 or da < 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    linii = [("1171", "457", da)] if da > 0 else []
    compensat = min(ti, da)
    if compensat > 0:
        linii.append(("457", "463", compensat))
    exces = ti - da if ti > da else Decimal("0.00")
    rez = {"linii": linii, "compensat": compensat, "exces_de_restituit": exces,
           "impozit_de_recuperat": Decimal("0.00"), "net_de_restituit": Decimal("0.00")}
    if exces > 0:
        # FORMĂ: fara impozitul retinut nu se poate spune cat restituie asociatul (netul) si cat bugetul
        if impozit_interimar in (None, ""):
            raise ValueError("Dividendele interimare depășesc dividendul anual cu %s lei: scrie impozitul reținut pe "
                             "dividendele interimare, ca să se știe cât restituie asociatul (netul) și cât se "
                             "recuperează de la buget." % exces)
        imp = _d(impozit_interimar)
        if imp < 0 or imp > ti:   # FORMĂ: impozitul nu poate fi negativ sau mai mare decat dividendul
            raise ValueError("Impozitul reținut pe dividendele interimare (%s) trebuie să fie între 0 și totalul "
                             "dividendelor interimare (%s)." % (imp, ti))
        rez["impozit_de_recuperat"] = (imp * exces / ti).quantize(B, rounding=ROUND_HALF_UP)
        rez["net_de_restituit"] = exces - rez["impozit_de_recuperat"]
    return rez


def nota_restituire_dividend(suma):
    """Restituire de dividende interimare INCASATA (de la asociat — netul; sau impozitul, de la buget): 5121=463, la
    data incasarii. OMFP 1802/2014, functiunea contului 463: credit 463 cu „sumele încasate reprezentând restituiri
    de dividende datorate, conform legii (512, 531)”."""
    s = _d(suma)
    if s <= 0:   # FORMĂ: suma incasata
        raise ValueError("Suma încasată trebuie să fie un număr pozitiv.")
    return {"linii": [("5121", "463", s)]}

def nota_imprumut_asociat(suma, operatie="primire", dobanda=0,
                          impozit_dobanda_pct=10):
    """4551: primire 5121=4551; restituire 4551=5121 (+ dobanda 666=4551,
    impozit retinut 4551=446)."""
    s = _d(suma)
    if s < 0 or (s == 0 and not dobanda):
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    if operatie == "primire":
        return {"linii": [("5121", "4551", s)]}
    if operatie == "restituire":
        linii = []
        if s > 0:
            linii.append(("4551", "5121", s))
        d = _d(dobanda)
        if d > 0:
            imp = _imp(d, Decimal(str(impozit_dobanda_pct)))
            linii.append(("666", "4551", d))
            if imp > 0:
                linii.append(("4551", "446", imp))
            linii.append(("4551", "5121", d - imp))
        return {"linii": linii}
    raise ValueError(nomenclator_cerut("operatie", "primire|restituire"))
