"""
core/salarizare.py — calcul salariu brut→net + deduceri + monografie. Calcul PUR, fără DB.
Construit de la zero din Codul fiscal (art. 77, 78, 138, 156, 220^1) + OUG 156/2024.
Cotele (CAS/CASS/impozit/CAM, salariu minim, facilitate) vin din common cu DATĂ de valabilitate.

Conturi salarii (OMFP 1802):
  641 = 421 (brut) ; 421 = 4315 (CAS) ; 421 = 4316 (CASS) ; 421 = 444 (impozit)
  646 = 436 (CAM angajator) ; 421 = 5121 (plata net)
"""
from __future__ import annotations
from decimal import Decimal
from math import floor

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "salarizare"

# deduceri (Cod fiscal art. 77)
PCT_DEDUCERE_BAZA = Decimal("0.20")        # 0 persoane în întreținere
PCT_PER_PERSOANA = Decimal("0.05")          # +5% per persoană (max 4)
PCT_TINERI = Decimal("0.15")                # +15% × salariu minim, tineri <26
DEDUCERE_COPIL_SCOALA = Decimal("100")      # +100 lei/copil la școală
PRAG_VENIT_DEDUCERE = Decimal("2000")       # plafon = salariu_minim + 2000


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


# ============================================================
#  DEDUCERE PERSONALĂ (art. 77)
# ============================================================
def deducere_personala(brut, persoane=0, sub_26=False, copii_scoala=0,
                       functie_baza=True, la_data=None):
    """Întoarce {baza, tineri, copii, total} — sume scăzute din baza impozitului."""
    if not functie_baza:
        return {"baza": _q(0), "tineri": _q(0), "copii": _q(0), "total": _q(0)}
    sm, _ = c.cota("salariu_minim", la_data)
    b = _dec(brut)
    plafon = sm + PRAG_VENIT_DEDUCERE

    # — de bază —
    if b > plafon:
        ded_baza = Decimal(0)
    else:
        pct = PCT_DEDUCERE_BAZA + PCT_PER_PERSOANA * min(persoane, 4)
        if b > sm:
            trepte = floor((b - sm) / 50)
            pct = max(Decimal(0), pct - Decimal("0.005") * trepte)
        ded_baza = pct * sm

    # — suplimentar tineri <26 (brut între 2000 și plafon) —
    tineri = PCT_TINERI * sm if (sub_26 and PRAG_VENIT_DEDUCERE < b <= plafon) else Decimal(0)
    # — suplimentar copii la școală (indiferent de venit) —
    copii = DEDUCERE_COPIL_SCOALA * _dec(copii_scoala)

    total = ded_baza + tineri + copii
    # rotunjire la 10 lei in SUS, in favoarea contribuabilului (art.77 Cod fiscal)
    if total > 0:
        total = (Decimal(int((total + Decimal("9.9999")) / 10))) * 10
    return {"baza": _q(ded_baza), "tineri": _q(tineri),
            "copii": _q(copii), "total": _q(total)}


