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
                     "(animale/plantatii), active NOI puse in functiune in 2026")
        raise ValueError(
            "MF %s (cont %s -> categorie '%s'): metoda '%s' nu e permisa de lege; permise: %s. Temei: %s."
            % (mf.get("cod"), cont, categorie, metoda,
               (", ".join(sorted(permise)) or "niciuna (activ neamortizabil)"), temei))


def calc_asset(mf, an):
    """mf: dict {cod, denumire, cont_imobilizare, cont_amortizare, valoare,
    rezidual, dnf_luni, data_pif, metoda, activ}. Returneaza dict Valuation pentru anul `an`.
    Metoda din activ decide calculul (CF art.28). Amortizarea incepe cu luna urmatoare PIF."""
    val = _d(mf["valoare"])
    rez = _d(mf.get("rezidual"))
    dnf = int(mf["dnf_luni"])
    if dnf <= 0 or val <= 0:
        raise ValueError(f"MF {mf.get('cod')}: valoare/dnf invalide")
    pif = mf.get("data_pif")
    amortizabil = val - rez
    metoda = _norm_metoda(mf.get("metoda"))
    _verifica_categorie(mf, metoda, pif)   # alin.5/8^1: ce legea nu permite pe categorie -> refuza

    if metoda == "liniara" or dnf < _MIN_LUNI_NELINIAR:
        # liniara (alin.6) - si fallback pentru durate sub 2 ani, unde metodele ne-liniare nu au sens
        rata = (amortizabil / dnf).quantize(B, rounding=ROUND_HALF_UP)
        luni_pana_inceput = max(0, min(dnf, _luni_intre(pif, an - 1, 12)))
        luni_pana_sfarsit = max(0, min(dnf, _luni_intre(pif, an, 12)))

        def _am(luni):
            if luni >= dnf:
                return amortizabil
            return (rata * luni).quantize(B, rounding=ROUND_HALF_UP)

        am_inceput = _am(luni_pana_inceput)
        am_sfarsit = _am(luni_pana_sfarsit)
    else:
        luni = _amort_lunar_neliniar(metoda, amortizabil, dnf)
        am_inceput = min(amortizabil, _accum_neliniar(luni, pif, an - 1)).quantize(B, rounding=ROUND_HALF_UP)
        am_sfarsit = min(amortizabil, _accum_neliniar(luni, pif, an)).quantize(B, rounding=ROUND_HALF_UP)

    achizitie_in_an = bool(pif and pif.year == an)
    return {
        "cost_begin": Decimal("0.00") if achizitie_in_an else val,
        "cost_end": val,
        "addition": val if achizitie_in_an else Decimal("0.00"),
        "book_begin": (Decimal("0.00") if achizitie_in_an else val - am_inceput).quantize(B),
        "depr_period": (am_sfarsit - am_inceput).quantize(B),
        "accum_depr": am_sfarsit,
        "book_end": (val - am_sfarsit).quantize(B),
        "procent_anual": (Decimal("100") * 12 / dnf).quantize(B, rounding=ROUND_HALF_UP),
    }

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
<nsSAFT:AppreciationForPeriod>0.00</nsSAFT:AppreciationForPeriod>
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
