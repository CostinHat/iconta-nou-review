# -*- coding: utf-8 -*-
"""D406 Active (SAF-T anual, sectiunea Assets) - generator PUR.
Structura verificata pe saft.xsd oficial ANAF: Asset{AssetID, AccountID,
Description, DateOfAcquisition, StartUpDate, Valuations/Valuation{
AssetValuationType, ValuationClass, AcquisitionAndProductionCostsBegin/End,
InvestmentSupport, choice(AssetLifeYear|AssetLifeMonth), AssetAddition,
Transfers, AssetDisposal, BookValueBegin, DepreciationMethod,
DepreciationPercentage, DepreciationForPeriod, AppreciationForPeriod,
ExtraordinaryDepreciationsForPeriod{...}, AccumulatedDepreciation, BookValueEnd}}.
Depunere anuala, termen = termenul situatiilor financiare.

Amortizarea se calculeaza PE METODA activului (CF art.28, verificat verbatim in
anaf_surse/cod_fiscal_227_2015_consolidat.txt si oug_8_2026.txt):
  - liniara      (alin.6):    cota liniara x valoare; lunar rata = amortizabil/dnf.
  - degresiva    (alin.7):    cota liniara x coeficient (1,5 durata 2-5 ani / 2,0 durata
                              6-10 ani / 2,5 durata >10 ani), pe valoarea ramasa, cu trecere
                              la liniar pe durata ramasa cand liniarul devine mai mare.
  - accelerata   (alin.8):    an 1 = max 50% din valoarea amortizabila; anii urmatori =
                              valoare ramasa / durata normala ramasa (liniar pe rest).
  - superaccelerata (alin.8^1, OUG 8/2026, MO 147/25.02.2026): an 1 = max 65%; rest ca la
                              accelerata. Doar active noi PIF in 2026, subgrupele 2.1 si 2.4.
Amortizarea incepe cu luna urmatoare PIF (alin.12). Eligibilitatea pe categorii (alin.5:
constructii doar liniar; degresiv/accelerat doar echipamente; superaccelerat doar 2.1/2.4)
e raspunderea contabilului - metoda vine din activ; motorul calculeaza metoda ceruta."""
import re as _re
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from xml.sax.saxutils import escape

B = Decimal("0.01")
_MIN_LUNI_NELINIAR = 24   # metodele ne-liniare presupun durata >= 2 ani (alin.7 "intre 2 si 5 ani")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _luni_intre(d1, an, luna):
    """Luni intregi de amortizare de la luna urmatoare PIF pana la (an, luna) inclusiv."""
    if d1 is None:
        return 0
    n = (an - d1.year) * 12 + (luna - d1.month)
    return max(0, n)

def _norm_metoda(v):
    """Normalizeaza eticheta metodei. superaccel se verifica INAINTE de acceler
    ('superaccelerata' contine subsirul 'acceler')."""
    t = _re.sub(r"[\s._-]+", "", str(v or "").lower())   # colapseaza separatorii: "super accelerata" -> "superaccelerata"
    if "superaccel" in t:
        return "superaccelerata"
    if "degres" in t:
        return "degresiva"
    if "acceler" in t:
        return "accelerata"
    return "liniara"

def _coef_degresiv(dnf_luni):
    """Coeficientul degresiv (CF art.28 alin.7): 1,5 (2-5 ani) / 2,0 (6-10 ani) / 2,5 (>10 ani)."""
    ani = Decimal(dnf_luni) / Decimal(12)
    if ani <= 5:
        return Decimal("1.5")
    if ani <= 10:
        return Decimal("2.0")
    return Decimal("2.5")

def _amort_anual_degresiv(amortizabil, dnf_luni):
    """Amortizarea pe fiecare an de utilizare (alin.7): cota liniara x coeficient pe valoarea
    ramasa, cu trecere la liniar (valoare ramasa / ani ramasi) cand liniarul devine >= degresivul.
    Ultimul an absoarbe restul de rotunjire, ca suma = amortizabil."""
    Y = (dnf_luni + 11) // 12
    if Y <= 0:
        return []
    rata = (Decimal(12) / Decimal(dnf_luni)) * _coef_degresiv(dnf_luni)   # cota liniara (=12/dnf) x coef
    out = []
    ramas = amortizabil
    switched = False
    for k in range(Y):
        ani_ramase = Y - k
        if k == Y - 1:
            amt = ramas
        elif switched:
            amt = ramas / ani_ramase
        else:
            deg = ramas * rata
            lin = ramas / ani_ramase
            if deg > lin:
                amt = deg
            else:
                switched = True
                amt = lin
        out.append(amt)
        ramas = ramas - amt
    return out

