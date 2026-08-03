"""
Motor calcul D212 - PFA/II/IF sistem real (partida simpla), conform:
- Cod fiscal art. 148-149 (CAS), art. 154/170 (CASS), art. 68-69 (venit net)
- Legea 239/2025 art.XII pct.19 (plafon CASS 72 sm - aplicabil DOAR veniturilor 2026, D212 depusa 2027)
- HG 1506/2024: salariu minim brut 2025 = 4050 lei (reper pt. D212 depusa in 2026)

ATENTIE: plafoanele difera pe an fiscal al VENITULUI, nu pe anul depunerii.
Se instantiaza cu salariul minim corect pentru anul de venit declarat.
"""

from dataclasses import dataclass
from datetime import date

from core import common as _common


@dataclass(frozen=True)
class PlafoaneD212:
    """Plafoane pentru un an fiscal de venit. Sursa trebuie verificata anual la ANAF/Cod fiscal."""
    salariu_minim: int          # reper anual (HG in vigoare pt anul de venit)
    cas_cota: float = 0.25
    cas_prag_min_sm: int = 12   # sub asta: CAS optional
    cas_prag_max_sm: int = 24   # peste asta: baza plafonata la 24 sm
    cass_cota: float = 0.10
    cass_prag_min_sm: int = 6   # sub asta: CASS optional (exceptie: asigurat din alta sursa)
    cass_prag_max_sm: int = 60  # peste asta: CASS plafonat la 60 sm
    impozit_cota: float = 0.10


def _sm_reper(an):
    """Salariul minim REPER pentru anul de venit `an`: valoarea la 1 IANUARIE, FIX pe tot anul
    (instructiunile formular 212), din registrul de cote - NU literal. Majorarea din iulie (ex. 4325 din
    01.07.2026, HG 146/2026) NU atinge reperul. Face dependenta D212->salariu_minim VIZIBILA in graf (V2)."""
    sm, _ = _common.cota("salariu_minim", date(an, 1, 1))
    return int(sm)


def plafoane_an(an):
    """PlafoaneD212 pentru anul de venit `an`, cu salariul minim reper din cota() (nu hardcodat). Legea
    239/2025 (art.XII pct.19) urca plafonul CASS de la 60 la 72 sm pentru venituri 2026+."""
    return PlafoaneD212(salariu_minim=_sm_reper(an), cass_prag_max_sm=72 if an >= 2026 else 60)


# Venituri 2025 (declarate in D212 depusa in 2026) - reper sm din cota() (HG 1506/2024 = 4050).
PLAFOANE_VENIT_2025 = plafoane_an(2025)
# Venituri 2026 (declarate 2027) - Legea 239/2025 art.XII pct.19 (MO 1160/15.12.2025) urca CASS la 72 sm. VERIFICAT LA SURSA 03.08.2026:
# reperul = salariul minim la 1 ian 2026 = 4050 (fix pe an, majorarea 4325 din iulie NU-l atinge).
PLAFOANE_VENIT_2026 = plafoane_an(2026)


def calculeaza_cas(venit_net: float, plafoane: PlafoaneD212, optiune_cas: bool = False) -> dict:
    """
    CAS 25%, NEOBLIGATORIU sub pragul minim (optional daca optiune_cas=True).
    Baza plafonata in trepte: [prag_min, prag_max) -> baza = prag_min * sm
                              [prag_max, inf)      -> baza = prag_max * sm
    """
    prag_min = plafoane.cas_prag_min_sm * plafoane.salariu_minim
    prag_max = plafoane.cas_prag_max_sm * plafoane.salariu_minim

    if venit_net < prag_min:
        if not optiune_cas:
            return {"obligatoriu": False, "baza": 0, "cas": 0.0}
        baza = prag_min
    elif venit_net < prag_max:
        baza = prag_min
    else:
        baza = prag_max

    return {
        "obligatoriu": venit_net >= prag_min,
        "baza": baza,
        "cas": round(baza * plafoane.cas_cota, 2),
    }


