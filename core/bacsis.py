# -*- coding: utf-8 -*-
"""Bacsis HoReCa - motor PUR (Legea 376/2022 + art. 115 CF).
CAEN 5610 Restaurante / 5630 Baruri: bacsisul (0-15% sau suma fixa, ales de
client pe nota de plata) se evidentiaza DISTINCT pe bonul fiscal.
Fiscal: NU intra in baza TVA, NU se datoreaza CAS/CASS, NU se recalifica
salarial; impozit pe venit 10% (venit din alte surse) retinut la sursa la
distribuire, plata pana pe 25 a lunii urmatoare (D100), informativ D205.
Monografie (Bența): incasare 461 = 462 (bacsis de distribuit salariatilor);
5121/5311 = 461; impozit 462 = 446; plata net 462 = 5121/5311."""
from decimal import Decimal, ROUND_HALF_UP
from core import common as _c
from core.common import Temei

B = Decimal("0.01")
# [FiscalOS §2] Cota = CF art.64 alin.(1) lit.h) "alte surse"; bacsisul e venit din alte surse NUMAI prin
# OUG 28/1999 art.2^3 alin.(10) (Legea 376/2022, de la 01.01.2023) - Codul fiscal nu numeste bacsisul.
# [R3c, 11.10.2026] Cota se citește din registru (`impozit_venit_categorii`, la data notei); până atunci `COTA_IMPOZIT = 10` ancorat
# aici dubla aceeași prevedere cu `d212.COTA_IMPOZIT_VENIT`.
TEMEI_BACSIS_ALTE_SURSE = Temei(
    "OUG", 28, 1999, art="2^3", alin="10", data_in="2023-01-01", verificat_la="2026-10-01", de_cine="Code/FiscalOS", nivel_sursa="MO",
    url="anaf_surse/oug_28_1999.html",
    text_citat=("Sumele provenite din încasarea bacșișului de către salariați ca urmare a distribuirii "
                "prevăzute la alin. (8) sunt calificate ca venituri din alte surse"),
    lant_acte="art.2^3 introdus de Legea 376/2022 art.I pct.1, in vigoare 01.01.2023")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_incasare(bacsis, sursa="card"):
    """La bonul fiscal: 461=462 + incasare 5121 (card) / 5311 (numerar) = 461."""
    b = _d(bacsis)
    if b <= 0:
        # [R147] „bacsis invalid" nu spunea nici care câmp, nici ce e greșit cu el.
        raise ValueError("Bacșișul încasat trebuie să fie o sumă mai mare decât zero. "
                         "Dacă nu s-a încasat bacșiș, operațiunea nu se înregistrează.")
    cont = "5121" if sursa == "card" else "5311"
    return {"linii": [("461", "462", b), (cont, "461", b)]}

def nota_distribuire(bacsis_brut, la_data, sursa="banca"):
    """Retinere impozit (462=446) + plata net catre salariati (462=5121/5311). Cota = CF art.64 alin.(1) lit.h), din registru la data
    notei (`la_data`, obligatorie: o functie fiscala nu cade pe data curenta - `core/test_data_curenta.py`)."""
    b = _d(bacsis_brut)
    if b <= 0:
        # [R147] Aici e bacșișul BRUT, din care se reține impozitul — alt înțeles decât la
        # încasare, deci alt mesaj.
        raise ValueError("Bacșișul brut de distribuit trebuie să fie o sumă mai mare decât "
                         "zero: din el se reține impozitul înainte de plata către salariați.")
    cota, temei_cota = _c.cota("impozit_venit_categorii", _c._ca_data(la_data))
    imp = (b * cota).quantize(B, rounding=ROUND_HALF_UP)
    net = b - imp
    cont = "5121" if sursa == "banca" else "5311"
    # temeiul insoteste nota: cota (CF art.64 alin.1 lit.h) + calificarea bacsisului (OUG 28/1999 art.2^3 alin.10)
    return {"linii": [("462", "446", imp), ("462", cont, net)],
            "impozit": imp, "net": net, "cota": (cota * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP),
            "temei": [str(temei_cota) + " lit.h", str(TEMEI_BACSIS_ALTE_SURSE)]}