def _amort_lunar_neliniar(metoda, amortizabil, dnf_luni):
    """Amortizarea pe fiecare LUNA de utilizare (index 0 = prima luna de amortizare =
    luna urmatoare PIF, alin.12). Suma = amortizabil."""
    n = dnf_luni
    luni = [Decimal(0)] * n
    if metoda in ("accelerata", "superaccelerata"):
        pct = Decimal("0.65") if metoda == "superaccelerata" else Decimal("0.50")
        n1 = min(12, n)
        an1 = amortizabil * pct                      # alin.8/8^1: plafon an 1 (50%/65%)
        for i in range(n1):
            luni[i] = an1 / n1
        rest = amortizabil - an1                      # anii urmatori: valoare ramasa / durata ramasa
        nrest = n - n1
        for i in range(n1, n):
            luni[i] = rest / nrest
    elif metoda == "degresiva":
        idx = 0
        for k, amt in enumerate(_amort_anual_degresiv(amortizabil, dnf_luni)):
            luni_an = min(12, n - k * 12)
            for _ in range(luni_an):
                luni[idx] = amt / luni_an
                idx += 1
    else:
        for i in range(n):
            luni[i] = amortizabil / n
    return luni

def _accum_neliniar(luni, pif, an):
    """Amortizarea cumulata pana la 31.12.<an> inclusiv. Luna de utilizare i (0-based) cade in
    anul calendaristic pif.year + (pif.month + i)//12 (amortizarea incepe luna urmatoare PIF)."""
    if pif is None:
        return Decimal(0)
    tot = Decimal(0)
    for i, amt in enumerate(luni):
        y = pif.year + (pif.month + i) // 12
        if y <= an:
            tot += amt
    return tot

# --- Restrictii pe categorii (CF art.28 alin.5 + alin.8^1), pe cont_imobilizare ---
# Legatura cont -> categorie e denumirea contului din OMFP 1802/2014 (in corpus):
#   212  Constructii                                             -> alin.5 lit.a: DOAR liniara
#   2131 Echipamente tehnologice (masini, utilaje si instalatii de lucru) -> alin.5 lit.b
#        (denumirea OMFP e identica cu textul legii): liniara/degresiva/accelerata
#   2134/217 Animale si plantatii (subgrupa 2.4)                -> lit.c (lin/deg) + superacc (alin.8^1)
#   211  Terenuri                                               -> neamortizabil
#   orice alt cont (2132 aparate masura, 2133 transport, 214 mobilier, necunoscut/lipsa) ->
#        alin.5 lit.c ("oricarui altui mijloc fix"): liniara/degresiva (FARA accelerata)
# alin.8^1 (OUG 8/2026): superaccelerata DOAR subgrupa 2.1 (2131) sau 2.4 (2134/217), active
#   NOI puse in functiune in 2026. "Nou vs la mana a doua" NU exista in mijloace_fixe -> se verifica
#   doar subgrupa + PIF in 2026; conditia "nou" ramane raspunderea contabilului (vezi DECIZII 13.08).
def _categorie_activ(cont_imobilizare):
    c = "".join(ch for ch in str(cont_imobilizare or "") if ch.isdigit())
    if c.startswith("212"):
        return "constructii"
    if c.startswith("2131"):
        return "echipamente_2_1"       # alin.5 lit.b (denumire OMFP = textul legii)
    if c.startswith("2134") or c.startswith("217"):
        return "animale_plantatii"     # subgrupa 2.4
    if c.startswith("211"):
        return "terenuri"              # neamortizabil
    return "alt_mijloc_fix"            # lit.c, catch-ul legal: "oricarui altui mijloc fix amortizabil"