# ============================================================
#  CALCUL SALARIU BRUT → NET
# ============================================================
def calcul_salariu(brut, persoane=0, sub_26=False, copii_scoala=0,
                   functie_baza=True, la_data=None,
                   norma_intreaga=True, venit_brut_total=None,
                   exceptat_suprataxare=False,
                   tichet_valoare=0, tichet_zile=0):
    """Întoarce breakdown complet: facilitate, CAS, CASS, deducere, impozit, net, CAM, cost.

    Parametri noi (OUG 89/2025 art.III + art.146 Cod fiscal):
    - norma_intreaga: False pentru part-time. Afecteaza FACILITATEA (HG 146/2026
      o da doar la norma intreaga). NU afecteaza suprataxarea: art. 146(5^6) o
      cere pentru contract "cu norma intreaga SAU cu timp partial".
    - venit_brut_total: venit brut lunar contractual (default = brut), pt plafon facilitate
    - exceptat_suprataxare: elev/student <26, pensionar, multi-contract cu declarație
    """
    b = _dec(brut)
    sm, temei_sm = c.cota("salariu_minim", la_data)
    cota_cas, _ = c.cota("cas", la_data)
    cota_cass, _ = c.cota("cass", la_data)
    cota_imp, _ = c.cota("impozit_venit", la_data)
    cota_cam, _ = c.cota("cam", la_data)
    facilitate_val, _ = c.cota("facilitate_salariu_minim", la_data)
    plafon_fac, _ = c.cota("plafon_facilitate_salariu_minim", la_data)

    # FACILITATE (OUG 89/2025 art.III) - conditii CUMULATIVE:
    #   (a) norma intreaga  (b) functie de baza  (c) brut EXACT = salariul minim
    #   (d) venit brut total (fara tichete) <= plafon (4300 S1 / 4600 S2)
    vbt = _dec(venit_brut_total) if venit_brut_total is not None else b
    facilitate = facilitate_val if (
        norma_intreaga and functie_baza and b == sm and vbt <= plafon_fac
    ) else Decimal(0)
    baza_contrib = b - facilitate

    cas = baza_contrib * cota_cas
    cass = baza_contrib * cota_cass

    ded = deducere_personala(b, persoane, sub_26, copii_scoala, functie_baza, la_data)

    baza_imp = baza_contrib - cas - cass - _dec(ded["total"])
    if baza_imp < 0:
        baza_imp = Decimal(0)

    # [F133] TICHETE DE MASA: CASS 10% + impozit 10% pe valoarea nominala; FARA CAS, FARA CAM,
    # FARA deducere personala (aceea e pe salariu). Contributia (CASS) e deductibila din baza
    # impozitului (regula Cod fiscal: impozit pe venit-contributii) -> impozit pe (nominal-cass).
    # Nr tichete = zile efectiv lucrate (0 fara pontaj - decis 20.07). Valoarea plafonata la
    # maximul legal (siguranta; inputul e deja validat 0..plafon in salariati_api).
    tichet_val, _ = c.cota("tichet_masa_plafon", la_data)
    tv = _dec(tichet_valoare)
    tv = min(tv, tichet_val) if tv > 0 else Decimal(0)
    tichete_nominal = tv * _dec(tichet_zile)
    cass_tichete = tichete_nominal * cota_cass
    baza_imp_tichete = tichete_nominal - cass_tichete
    if baza_imp_tichete < 0:
        baza_imp_tichete = Decimal(0)
    impozit_tichete = baza_imp_tichete * cota_imp

    # impozitul returnat = TOTAL (salariu + tichete), ca sa fie corect pt net/monografie/D112
    impozit = baza_imp * cota_imp + impozit_tichete
    net = b - cas - cass - cass_tichete - impozit

    cam = b * cota_cam

    # SUPRATAXARE SUB SALARIUL MINIM (art. 146 alin. (5^6) si art. 168 alin. (6^1)
    # Cod fiscal). Verificat la sursa 15.07.2026 (mfinante.gov.ro, text oficial):
    # "in baza unui contract individual de munca CU NORMA INTREAGA SAU CU TIMP PARTIAL
    # ... nu poate fi mai mica decat nivelul contributiei ... asupra salariului de baza
    # minim brut pe tara". CONDITIA LEGALA E VENITUL SUB MINIM, NU NORMA.
    # CORECTIE 15.07.2026: conditia cerea `not norma_intreaga` -> un salariat cu norma
    # intreaga si brut sub minim NU era suprataxat in statul de plata, dar ERA declarat
    # suprataxat in D112 (d112.pull:336 aplica pragul indiferent de norma). Doua cifre
    # diferite pentru acelasi salariat. Divergenta descoperita mecanic, prin control
    # incrucisat nota-vs-declaratie (salarii_contare.control_coerenta).
    # Exceptiile sunt cele de la alin. (5^7): elev/student <26, pensionar, multi-contract
    # cu declaratie pe propria raspundere -> parametrul exceptat_suprataxare.
    # norma_intreaga ramane conditie pentru FACILITATE (HG 146/2026 cere norma intreaga),
    # nu pentru suprataxare.
    baza_podea = sm - facilitate_val
    cas_suprataxa = Decimal(0)
    cass_suprataxa = Decimal(0)
    if (not exceptat_suprataxare) and baza_contrib < baza_podea:
        diferenta = baza_podea - baza_contrib
        cas_suprataxa = diferenta * cota_cas
        cass_suprataxa = diferenta * cota_cass

    return {
        "brut": _q(b),
        "facilitate": _q(facilitate),
        "cas": _q(cas),
        "cass": _q(cass),
        "deducere": ded,
        "baza_impozabila": _q(baza_imp),
        "impozit": _q(impozit),
        "net": _q(net),
        "cam": _q(cam),
        "cas_suprataxa": _q(cas_suprataxa),
        "cass_suprataxa": _q(cass_suprataxa),
        # [F133] tichete de masa (0 daca nu primeste / fara pontaj)
        "tichete_nominal": _q(tichete_nominal),   # valoarea tichetelor acordate
        "cass_tichete": _q(cass_tichete),          # CASS retinut pe tichete (inclus in baza CASS D112)
        "impozit_tichete": _q(impozit_tichete),    # impozit pe tichete (inclus in "impozit")
        # angajatorul suporta valoarea nominala a tichetelor (le cumpara) - cost real
        "cost_angajator": _q(b + cam + cas_suprataxa + cass_suprataxa + tichete_nominal),
    }


