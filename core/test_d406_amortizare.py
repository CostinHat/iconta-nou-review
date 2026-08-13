# -*- coding: utf-8 -*-
"""Golden pe motorul de amortizare D406/SAF-T (core/d406_active.py), pe metoda.

Inchide DATORIA din test_datorie.py (03.08.2026): calc_asset calcula DOAR liniar;
metoda din activ era ignorata. Acum calc_asset aplica metoda ceruta (CF art.28).

Temeiuri verbatim (anaf_surse/cod_fiscal_227_2015_consolidat.txt, oug_8_2026.txt):
  - alin.6  liniara: cota liniara la valoarea de intrare.
  - alin.7  degresiva: cota liniara x coef (1,5 durata 2-5 ani / 2,0 6-10 ani / 2,5 >10 ani),
            pe valoarea ramasa, cu trecere la liniar pe durata ramasa.
  - alin.8  accelerata: an 1 = max 50%; anii urmatori = valoare ramasa / durata ramasa.
  - alin.8^1 superaccelerata (OUG 8/2026, MO 147/25.02.2026): an 1 = max 65%; rest ca la accelerata.

Restrictiile pe categorii (alin.5) sunt in test_d406_restrictii_metode.py. Aici toate activele
sunt echipamente (cont 2131 = lit.b), ca sa treaca de gardul de categorie si sa probeze DOAR aritmetica.

GOLDEN calculat de mana din lege: activ 100.000 lei, rezidual 0, durata 60 luni (5 ani).
PIF ales ca amortizarea (luna urmatoare PIF) sa inceapa in ianuarie -> anii de utilizare = anii
calendaristici. Liniar/degresiv/accelerat: PIF 20.12.2025 -> din 2026. Superaccelerat cere PIF in 2026
(alin.8^1) -> PIF 20.12.2026 -> din 2027.
"""
from datetime import date
from decimal import Decimal

import pytest

from core import d406_active as m
from core.d406_active import _norm_metoda
from core.mijloace_fixe_import_api import _normalizeaza_metoda


def _mf(metoda, valoare=100000, rezidual=0, dnf_luni=60, pif=None, cont="2131"):
    if pif is None:
        pif = date(2026, 12, 20) if metoda == "superaccelerata" else date(2025, 12, 20)
    return {"cod": "MF-%s" % metoda[:4].upper(), "denumire": "Test %s" % metoda,
            "valoare": valoare, "rezidual": rezidual, "dnf_luni": dnf_luni,
            "data_pif": pif, "cont_imobilizare": cont, "cont_amortizare": "2813",
            "metoda": metoda, "activ": True}


# --- GOLDEN: depr_period pe an, calculat verbatim din lege ---
GOLDEN = {
    "liniara":         {2026: "20000.04", 2027: "20000.04", 2028: "20000.04", 2029: "20000.04", 2030: "19999.84"},
    "degresiva":       {2026: "30000.00", 2027: "21000.00", 2028: "16333.33", 2029: "16333.34", 2030: "16333.33"},
    "accelerata":      {2026: "50000.00", 2027: "12500.00", 2028: "12500.00", 2029: "12500.00", 2030: "12500.00"},
    "superaccelerata": {2027: "65000.00", 2028:  "8750.00", 2029:  "8750.00", 2030:  "8750.00", 2031:  "8750.00"},
}


@pytest.mark.parametrize("metoda", list(GOLDEN))
def test_golden_depr_pe_an(metoda):
    """Amortizarea anuala pe fiecare metoda = valoarea calculata de mana din CF art.28."""
    mf = _mf(metoda)
    for an, asteptat in GOLDEN[metoda].items():
        got = str(m.calc_asset(mf, an)["depr_period"])
        assert got == asteptat, "%s %d: %s != %s" % (metoda, an, got, asteptat)


@pytest.mark.parametrize("metoda", list(GOLDEN))
def test_amortizare_integrala(metoda):
    """Suma amortizarilor = valoarea amortizabila; la sfarsitul vietii book_end=rezidual(0)."""
    mf = _mf(metoda)
    total = sum(m.calc_asset(mf, an)["depr_period"] for an in range(2026, 2033))
    assert total == Decimal("100000.00"), "%s: suma %s" % (metoda, total)
    assert m.calc_asset(mf, 2033)["book_end"] == Decimal("0.00")
    assert m.calc_asset(mf, 2033)["accum_depr"] == Decimal("100000.00")