def _metode_permise(categorie, pif):
    """Setul de metode permise de lege pentru categorie (alin.5) + fereastra superaccelerata (alin.8^1)."""
    if categorie == "terenuri":
        return set()                   # terenurile nu se amortizeaza
    if categorie == "constructii":
        return {"liniara"}             # lit.a
    permise = {"liniara", "degresiva"}  # lit.b si lit.c permit ambele
    if categorie == "echipamente_2_1":
        permise.add("accelerata")       # lit.b
    if categorie in ("echipamente_2_1", "animale_plantatii") and pif is not None and pif.year == 2026:
        permise.add("superaccelerata")  # alin.8^1: subgrupa 2.1/2.4, PIF in 2026
    return permise

def _verifica_categorie(mf, metoda, pif):
    """Refuza (ValueError) metoda pe care legea NU o permite pentru categoria activului."""
    cont = mf.get("cont_imobilizare")
    categorie = _categorie_activ(cont)
    permise = _metode_permise(categorie, pif)
    if metoda not in permise:
        temei = "CF art.28 alin.5"
        if metoda == "superaccelerata":
            temei = ("CF art.28 alin.8^1 (OUG 8/2026): doar subgrupa 2.1 (echipamente) sau 2.4 "
                     "(animale/plantații), active NOI puse în funcțiune în 2026")
        raise ValueError(
            "MF %s (cont %s -> categorie '%s'): metoda '%s' nu e permisă de lege; permise: %s. Temei: %s."
            % (mf.get("cod"), cont, categorie, metoda,
               (", ".join(sorted(permise)) or "niciuna (activ neamortizabil)"), temei))


# ── REEVALUAREA, ca etapa a amortizarii (R59) ───────────────────────────────────────────────
# OMFP 1802/2014 pct.111-116, METODA VALORII NETE — chiar cea implementata de `core/reevaluare.py`:
# amortizarea cumulata se ELIMINA din valoarea bruta (28xx = 21x), apoi diferenta pana la valoarea
# justa. Consecinta pentru amortizare, si e intreaga regula de mai jos: de la data reevaluarii
# activul se amortizeaza DE LA ZERO, pe valoarea justa, pe durata RAMASA.
#
# De ce sta aici si nu in registru: reevaluarea nu schimba un camp, TAIE durata in etape. Un
# `mijloace_fixe.valoare` urcat fara etapa ar face motorul sa recalculeze amortizarea cumulata pe
# valoarea NOUA de la PIF-ul ORIGINAL — adica sa afirme o amortizare care nu s-a inregistrat
# niciodata, exact divergenta pe care R59 o numeste, mutata de pe o coloana pe alta.

class DurataEpuizata(ValueError):
    """Reevaluare peste o durata normala deja consumata.

    Clasa proprie, nu un `ValueError` oarecare, si nu din eleganta: fara ea, singurul fel de a
    asearta MOTIVUL refuzului ar fi cautarea unui cuvant in mesaj — adica o garda pe TEXT, care
    pazeste formularea de langa lucru, nu lucrul (METODA §23). Iar un test care accepta ORICE refuz
    nu apara motivul refuzului. Mosteneste `ValueError` ca apelantii care il prind deja (generatorul
    SAF-T, ruta de reevaluare) sa se poarte neschimbat.
    """


def _reev_aplicate(mf):
    """Reevaluarile APLICATE ale activului, normalizate si in ordine cronologica.

    `data` se accepta si ca `date`, si ca sir ISO: randurile vin din depozit, dar si din fixturi.
    Fara cheia `reevaluari` lista e goala — si atunci tot ce urmeaza e identic cu comportamentul
    de dinainte, bit cu bit.
    """
    out = []
    for r in (mf.get("reevaluari") or []):
        d = r.get("data")
        if isinstance(d, str):
            d = date.fromisoformat(d[:10])
        if d is None:
            continue
        out.append({"data": d,
                    "valoare_bruta_veche": _d(r.get("valoare_bruta_veche")),
                    "amortizare_eliminata": _d(r.get("amortizare_eliminata")),
                    "valoare_justa": _d(r.get("valoare_justa"))})
    out.sort(key=lambda r: r["data"])
    return out


