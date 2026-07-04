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
Amortizare liniara lunara (modulul MF existent): rata = valoare/dnf_luni."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from xml.sax.saxutils import escape

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _luni_intre(d1, an, luna):
    """Luni intregi de amortizare de la luna urmatoare PIF pana la (an, luna) inclusiv."""
    if d1 is None:
        return 0
    n = (an - d1.year) * 12 + (luna - d1.month)
    return max(0, n)

def calc_asset(mf, an):
    """mf: dict {cod, denumire, cont_imobilizare, cont_amortizare, valoare,
    rezidual, dnf_luni, data_pif, metoda, activ}. Returneaza dict Valuation
    pentru anul `an` (amortizare liniara lunara, incepand cu luna urmatoare PIF)."""
    val = _d(mf["valoare"])
    rez = _d(mf.get("rezidual"))
    dnf = int(mf["dnf_luni"])
    if dnf <= 0 or val <= 0:
        raise ValueError(f"MF {mf.get('cod')}: valoare/dnf invalide")
    pif = mf.get("data_pif")
    amortizabil = val - rez
    rata = (amortizabil / dnf).quantize(B, rounding=ROUND_HALF_UP)

    luni_pana_inceput = max(0, min(dnf, _luni_intre(pif, an - 1, 12)))
    luni_pana_sfarsit = max(0, min(dnf, _luni_intre(pif, an, 12)))

    def _am(luni):
        if luni >= dnf:
            return amortizabil
        return (rata * luni).quantize(B, rounding=ROUND_HALF_UP)

    am_inceput = _am(luni_pana_inceput)
    am_sfarsit = _am(luni_pana_sfarsit)
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
<nsSAFT:DepreciationMethod>{e(mf.get('metoda') or 'liniara')}</nsSAFT:DepreciationMethod>
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