# ============================================================
#  MONOGRAFIE SALARII — note cu urmă
# ============================================================
def monografie_salariu(calc):
    """Generează notele din rezultatul calcul_salariu."""
    # [F133] CASS retinut = salariu + tichete (tichetele intra in baza CASS); impozitul
    # returnat e deja TOTAL (salariu+tichete). Reteneri suportate din salariul cash (421).
    cass_total = _dec(calc["cass"]) + _dec(calc.get("cass_tichete", 0))
    note = [
        _nota("641", "421", calc["brut"]),       # cheltuială salarii brute
        _nota("421", "4315", calc["cas"]),        # CAS reținut (angajat)
        _nota("421", "4316", cass_total),         # CASS reținut (salariu + tichete)
        _nota("421", "444", calc["impozit"]),     # impozit pe venit (salariu + tichete)
        _nota("646", "436", calc["cam"]),         # CAM angajator
    ]
    # [F133] acordarea tichetelor de masa: cheltuiala (642) din biletele de valoare (5328).
    # Achizitia biletelor (5328=5121/401) e tranzactie separata, in afara statului.
    tichete_nom = _dec(calc.get("tichete_nominal", 0))
    if tichete_nom > 0:
        note.append(_nota("642", "5328", tichete_nom))  # cheltuiala tichete de masa acordate
    # suprataxare part-time (art.146 Cod fiscal): diferența CAS/CASS suportată
    # de angajator peste venitul real, până la baza-podea (minim - facilitate)
    cas_supra = calc.get("cas_suprataxa", 0)
    cass_supra = calc.get("cass_suprataxa", 0)
    if _dec(cas_supra) > 0:
        note.append(_nota("6451", "4315", cas_supra))   # CAS suprataxa (cheltuială unitate)
    if _dec(cass_supra) > 0:
        note.append(_nota("6453", "4316", cass_supra))  # CASS suprataxa (cheltuială unitate)
    return note


def monografie_plata(net, cont_trezorerie="5121"):
    """421 = 5121/5311 (plata salariului net)."""
    return _nota("421", cont_trezorerie, net)

# ============================================================
#  CONCEDII MEDICALE — OUG 158/2005 + Legea 141/2025 + OUG 91/2025
#  + Ordinul 506/1030/2026 (diminuare 1 zi PER EPISOD, nu per certificat)
#  Verificat la sursa: legislatie.just.ro, MOF 507/19.06.2026
# ============================================================
def procent_cm(cod, zile_episod, procent_accident=100):
    """Procent indemnizatie dupa cod (nomenclator Legea 125/2006, art. 17-31 OUG 158/2005).
    01=55/65/75 progresiv (Legea 141/2025); 02/03/04=80 sau 100 (FAAMBP, param);
    05/06/12/14/51=100; 07/13/15=75; 08/09=85. Cod 10 (reducere timp munca) NU are
    procent - formula speciala art. 19 (diferenta venit, max 25% din baza) -> ValueError."""
    cod = str(cod or "01").zfill(2)
    if cod == "01":
        if zile_episod <= 7: return Decimal("0.55")
        if zile_episod <= 14: return Decimal("0.65")
        return Decimal("0.75")
    if cod == "10":
        raise ValueError("cod 10 (reducere timp munca): formula speciala art. 19 - "
                         "foloseste calcul_cm_cod10")
    if cod in ("02", "03", "04"):  # accidente munca/boala prof: 80% sau 100% (aviz ITM)
        return Decimal(str(procent_accident)) / 100
    if cod in ("05", "06", "12", "14", "51"): return Decimal("1.00")  # infectocontagioase A/urgente/TBC/neoplazii-SIDA/izolare
    if cod in ("08", "09"): return Decimal("0.85")  # maternitate / ingrijire copil
    return Decimal("0.75")  # 07 carantina, 13 cardiovasculare, 15 risc maternal, rest


def calcul_cm_cod10(baza_lunara, venit_realizat):
    """Cod 10 - reducere timp munca cu 1/4 (art. 19 OUG 158/2005):
    indemnizatia = baza de calcul - venitul realizat in noua situatie,
    plafonata la 25% din baza de calcul."""
    b, v = _dec(baza_lunara), _dec(venit_realizat)
    if b <= 0 or v < 0:
        raise ValueError("baza/venit invalide")
    return _q(min(max(b - v, Decimal("0")), b * Decimal("0.25")))