def _mf_la(mf, la_data):
    """(mf_efectiv, pif_real) — activul asa cum il vede AMORTIZAREA la `la_data`.

    Intoarce un `mf` sintetic cu `valoare` / `data_pif` / `dnf_luni` mutate pe ETAPA care contine
    `la_data`; restul (metoda, rezidual, cont) ramane neatins. Fara reevaluari aplicate intoarce
    `mf` NEATINS — nu o copie, ca sa nu existe nici macar o cale diferita pentru cazul obisnuit.

    `pif_real` se intoarce SEPARAT fiindca `_verifica_categorie` judeca pe data punerii in
    functiune (alin.8^1: „active NOI puse in functiune in 2026"). O reevaluare nu face activul nou;
    daca PIF-ul sintetic ar ajunge acolo, un activ din 2024 reevaluat in 2026 ar deveni deodata
    eligibil pentru superaccelerata. *Reevaluarea schimba valoarea, nu vechimea.*
    """
    pif = mf.get("data_pif")
    reev = _reev_aplicate(mf)
    if not reev:
        return mf, pif
    dnf = int(mf.get("dnf_luni") or 0)
    if pif is None or dnf <= 0:
        return mf, pif
    start, valoare, consumate = pif, reev[0]["valoare_bruta_veche"], 0
    for r in reev:
        if la_data < r["data"]:
            break
        luni = max(0, min(dnf - consumate, _luni_intre(start, r["data"].year, r["data"].month)))
        consumate += luni
        start, valoare = r["data"], r["valoare_justa"]
    if start == pif:
        # `la_data` e INAINTEA primei reevaluari. Valoarea bruta de atunci NU e cea din registru
        # (registrul poarta valoarea de azi), ci cea consemnata pe prima reevaluare. *Fara randul
        # asta, bornele de deschidere ale anilor dinainte s-ar calcula pe valoarea de dupa.*
        ef = dict(mf)
        ef["valoare"] = valoare
        return ef, pif
    ramase = dnf - consumate
    if ramase <= 0:
        # Durata normala s-a epuizat inainte de reevaluare. Cat se amortizeaza de acum e o
        # DECIZIE cu temei din afara (raportul evaluatorului: durata de viata ramasa reestimata,
        # OMFP 1802 pct.113). Nu se poate deriva din registru, deci nu se fabrica.
        raise DurataEpuizata(
            "MF %s: reevaluare la %s peste o durată normală deja epuizată (%d luni de la %s). "
            "Durata rămasă după reevaluare se ia din raportul evaluatorului (OMFP 1802/2014 "
            "pct.113); registrul nu o poate deriva."
            % (mf.get("cod"), start.isoformat(), dnf, pif.isoformat()))
    ef = dict(mf)
    ef["valoare"], ef["data_pif"], ef["dnf_luni"] = valoare, start, ramase
    return ef, pif


