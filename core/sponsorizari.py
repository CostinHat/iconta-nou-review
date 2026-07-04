# -*- coding: utf-8 -*-
"""Sponsorizari si redirectionare impozit - motor PUR.
Surse: art. 25(4)i CF + Legea 32/1994 + Ordinul ANAF 3562/2024 (D177).
- cheltuiala NEDEDUCTIBILA (6582), dar credit fiscal la impozit pe PROFIT:
  min(0,75% x cifra de afaceri; 20% x impozitul pe profit datorat);
  conditie: beneficiar inscris in Registrul entitatilor/unitatilor de cult
  la data incheierii contractului;
- diferenta neutilizata din plafon -> redirectionare prin D177 pana la
  termenul de depunere D101; fara report (eliminat din 2022; sumele
  2015-2021 utilizabile pana in 2028);
- MICROINTREPRINDERI: facilitatea ELIMINATA (OUG 115/2023) - sponsorizarea
  ramane simpla cheltuiala, fara credit fiscal si fara D177;
- nota contabila: 6582 = 401 (contract) / 5121 (plata directa) / 3xx (in natura)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def plafon_credit(cifra_afaceri, impozit_profit):
    """min(0,75% x CA; 20% x impozit)."""
    ca, ip = _d(cifra_afaceri), _d(impozit_profit)
    if ca < 0 or ip < 0:
        raise ValueError("valori invalide")
    p1 = (ca * Decimal("0.0075")).quantize(B, rounding=ROUND_HALF_UP)
    p2 = (ip * Decimal("0.20")).quantize(B, rounding=ROUND_HALF_UP)
    return {"limita_ca": p1, "limita_impozit": p2, "plafon": min(p1, p2)}

def credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate,
                        tip_impozit="profit", beneficiar_in_registru=True):
    """Creditul fiscal utilizabil + suma redirectionabila prin D177."""
    if tip_impozit == "micro":
        return {"credit": Decimal("0.00"), "redirectionabil_d177": Decimal("0.00"),
                "plafon": Decimal("0.00"),
                "nota": "microintreprinderi: facilitate eliminata (OUG 115/2023) - "
                        "sponsorizarea ramane cheltuiala fara credit fiscal"}
    if not beneficiar_in_registru:
        return {"credit": Decimal("0.00"), "redirectionabil_d177": Decimal("0.00"),
                "plafon": plafon_credit(cifra_afaceri, impozit_profit)["plafon"],
                "nota": "beneficiar NEINSCRIS in Registrul entitatilor la data "
                        "contractului - fara credit fiscal (art. 25(4^1))"}
    p = plafon_credit(cifra_afaceri, impozit_profit)
    sp = _d(sponsorizari_efectuate)
    credit = min(sp, p["plafon"])
    redir = p["plafon"] - credit
    return {"credit": credit, "redirectionabil_d177": redir, "plafon": p["plafon"],
            "limita_ca": p["limita_ca"], "limita_impozit": p["limita_impozit"],
            "nota": "restul de plafon se poate redirectiona prin D177 pana la "
                    "termenul D101 (Ordin ANAF 3562/2024)"}

def nota_sponsorizare(suma, mod="contract"):
    """6582 = 401 (contract, plata ulterioara) | 5121 (plata directa)."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    cont = {"contract": "401", "plata": "5121"}.get(mod)
    if not cont:
        raise ValueError("mod: contract|plata")
    return {"linii": [("6582", cont, s)]}
