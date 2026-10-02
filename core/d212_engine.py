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
    cass_prag_min_sm: int = 6   # baza MINIMA (CF art.174 alin.(6)); sub ea se datoreaza diferenta, cu exceptiile alin.(7)-(8)
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

# Anii de venit pentru care plafoanele sunt VERIFICATE LA SURSA. `fisa_d212` refuza restul:
# un an neverificat ar produce o fisa PLAUZIBILA pe praguri neconfirmate, iar aia e mai rea
# decat un refuz. Un an se adauga DUPA ce plafoanele lui sunt verificate la sursa si scrise
# deasupra, nu inainte. [an_derivat 24.08.2026]
ANI_VERIFICATI = (2025, 2026)


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
        "cas": float(_common._q(baza * plafoane.cas_cota)),
    }


#: Situațiile în care diferența de CASS până la baza minimă de 6 salarii NU se datorează (CF art.174 alin.(7) și (8)).
#: Le știe contabilul (venituri din alte surse, statut), nu evidența PFA — de-aia sunt un parametru, nu o deducție.
EXCEPTII_MINIM_CASS = {
    "salarii": "art.174 alin.(7) lit.a) — salarii și asimilate salariilor de cel puțin 6 salarii minime",
    "venituri_c_h": "art.174 alin.(7) lit.b) — venituri art.155 alin.(1) lit.c)-h) cu CASS la cel puțin 6 salarii minime",
    "pensii": "art.174 alin.(7) lit.c) — venituri din pensii",
    "exceptat_art154": "art.174 alin.(8) lit.a) — exceptat în anul precedent (art.154 alin.(1) lit.a), b), e), f))",
    "optiune_art180": "art.174 alin.(8) lit.b) — a optat în anul precedent pentru CASS (art.180 alin.(1))",
}


def calculeaza_cass(venit_net: float, plafoane: PlafoaneD212, optiune_cass: bool = False,
                    exceptie_minim: str = None) -> dict:
    """
    CASS 10% (CF art.156) pe venitul net din activități independente, LINIAR (art.170 alin.(1)): baza = venitul net,
    plafonată la prag_max salarii minime. Pierderea / venitul zero -> nu se datorează (instrucțiunile D212 pct.48 lit.c),
    decât prin opțiune (baza = prag_min).

    [02.10.2026, neconformitate reparată] Sub prag_min CASS NU e „opțională”: art.170 alin.(1) o cere pe venitul net
    oricât de mic, iar art.174 alin.(6) cere în plus „o diferență de contribuție … până la nivelul celei corespunzătoare
    bazei de calcul egale cu 6 salarii minime brute pe țară” — deci baza = prag_min — cu excepțiile din alin.(7)-(8)
    (`EXCEPTII_MINIM_CASS`, date de contabil). Diferența NU se deduce la impozit (art.118 alin.(2) lit.b): de-aia se
    întoarce separat `cass_pe_venit` (deductibilă) și `diferenta_minim`.
    """
    prag_min = plafoane.cass_prag_min_sm * plafoane.salariu_minim
    prag_max = plafoane.cass_prag_max_sm * plafoane.salariu_minim
    if exceptie_minim is not None and exceptie_minim not in EXCEPTII_MINIM_CASS:
        raise ValueError("excepție de la baza minimă CASS necunoscută: %r (permise: %s)"
                         % (exceptie_minim, ", ".join(sorted(EXCEPTII_MINIM_CASS))))

    def _r(obligatoriu, baza, pe_venit):
        cass = float(_common._q(baza * plafoane.cass_cota))
        cass_venit = float(_common._q(pe_venit * plafoane.cass_cota))
        return {"obligatoriu": obligatoriu, "baza": float(_common._q(baza)), "cass": cass,
                "cass_pe_venit": cass_venit, "diferenta_minim": float(_common._q(cass - cass_venit)),
                "exceptie_minim": exceptie_minim}

    if venit_net <= 0:
        # pierdere / venit zero: nu se datorează; opțiunea (art.180) -> baza minimă, nimic deductibil
        return _r(False, prag_min, 0) if optiune_cass else _r(False, 0, 0)
    if venit_net < prag_min:
        # art.170 alin.(1) pe venit + art.174 alin.(6) diferența până la 6 sm, afară de excepțiile alin.(7)-(8)
        return _r(True, venit_net if exceptie_minim else prag_min, venit_net)
    baza = venit_net if venit_net <= prag_max else prag_max
    return _r(True, baza, baza)


def calculeaza_d212(
    venit_brut: float,
    cheltuieli_deductibile: float,
    plafoane: PlafoaneD212,
    optiune_cas: bool = False,
    optiune_cass: bool = False,
    exceptie_minim_cass: str = None,
) -> dict:
    """
    Venit net = venit brut - cheltuieli deductibile (art. 68 Cod fiscal).
    Impozit = 10% x (venit net - CAS - CASS).
    Returneaza toate componentele pentru Fisa de calcul D212.
    """
    venit_net = float(_common._q(venit_brut - cheltuieli_deductibile))
    if venit_net < 0:
        venit_net = 0.0

    cas = calculeaza_cas(venit_net, plafoane, optiune_cas)
    cass = calculeaza_cass(venit_net, plafoane, optiune_cass, exceptie_minim_cass)

    # CF art.118 alin.(2) lit.b): se deduc CAS și CASS datorate, „cu excepția diferenței de contribuție de asigurări
    # sociale de sănătate prevăzută la art. 174 alin. (6)” -> doar CASS pe venit, nu și completarea până la 6 sm
    baza_impozit = max(0.0, venit_net - cas["cas"] - cass["cass_pe_venit"])
    impozit = float(_common._q(baza_impozit * plafoane.impozit_cota))

    return {
        "venit_brut": venit_brut,
        "cheltuieli_deductibile": cheltuieli_deductibile,
        "venit_net": venit_net,
        "cas": cas,
        "cass": cass,
        "baza_impozit": float(_common._q(baza_impozit)),
        "impozit": impozit,
        "total_datorat": float(_common._q(cas["cas"] + cass["cass"] + impozit)),
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

    # CASS: sub 6 sm (24300) -> baza minima 6 sm (CF art.174 alin.(6)); deductibila doar CASS pe venit (art.118)
    r = calculeaza_cass(20000, p)
    assert (r["obligatoriu"], r["baza"], r["cass"], r["cass_pe_venit"], r["diferenta_minim"]) == \
        (True, 24300, 2430.0, 2000.0, 430.0), r
    # ... cu exceptia art.174 alin.(7): doar CASS pe venit
    r = calculeaza_cass(20000, p, exceptie_minim="salarii")
    assert (r["baza"], r["cass"], r["diferenta_minim"]) == (20000, 2000.0, 0.0), r

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
    assert r["impozit"] == float(_common._q(r["baza_impozit"] * 0.10))

    print("Toate testele D212 au trecut. Praguri: sm=%s" % p.salariu_minim)


if __name__ == "__main__":
    _test()