def calc_asset(mf, an):
    """mf: dict {cod, denumire, cont_imobilizare, cont_amortizare, valoare,
    rezidual, dnf_luni, data_pif, metoda, activ}. Returneaza dict Valuation pentru anul `an`.
    Metoda din activ decide calculul (CF art.28). Amortizarea incepe cu luna urmatoare PIF.

    [R59] `mf['reevaluari']` (reevaluarile APLICATE) taie durata in etape — v. `_mf_la`. Cele doua
    borne ale anului se calculeaza fiecare pe etapa ei, fiindca o reevaluare din cursul anului le
    pune in etape DIFERITE: 31.12.<an-1> pe valoarea veche, 31.12.<an> pe cea justa.
    """
    reev = _reev_aplicate(mf)
    mf_i, pif_real = _mf_la(mf, date(an - 1, 12, 31))
    mf_s, _ = _mf_la(mf, date(an, 12, 31))
    val = _d(mf_s["valoare"])
    dnf = int(mf.get("dnf_luni") or 0)
    if dnf <= 0 or val <= 0:
        raise ValueError(f"MF {mf.get('cod')}: valoare/dnf invalide")
    _verifica_categorie(mf, _norm_metoda(mf.get("metoda")), pif_real)   # alin.5/8^1: ce legea nu permite -> refuza

    am_inceput = _acumulat_final_an(mf_i, pif_real, an - 1)
    am_sfarsit = _acumulat_final_an(mf_s, pif_real, an)

    achizitie_in_an = bool(pif_real and pif_real.year == an)
    reev_an = [r for r in reev if r["data"].year == an]
    # Valoarea bruta la 1 ianuarie: intr-un an cu reevaluare e cea de dinaintea PRIMEI dintre ele.
    # `cost_begin` = `cost_end` intr-un an in care valoarea s-a schimbat ar fi o afirmatie falsa
    # despre soldul de DESCHIDERE — exact felul de cifra pe care R59 il numeste.
    val_inceput = reev_an[0]["valoare_bruta_veche"] if reev_an else val
    apreciere = sum((r["valoare_justa"] - r["valoare_bruta_veche"] for r in reev_an),
                    Decimal("0.00"))
    if reev_an:
        # Amortizarea ANULUI nu mai e diferenta celor doua borne: reevaluarea ELIMINA amortizarea
        # cumulata intre ele, deci diferenta ar scadea o eliminare din cheltuiala si ar putea iesi
        # chiar negativa. Ce se raporteaza e CHELTUIALA anului — suma ratelor lunare, adica exact
        # ce inregistreaza nota lunara de amortizare (6811 = 28xx). *Un singur motor pentru
        # amandoua; altfel declaratia si evidenta ar avea din nou doua surse.*
        depr = sum((amortizare_luna(mf, an, l) for l in range(1, 13)), Decimal("0.00")).quantize(B)
    else:
        depr = (am_sfarsit - am_inceput).quantize(B)
    return {
        "cost_begin": Decimal("0.00") if achizitie_in_an else val_inceput,
        "cost_end": val,
        "addition": val_inceput if achizitie_in_an else Decimal("0.00"),
        "apreciere": apreciere.quantize(B),
        "book_begin": (Decimal("0.00") if achizitie_in_an else val_inceput - am_inceput).quantize(B),
        "depr_period": depr,
        "accum_depr": am_sfarsit,
        "book_end": (val - am_sfarsit).quantize(B),
        "procent_anual": (Decimal("100") * 12 / dnf).quantize(B, rounding=ROUND_HALF_UP),
    }


def _acumulat_final_an(mf_ef, pif_real, an):
    """Amortizarea cumulata la 31.12.<an>, pe ETAPA primita (`mf_ef` vine din `_mf_la`).

    Corpul e cel dinainte de R59, mutat aici neschimbat, ca cele doua borne ale anului sa se poata
    calcula pe etape DIFERITE. `pif_real` doar pentru `_verifica_categorie` — v. `_mf_la`.
    """
    val = _d(mf_ef["valoare"])
    rez = _d(mf_ef.get("rezidual"))
    dnf = int(mf_ef.get("dnf_luni") or 0)
    pif = mf_ef.get("data_pif")
    amortizabil = val - rez
    metoda = _norm_metoda(mf_ef.get("metoda"))
    _verifica_categorie(mf_ef, metoda, pif_real)
    if metoda == "liniara" or dnf < _MIN_LUNI_NELINIAR:
        # liniara (alin.6) - si fallback pentru durate sub 2 ani, unde metodele ne-liniare nu au sens
        rata = (amortizabil / dnf).quantize(B, rounding=ROUND_HALF_UP)
        luni_pana = max(0, min(dnf, _luni_intre(pif, an, 12)))
        if luni_pana >= dnf:
            return amortizabil
        return (rata * luni_pana).quantize(B, rounding=ROUND_HALF_UP)
    luni = _amort_lunar_neliniar(metoda, amortizabil, dnf)
    return min(amortizabil, _accum_neliniar(luni, pif, an)).quantize(B, rounding=ROUND_HALF_UP)