def test_metoda_chiar_conteaza():
    """Regresie anti-DATORIE: metodele ne-liniare difera de liniara in primul an de amortizare
    (inainte de fix toate dadeau ~20.000)."""
    an1 = {met: m.calc_asset(_mf(met), min(GOLDEN[met]))["depr_period"] for met in GOLDEN}
    assert an1["accelerata"] > an1["liniara"], an1
    assert an1["superaccelerata"] > an1["accelerata"], an1
    assert an1["degresiva"] > an1["liniara"], an1
    assert len(set(an1.values())) == 4, an1


def test_coeficient_degresiv_pe_durata():
    """alin.7: coef 1,5 (2-5 ani), 2,0 (6-10 ani), 2,5 (>10 ani). Primul an, val 100000, rezidual 0.
       an1 degresiv = valoare x cota_liniara x coef (cont 2131 = echipament, degresiv permis)."""
    # 5 ani (60 luni): cota 20%, coef 1,5 -> 30% -> 30.000
    assert m.calc_asset(_mf("degresiva", dnf_luni=60), 2026)["depr_period"] == Decimal("30000.00")
    # 10 ani (120 luni): cota 10%, coef 2,0 -> 20% -> 20.000
    assert m.calc_asset(_mf("degresiva", dnf_luni=120), 2026)["depr_period"] == Decimal("20000.00")
    # 20 ani (240 luni): cota 5%, coef 2,5 -> 12,5% -> 12.500
    assert m.calc_asset(_mf("degresiva", dnf_luni=240), 2026)["depr_period"] == Decimal("12500.00")


def test_superaccel_65_la_suta_primul_an():
    """alin.8^1: an 1 = 65% (PIF in 2026, echipament -> permis; amortizare din 2027)."""
    assert m.calc_asset(_mf("superaccelerata"), 2027)["depr_period"] == Decimal("65000.00")


def test_accelerat_50_la_suta_primul_an():
    """alin.8: an 1 = 50%."""
    assert m.calc_asset(_mf("accelerata"), 2026)["depr_period"] == Decimal("50000.00")


def test_fallback_liniar_sub_2_ani():
    """Durata < 24 luni: metodele ne-liniare nu au sens (alin.7 porneste la 2 ani) -> liniar."""
    mf = _mf("accelerata", dnf_luni=12)   # cont 2131 -> accelerat permis; dar durata < 2 ani -> liniar
    v = m.calc_asset(mf, 2026)
    assert v["accum_depr"] == Decimal("100000.00")
    assert v["depr_period"] == Decimal("100000.00")   # nu 50% ca la accelerat


def test_superaccel_inainte_de_accel_in_ambii_normalizatori():
    """Cerinta explicita: superaccel se verifica INAINTE de acceler in _normalizeaza_metoda."""
    for f in (_norm_metoda, _normalizeaza_metoda):
        assert f("superaccelerata") == "superaccelerata"
        assert f("super accelerata") == "superaccelerata"
        assert f("super-accelerata") == "superaccelerata"
        assert f("accelerata") == "accelerata"
        assert f("degresiva") == "degresiva"
        assert f("liniara") == "liniara"
        assert f("") == "liniara"


def test_xml_contine_metoda_si_sume():
    """XML-ul Asset poarta metoda normalizata si amortizarea pe metoda."""
    xml = m.xml_asset(_mf("superaccelerata"), 2027)
    assert "<nsSAFT:DepreciationMethod>superaccelerata</nsSAFT:DepreciationMethod>" in xml
    assert "<nsSAFT:DepreciationForPeriod>65000.00</nsSAFT:DepreciationForPeriod>" in xml
    xmld = m.xml_asset(_mf("degresiva"), 2026)
    assert "<nsSAFT:DepreciationMethod>degresiva</nsSAFT:DepreciationMethod>" in xmld
    assert "<nsSAFT:DepreciationForPeriod>30000.00</nsSAFT:DepreciationForPeriod>" in xmld
