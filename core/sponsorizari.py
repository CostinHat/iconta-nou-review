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

from core import common as c

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _plafon_credit_2018(cifra_afaceri, impozit_profit):
    """min(0,75% x CA; 20% x impozit)."""
    ca, ip = _d(cifra_afaceri), _d(impozit_profit)
    if ca < 0 or ip < 0:
        raise ValueError("valori invalide")
    p1 = (ca * Decimal("0.0075")).quantize(B, rounding=ROUND_HALF_UP)
    p2 = (ip * Decimal("0.20")).quantize(B, rounding=ROUND_HALF_UP)
    return {"limita_ca": p1, "limita_impozit": p2, "plafon": min(p1, p2)}


_VARIANTE_PLAFON_CREDIT = [
    ("2018-01-01", _plafon_credit_2018,
     c.Temei("CF", art="25", alin="4", lit="i", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31")),
]


def plafon_credit(cifra_afaceri, impozit_profit, la_data=None):
    """Plafonul creditului de sponsorizare, DISPECER pe la_data.
    TEMEI: CF art.25 alin.(4) lit.i (credit = min 0,75% cifra afaceri; 20% impozit profit). nivel_sursa:
    REDARE. Versionata in timp: o schimbare de procent/plafon -> varianta datata noua, nu 'if data'."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_PLAFON_CREDIT, la_data or _dt.today())
    return fn(cifra_afaceri, impozit_profit)


def _credit_sponsorizare_2018(cifra_afaceri, impozit_profit, sponsorizari_efectuate,
                        tip_impozit="profit", beneficiar_in_registru=True, la_data=None):
    """Creditul fiscal utilizabil + suma redirectionabila prin D177."""
    if tip_impozit == "micro":
        # Micro-sponsorizare: credit = 20%% din impozitul micro (CF fostul art.56 alin.1^1),
        # VALABIL 01.04.2019 (Legea 30/2019, forma 20%%+Registru; introdus OUG 25/2018) - 31.12.2023
        # (ABROGAT OUG 115/2023, ultimul an fiscal 2023). Verificat la sursa 03.08.2026:
        # anaf_surse/cf_art56_alin15_istoric_micro_sponsorizare.txt. Redirectionabil in 6 luni.
        from datetime import date as _dt
        _ref = la_data or _dt.today()
        if _ref < _dt(2019, 4, 1) or _ref > _dt(2023, 12, 31):
            return {"credit": Decimal("0.00"), "redirectionabil_d177": Decimal("0.00"),
                    "plafon": Decimal("0.00"),
                    "nota": "micro: credit de sponsorizare valabil DOAR 01.04.2019-31.12.2023 "
                            "(art.56 alin.1^1, abrogat OUG 115/2023) - in rest doar cheltuiala"}
        plafon_m = _d(_d(impozit_profit) * Decimal("0.20"))
        if not beneficiar_in_registru:
            return {"credit": Decimal("0.00"), "redirectionabil_d177": Decimal("0.00"), "plafon": plafon_m,
                    "nota": "micro: beneficiar NEINSCRIS in Registrul entitatilor la data contractului "
                            "(art.25 alin.4^1) - fara credit fiscal"}
        sp_m = _d(sponsorizari_efectuate)
        credit_m = min(sp_m, plafon_m)
        return {"credit": credit_m, "redirectionabil_d177": plafon_m - credit_m, "plafon": plafon_m,
                "nota": "micro: credit 20%% din impozitul micro (art.56 alin.1^1), rest redirectionabil "
                        "6 luni; valabil 2019-2023"}
    if not beneficiar_in_registru:
        return {"credit": Decimal("0.00"), "redirectionabil_d177": Decimal("0.00"),
                "plafon": plafon_credit(cifra_afaceri, impozit_profit, la_data=la_data)["plafon"],
                "nota": "beneficiar NEINSCRIS in Registrul entitatilor la data "
                        "contractului - fara credit fiscal (art. 25(4^1))"}
    p = plafon_credit(cifra_afaceri, impozit_profit, la_data=la_data)
    sp = _d(sponsorizari_efectuate)
    credit = min(sp, p["plafon"])
    redir = p["plafon"] - credit
    return {"credit": credit, "redirectionabil_d177": redir, "plafon": p["plafon"],
            "limita_ca": p["limita_ca"], "limita_impozit": p["limita_impozit"],
            "nota": "restul de plafon se poate redirectiona prin D177 pana la "
                    "termenul D101 (Ordin ANAF 3562/2024)"}


_VARIANTE_CREDIT_SPONSORIZARE = [
    ("2018-01-01", _credit_sponsorizare_2018,
     c.Temei("CF", art="25", alin="4", lit="i", data_in="2018-01-01", nivel_sursa="REDARE",
             de_cine="Code/Costin", verificat_la="2026-07-31",
             lant_acte="OUG 115/2023 (micro: facilitate eliminata); Ordin ANAF 3562/2024 (D177)")),
]


def credit_sponsorizare(cifra_afaceri, impozit_profit, sponsorizari_efectuate,
                        tip_impozit="profit", beneficiar_in_registru=True, la_data=None):
    """Creditul fiscal de sponsorizare + redirectionabil D177, DISPECER pe la_data.
    TEMEI: CF art.25 alin.(4) lit.i (credit sponsorizare); OUG 115/2023 (micro: facilitate eliminata);
    Ordin ANAF 3562/2024 (D177). nivel_sursa: REDARE. Versionata in timp: o schimbare de regula (ex.
    eliminarea facilitatii micro) -> varianta datata noua, nu 'if data' - trecutul ramane calculabil."""
    from datetime import date as _dt
    fn, _ = c.alege_varianta(_VARIANTE_CREDIT_SPONSORIZARE, la_data or _dt.today())
    return fn(cifra_afaceri, impozit_profit, sponsorizari_efectuate, tip_impozit, beneficiar_in_registru, la_data)

def nota_sponsorizare(suma, mod="contract"):
    """6582 = 401 (contract, plata ulterioara) | 5121 (plata directa)."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    cont = {"contract": "401", "plata": "5121"}.get(mod)
    if not cont:
        raise ValueError("mod: contract|plata")
    return {"linii": [("6582", cont, s)]}