def amortizat_la_data(mf, la_data):
    """Amortizarea cumulata 'la zi' (pana la `la_data` inclusiv) pe METODA reala a activului
    (CF art.28), plus valoarea ramasa (net book value). Amortizarea incepe luna urmatoare PIF
    (alin.12); numarul de rate lunare inregistrate = lunile scurse de la PIF pana la la_data,
    plafonat la dnf. La granita de an (la_data = 31.12.<an>) rezultatul coincide cu
    calc_asset(mf, an)['accum_depr'] / ['book_end'] - aceeasi sursa de amortizare, un singur motor.
    mf: acelasi dict ca la calc_asset. Ridica ValueError pe metoda nepermisa pe categorie
    (alin.5/8^1) sau date invalide - apelantul decide cum arata randul, NU fabrica liniar tacit.

    [R59] Daca activul are reevaluari APLICATE, se raspunde pe ETAPA care contine `la_data`:
    amortizarea cumulata a fost ELIMINATA la reevaluare, deci dupa ea porneste de la zero."""
    mf, _pif_real = _mf_la(mf, la_data)
    val = _d(mf["valoare"])
    rez = _d(mf.get("rezidual"))
    dnf = int(mf.get("dnf_luni") or 0)
    if dnf <= 0 or val <= 0:
        raise ValueError(f"MF {mf.get('cod')}: valoare/dnf invalide")
    pif = mf.get("data_pif")
    metoda = _norm_metoda(mf.get("metoda"))
    _verifica_categorie(mf, metoda, _pif_real)   # ce legea nu permite pe categorie -> refuza (nu calcula gresit)
    amortizabil = val - rez
    if pif is None:
        return {"amortizat": Decimal("0.00"), "ramas": val.quantize(B), "metoda": metoda}
    luni_scurse = max(0, min(dnf, (la_data.year - pif.year) * 12 + (la_data.month - pif.month)))
    if metoda == "liniara" or dnf < _MIN_LUNI_NELINIAR:
        rata = (amortizabil / dnf).quantize(B, rounding=ROUND_HALF_UP)
        amortizat = amortizabil if luni_scurse >= dnf else (rata * luni_scurse).quantize(B, rounding=ROUND_HALF_UP)
    else:
        luni = _amort_lunar_neliniar(metoda, amortizabil, dnf)
        amortizat = min(amortizabil, sum(luni[:luni_scurse], Decimal(0))).quantize(B, rounding=ROUND_HALF_UP)
    ramas = (val - amortizat).quantize(B)
    return {"amortizat": amortizat, "ramas": ramas, "metoda": metoda}

def amortizare_luna(mf, an, luna):
    """Amortizarea unei SINGURE luni calendaristice (an, luna) pe METODA reala (CF art.28).
    0.00 daca luna e inaintea primei luni de amortizare (luna urmatoare PIF, alin.12) sau dupa
    epuizarea dnf. Ultima luna liniara absoarbe restul de rotunjire, ca suma lunilor 1..dnf =
    valoarea amortizabila (coerent cu amortizat_la_data la epuizare). Ridica ValueError pe metoda
    nepermisa pe categorie (alin.5/8^1) - apelantul (nota lunara) decide, nu fabrica liniar tacit.

    [R59] Luna se calculeaza pe ETAPA in care cade: dupa o reevaluare aplicata, rata e valoarea
    JUSTA impartita la durata RAMASA. Luna reevaluarii apartine etapei NOI — reevaluarea se
    inregistreaza cu data ei, iar amortizarea incepe luna urmatoare (alin.12), ca la PIF."""
    mf, _pif_real = _mf_la(mf, date(an, luna, 28))
    val = _d(mf["valoare"])
    rez = _d(mf.get("rezidual"))
    dnf = int(mf.get("dnf_luni") or 0)
    if dnf <= 0 or val <= 0:
        raise ValueError(f"MF {mf.get('cod')}: valoare/dnf invalide")
    pif = mf.get("data_pif")
    metoda = _norm_metoda(mf.get("metoda"))
    _verifica_categorie(mf, metoda, _pif_real)
    if pif is None:
        return Decimal("0.00")
    luni_trecute = (an - pif.year) * 12 + (luna - pif.month)   # index (1-based) al lunii de amortizare
    if luni_trecute < 1 or luni_trecute > dnf:
        return Decimal("0.00")
    amortizabil = val - rez
    if metoda == "liniara" or dnf < _MIN_LUNI_NELINIAR:
        rata = (amortizabil / dnf).quantize(B, rounding=ROUND_HALF_UP)
        if luni_trecute == dnf:                                 # ultima luna: rest, ca totalul = amortizabil
            return (amortizabil - rata * (dnf - 1)).quantize(B)
        return rata
    luni = _amort_lunar_neliniar(metoda, amortizabil, dnf)
    if luni_trecute == dnf:                                     # ultima luna: rest, ca totalul = amortizabil
        prev = sum((x.quantize(B, rounding=ROUND_HALF_UP) for x in luni[:dnf - 1]), Decimal(0))
        return (amortizabil - prev).quantize(B)
    return luni[luni_trecute - 1].quantize(B, rounding=ROUND_HALF_UP)