def calcul_cm(venituri_6_luni, zile_lucratoare_6_luni, zile_lucratoare_cm,
              cod="01", zile_episod=None, prima_zi_din_episod=True,
              spitalizare=False, la_data=None, exceptat_prima_zi=False,
              procent_accident=100):
    """
    Ci = Mzbci x procent x (NZLCM - diminuare)
    - Mzbci = suma venituri 6 luni / total zile lucratoare 6 luni
    - diminuare 1 zi: certificate 01.02.2026-31.12.2027, O DATA per episod,
      NU la spitalizare, accidente 02/03/04, izolare 51, maternitate 08, oncologic 17, risc maternal 15, PNS 12/13/14
    - rotunjire la leu (norme CNAS)
    """
    from datetime import date as _dt
    ref = la_data or _dt.today()
    mz = _dec(venituri_6_luni) / _dec(zile_lucratoare_6_luni or 1)
    ze = zile_episod if zile_episod is not None else zile_lucratoare_cm
    pct = procent_cm(cod, ze, procent_accident)
    diminuare = 0
    # Exceptii diminuare 1 zi verif. la sursa MOF 507/19.06.2026 (Ordinul 506/1030/2026):
    # accidente 02/03/04, izolare 51, maternitate 08, oncologic 17, risc maternal 15, PNS 12/13/14.
    # NU exceptate: urgente 06, carantina 07, boala obisnuita 01, ingrijire copil 09.
    if (_dt(2026, 2, 1) <= ref <= _dt(2027, 12, 31)
            and prima_zi_din_episod and not spitalizare and not exceptat_prima_zi
            and str(cod).zfill(2) not in ("02", "03", "04", "08", "12", "13", "14", "15", "17", "51")):
        diminuare = 1
    zile_platite = max(zile_lucratoare_cm - diminuare, 0)
    brut = (mz * pct * zile_platite).quantize(Decimal("1"))  # rotunjit la leu
    # split angajator/FNUASS (Norme OUG 158/2005): angajatorul suporta zilele 2-6 ale
    # concediului = primele 5 zile lucratoare din cele PLATITE (prima zi diminuata e
    # neplatita, nu reduce plafonul de 5 al angajatorului); FNUASS suporta din ziua 7.
    zile_ang = min(zile_platite, 5)
    zile_fnuass = zile_platite - zile_ang
    brut_ang = (mz * pct * zile_ang).quantize(Decimal("1"))
    brut_fnuass = brut - brut_ang
    return {
        "media_zilnica": _q(mz), "procent": _q(pct * 100),
        "zile_platite": zile_platite, "diminuare": diminuare,
        "zile_ang": zile_ang, "zile_fnuass": zile_fnuass,
        "brut": _q(brut), "brut_ang": _q(brut_ang), "brut_fnuass": _q(brut_fnuass),
    }


# Coduri indemnizatie pt care NU se retine CASS (verif. la sursa: art.17(2) OUG 34/2024,
# aplicabil dupa 12.04.2024). CASS se retine DOAR pt 01 (boala obisnuita), 07 (carantina),
# 10 (reducere program). CAS NU se retine niciodata pe indemnizatia CM. Impozit 10% mereu.
_CM_COD_CU_CASS = ("01", "07", "10")


def taxe_cm(brut, cod="01", la_data=None):
    """Retineri pe indemnizatia de concediu medical (OUG 158/2005 + Cod fiscal).
    - CAS = 0 (indemnizatia CM nu e baza CAS)
    - CASS 10% DOAR pentru codurile 01/07/10; scutit pentru rest (08 maternitate,
      15/16/17, 09 ingrijire copil, 05/06/51/91/92/12/13/14 etc.)
    - impozit 10% pe (brut - cass), fara deducere personala pe indemnizatie
    Intoarce {cas, cass, impozit, net}."""
    from core import common as _c
    b = _dec(brut)
    cota_cass, _ = _c.cota("cass", la_data)
    cota_imp, _ = _c.cota("impozit_venit", la_data)
    cas = Decimal(0)
    cass = (b * cota_cass).quantize(Decimal("1")) if str(cod).zfill(2) in _CM_COD_CU_CASS else Decimal(0)
    impozit = ((b - cass) * cota_imp).quantize(Decimal("1"))
    net = b - cas - cass - impozit
    return {"cas": _q(cas), "cass": _q(cass), "impozit": _q(impozit), "net": _q(net)}