def calculeaza_cass(venit_net: float, plafoane: PlafoaneD212, optiune_cass: bool = False) -> dict:
    """
    CASS 10%, LINIAR pe venitul net intre prag_min si prag_max (nu in trepte, spre deosebire de CAS
    si de veniturile pasive - chirii/dividende/dobanzi - care raman pe trepte 6/12/24 sm).
    Sub prag_min: optional. Peste prag_max: plafonat la prag_max * sm.
    """
    prag_min = plafoane.cass_prag_min_sm * plafoane.salariu_minim
    prag_max = plafoane.cass_prag_max_sm * plafoane.salariu_minim

    if venit_net < prag_min:
        if not optiune_cass:
            return {"obligatoriu": False, "baza": 0, "cass": 0.0}
        baza = prag_min
    elif venit_net <= prag_max:
        baza = venit_net
    else:
        baza = prag_max

    return {
        "obligatoriu": venit_net >= prag_min,
        "baza": round(baza, 2),
        "cass": round(baza * plafoane.cass_cota, 2),
    }


def calculeaza_d212(
    venit_brut: float,
    cheltuieli_deductibile: float,
    plafoane: PlafoaneD212,
    optiune_cas: bool = False,
    optiune_cass: bool = False,
) -> dict:
    """
    Venit net = venit brut - cheltuieli deductibile (art. 68 Cod fiscal).
    Impozit = 10% x (venit net - CAS - CASS).
    Returneaza toate componentele pentru Fisa de calcul D212.
    """
    venit_net = round(venit_brut - cheltuieli_deductibile, 2)
    if venit_net < 0:
        venit_net = 0.0

    cas = calculeaza_cas(venit_net, plafoane, optiune_cas)
    cass = calculeaza_cass(venit_net, plafoane, optiune_cass)

    baza_impozit = max(0.0, venit_net - cas["cas"] - cass["cass"])
    impozit = round(baza_impozit * plafoane.impozit_cota, 2)

    return {
        "venit_brut": venit_brut,
        "cheltuieli_deductibile": cheltuieli_deductibile,
        "venit_net": venit_net,
        "cas": cas,
        "cass": cass,
        "baza_impozit": round(baza_impozit, 2),
        "impozit": impozit,
        "total_datorat": round(cas["cas"] + cass["cass"] + impozit, 2),
    }


# ---------------------------------------------------------------------------
# Teste (validare praguri oficiale venituri 2025 / D212 depusa 2026)
# ---------------------------------------------------------------------------

def _test():
    p = PLAFOANE_VENIT_2025  # salariu_minim=4050

    # CAS: sub 12 sm (48600) -> optional, neobligatoriu
    r = calculeaza_cas(40000, p)
    assert r == {"obligatoriu": False, "baza": 0, "cas": 0.0}, r

    # CAS: intre 12 si 24 sm -> baza = 12 sm = 48600, CAS = 12150
    r = calculeaza_cas(70000, p)
    assert r["obligatoriu"] is True and r["baza"] == 48600 and r["cas"] == 12150.0, r

    # CAS: peste 24 sm (97200) -> baza = 24 sm = 97200, CAS = 24300
    r = calculeaza_cas(150000, p)
    assert r["baza"] == 97200 and r["cas"] == 24300.0, r

    # CASS: sub 6 sm (24300) -> optional, neobligatoriu
    r = calculeaza_cass(20000, p)
    assert r == {"obligatoriu": False, "baza": 0, "cass": 0.0}, r

    # CASS: exact 6 sm -> CASS min 2430
    r = calculeaza_cass(24300, p)
    assert r["cass"] == 2430.0, r

    # CASS: liniar in interval -> 100000 x 10% = 10000
    r = calculeaza_cass(100000, p)
    assert r["cass"] == 10000.0, r

    # CASS: peste 60 sm (243000) -> plafonat la 24300
    r = calculeaza_cass(300000, p)
    assert r["baza"] == 243000 and r["cass"] == 24300.0, r

    # Caz complet: venit brut 150000, cheltuieli 30000 -> venit net 120000
    r = calculeaza_d212(150000, 30000, p)
    assert r["venit_net"] == 120000
    assert r["cas"]["cas"] == 24300.0          # peste 24 sm -> plafon
    assert r["cass"]["cass"] == 12000.0        # 120000 x 10%
    assert r["baza_impozit"] == 120000 - 24300 - 12000
    assert r["impozit"] == round(r["baza_impozit"] * 0.10, 2)

    print("Toate testele D212 au trecut. Praguri: sm=%s" % p.salariu_minim)


if __name__ == "__main__":
    _test()