def xml_asset(mf, an, valuation_class="2"):
    """XML pentru un Asset. valuation_class: cod clasificare (implicit grupa 2)."""
    v = calc_asset(mf, an)
    pif = mf.get("data_pif") or date(an, 1, 1)
    e = escape
    return f"""<nsSAFT:Asset>
<nsSAFT:AssetID>{e(str(mf.get('cod') or mf['id']))}</nsSAFT:AssetID>
<nsSAFT:AccountID>{e(mf.get('cont_imobilizare') or '2131')}</nsSAFT:AccountID>
<nsSAFT:Description>{e(mf['denumire'])}</nsSAFT:Description>
<nsSAFT:DateOfAcquisition>{pif.isoformat()}</nsSAFT:DateOfAcquisition>
<nsSAFT:StartUpDate>{pif.isoformat()}</nsSAFT:StartUpDate>
<nsSAFT:Valuations><nsSAFT:Valuation>
<nsSAFT:AssetValuationType>contabila</nsSAFT:AssetValuationType>
<nsSAFT:ValuationClass>{e(str(valuation_class))}</nsSAFT:ValuationClass>
<nsSAFT:AcquisitionAndProductionCostsBegin>{v['cost_begin']}</nsSAFT:AcquisitionAndProductionCostsBegin>
<nsSAFT:AcquisitionAndProductionCostsEnd>{v['cost_end']}</nsSAFT:AcquisitionAndProductionCostsEnd>
<nsSAFT:InvestmentSupport>0.00</nsSAFT:InvestmentSupport>
<nsSAFT:AssetLifeMonth>{mf['dnf_luni']}</nsSAFT:AssetLifeMonth>
<nsSAFT:AssetAddition>{v['addition']}</nsSAFT:AssetAddition>
<nsSAFT:Transfers>0.00</nsSAFT:Transfers>
<nsSAFT:AssetDisposal>0.00</nsSAFT:AssetDisposal>
<nsSAFT:BookValueBegin>{v['book_begin']}</nsSAFT:BookValueBegin>
<nsSAFT:DepreciationMethod>{e(_norm_metoda(mf.get('metoda')))}</nsSAFT:DepreciationMethod>
<nsSAFT:DepreciationPercentage>{v['procent_anual']}</nsSAFT:DepreciationPercentage>
<nsSAFT:DepreciationForPeriod>{v['depr_period']}</nsSAFT:DepreciationForPeriod>
<nsSAFT:AppreciationForPeriod>{v['apreciere']}</nsSAFT:AppreciationForPeriod>
<nsSAFT:ExtraordinaryDepreciationsForPeriod><nsSAFT:ExtraordinaryDepreciationForPeriod>
<nsSAFT:ExtraordinaryDepreciationMethod>nu</nsSAFT:ExtraordinaryDepreciationMethod>
<nsSAFT:ExtraordinaryDepreciationAmountForPeriod>0.00</nsSAFT:ExtraordinaryDepreciationAmountForPeriod>
</nsSAFT:ExtraordinaryDepreciationForPeriod></nsSAFT:ExtraordinaryDepreciationsForPeriod>
<nsSAFT:AccumulatedDepreciation>{v['accum_depr']}</nsSAFT:AccumulatedDepreciation>
<nsSAFT:BookValueEnd>{v['book_end']}</nsSAFT:BookValueEnd>
</nsSAFT:Valuation></nsSAFT:Valuations>
</nsSAFT:Asset>"""

def xml_assets(lista_mf, an):
    corp = "\n".join(xml_asset(mf, an) for mf in lista_mf)
    return f"<nsSAFT:Assets>\n{corp}\n</nsSAFT:Assets>"


def xml_d406_anual_active(prof, lista_mf, an, data_creata=None):
    """D406 ANUAL - raportarea de active (SAF-T), FISIER COMPLET, DUK-valid.

    Poarta care permite sectiunea Assets e HeaderComment='A' (tip anual); sursa: enumul
    AUDIT_FILE_TYPE din D406Validator.jar (L=lunar, T=trimestrial, C=la cerere, A=anual).
    Cu 'L'/'T' Asset are max 0 aparitii ("AssetID a depasit numarul maxim (0)"); cu 'A' e
    permis. Profilul anual cere: perioada 1..12 pe acelasi an; toate sectiunile non-Asset
    prezente dar GOALE; GeneralLedgerEntries gol; SourceDocuments cu cele 5 subsectiuni in
    ordine (AssetTransactions cu NumberOfAssetTransactions=0). Doar <Assets> e populat, cu
    amortizarea pe metoda (calc_asset). Dovedit DUK-valid pe tenant_013 (13.08.2026,
    DUKIntegrator_AnLunaUI, pachet oficial ANAF)."""
    e = escape
    cui = "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit())
    tab = (prof.get("baza_contabila") or "A").upper()
    frag = xml_assets(lista_mf, an).replace("nsSAFT:", "")   # plicul anual are ns implicit (fara prefix)
    dc = data_creata or date.today().isoformat()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<AuditFile xmlns="mfp:anaf:dgti:d406:declaratie:v1">
  <Header>
    <AuditFileVersion>2.4.9</AuditFileVersion>
    <AuditFileCountry>RO</AuditFileCountry>
    <AuditFileDateCreated>{dc}</AuditFileDateCreated>
    <SoftwareCompanyName>iConta</SoftwareCompanyName>
    <SoftwareID>iConta SaaS</SoftwareID>
    <SoftwareVersion>1.0</SoftwareVersion>
    <Company>
      <RegistrationNumber>{e(cui)}</RegistrationNumber>
      <Name>{e(prof.get('nume') or '-')}</Name>
      <Address>
        <StreetName>{e(prof.get('adresa') or '-')}</StreetName>
        <City>{e(prof.get('oras') or '-')}</City>
        <PostalCode>{e(prof.get('cod_postal') or '000000')}</PostalCode>
        <Country>RO</Country>
      </Address>
      <Contact>
        <ContactPerson>
          <FirstName>-</FirstName>
          <LastName>{e(prof.get('nume') or '-')}</LastName>
        </ContactPerson>
        <Telephone>-</Telephone>
      </Contact>
      <BankAccount>
        <IBANNumber>RO00BANK0000000000000000</IBANNumber>
      </BankAccount>
    </Company>
    <DefaultCurrencyCode>RON</DefaultCurrencyCode>
    <SelectionCriteria>
      <PeriodStart>1</PeriodStart>
      <PeriodStartYear>{an}</PeriodStartYear>
      <PeriodEnd>12</PeriodEnd>
      <PeriodEndYear>{an}</PeriodEndYear>
    </SelectionCriteria>
    <HeaderComment>A</HeaderComment>
    <SegmentIndex>1</SegmentIndex>
    <TotalSegmentsInsequence>1</TotalSegmentsInsequence>
    <TaxAccountingBasis>{e(tab)}</TaxAccountingBasis>
  </Header>
  <MasterFiles>
    <GeneralLedgerAccounts/>
    <Customers/>
    <Suppliers/>
    <TaxTable/>
    <UOMTable/>
    <AnalysisTypeTable/>
    <MovementTypeTable/>
    <Products/>
    <Owners/>
    {frag}
  </MasterFiles>
  <GeneralLedgerEntries/>
  <SourceDocuments>
    <SalesInvoices/>
    <PurchaseInvoices/>
    <Payments/>
    <MovementOfGoods/>
    <AssetTransactions>
      <NumberOfAssetTransactions>0</NumberOfAssetTransactions>
    </AssetTransactions>
  </SourceDocuments>
</AuditFile>"""
