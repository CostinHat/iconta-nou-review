# -*- coding: utf-8 -*-
"""TURA 4 (CR-5/T8): oglinda rd.12 <-> rd.25 la taxare inversa PRIMITA (masuri de simplificare).

GAP (reconciliere / cross-total): R12 (colectat prin taxare inversa) FARA oglinda R25 (deductibil)
trece AZI si prin generator (calea manuala) SI prin validatorul DUK INSTALAT - regulile V19/V20
(R25=R12) NU sunt impuse, iar reconcilierea a-doua-cale SARE randurile manuale. Rezultat: TVA
colectata supra-declarata, net != 0, TVA de plata umflata. Nimeni nu prinde.

Sursa oficiala confruntata (anaf_surse/d300_struct_anaf.txt):
  V_19  R25_1 = R12_1   ERR: rd.25<>rd.12 (col.1)
  V_20  R25_2 = R12_2   ERR: rd.25<>rd.12 (col.2)
Colectatul rd.12 (achizitii supuse masurilor de simplificare, art.331) trebuie oglindit INTEGRAL de
deductibilul rd.25 -> net zero.

FIX (core/d300.py): _oglinda_r12_r25(res) impune R25_1==R12_1 si R25_2==R12_2; cablat in genereaza()
la aceeasi poarta ca reconcilierea, INAINTE de build_xml. Divergenta -> ValueError care numeste AMBELE
valori + \"DUK regula V19/V20 (neimpusa de validatorul instalat)\". Auto-derivarea corecta (net zero din
facturi cu flag taxare_inversa) NU e atinsa.
"""
import pytest
from core.common import Perioada
from core import d300
from core.d300 import calcul_d300, _oglinda_r12_r25


def _prof():
    return {"cui": "14399840", "nume": "PROBA SRL", "banca": "BCR",
            "iban": "RO49AAAA1B31007593840000", "cont": "RO49AAAA1B31007593840000",
            "caen": "4711", "tip_decont": "L", "pro_rata": 100,
            "declarant_nume": "POPESCU", "declarant_prenume": "ION"}


def _fact_rc(baza=1000, cota=21):
    return {"directie": "primita", "taxare_inversa": True, "linii": [(1, baza, cota)]}


def _res_cu(**R):
    r = d300.Rezultat(an=2026, luna=8, prof=_prof())
    r.R = dict(R)
    return r


def _duk_ok():
    try:
        from core import duk
        return duk
    except Exception:
        return None


# ---------------------------------------------------------------------------
#  GAP: DUK INSTALAT accepta R12 fara R25 (V19/V20 neimpuse). XML construit direct
#  (build_xml), reproducand EXACT randurile pe care generatorul le emitea pe calea
#  manuala inainte de gard - altfel poarta din genereaza ar bloca inainte de DUK.
# ---------------------------------------------------------------------------
def test_GAP_duk_instalat_accepta_R12_fara_R25():
    duk = _duk_ok()
    if duk is None:
        pytest.skip("modul duk indisponibil")
    # R12 colectat -> R17; fara R25 -> R27/R32=0; lantul rezultat R34/R37/R41 = 2100 (TVA de plata umflata).
    res = _res_cu(R12_1=10000, R12_2=2100, R17_1=10000, R17_2=2100,
                  R34_2=2100, R37_2=2100, R41_2=2100)
    res.total_plata_a = sum(res.R.values())
    r = duk.valideaza(d300.build_xml(res), "d300", an=2026, luna=8, timeout=110)
    assert r["stare"] == "valid", ("DUK ar trebui sa accepte gapul (V19/V20 neimpus)", r)


# ---------------------------------------------------------------------------
#  MUTATIE prin GENEREAZA (poarta reala): R12 fara R25 -> ACUM RIDICA.
#  _oglinda ruleaza inainte de reconciliere, deci conn=None e ok (ridica pre-conn).
# ---------------------------------------------------------------------------
def test_MUTATIE_R12_fara_R25_ridica_in_genereaza(monkeypatch):
    monkeypatch.setattr(d300, "pull", lambda conn, schema, perioada: (_prof(), []))
    with pytest.raises(ValueError) as ei:
        d300.genereaza(None, "tenant_013", Perioada(2026, luna=8),
                       {"R12_1": 10000, "R12_2": 2100})
    m = str(ei.value)
    assert "DUK regula V19/V20" in m, m
    assert "R12_2=2100" in m and "R25_2=0" in m, m   # numeste AMBELE valori


# ---------------------------------------------------------------------------
#  MUTATIE (unit pe helper): variante de rupere a oglinzii -> RIDICA.
# ---------------------------------------------------------------------------
def test_MUTATIE_R12_fara_R25_helper():
    with pytest.raises(ValueError) as ei:
        _oglinda_r12_r25(_res_cu(R12_1=10000, R12_2=2100))
    assert "DUK regula V19/V20" in str(ei.value)


def test_MUTATIE_R25_fara_R12_helper():
    """Simetric: deductibil fara colectat = tot rupere de oglinda."""
    with pytest.raises(ValueError) as ei:
        _oglinda_r12_r25(_res_cu(R25_1=10000, R25_2=2100))
    assert "DUK regula V19/V20" in str(ei.value)


def test_MUTATIE_R12_diferit_de_R25_helper():
    """R12 != R25 (inegal, nu doar lipsa) -> ridica, numind ambele valori."""
    with pytest.raises(ValueError) as ei:
        _oglinda_r12_r25(_res_cu(R12_1=10000, R12_2=2100, R25_1=10000, R25_2=999))
    m = str(ei.value)
    assert "R12_2=2100" in m and "R25_2=999" in m, m


# ---------------------------------------------------------------------------
#  VALID: net-zero (auto-derivat) trece gardul + DUK-valid. Auto-derivarea neatinsa.
# ---------------------------------------------------------------------------
def test_VALID_net_zero_autoderivat_trece_gardul():
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [_fact_rc(40000, 21)])
    assert (res.R.get("R12_1"), res.R.get("R12_2")) == (40000, 8400)
    assert (res.R.get("R25_1"), res.R.get("R25_2")) == (40000, 8400)
    assert res.tva_de_plata == 0 and res.tva_de_recuperat == 0
    assert res.R.get("R17_2") == res.R.get("R27_2") == 8400
    _oglinda_r12_r25(res)   # nu ridica


def test_VALID_net_zero_autoderivat_duk_valid():
    duk = _duk_ok()
    if duk is None:
        pytest.skip("modul duk indisponibil")
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [_fact_rc(40000, 21)])
    r = duk.valideaza(d300.build_xml(res), "d300", an=2026, luna=8, timeout=110)
    assert r["stare"] == "valid", r


def test_VALID_manual_oglinda_egala_trece_si_duk_valid():
    """Calea manuala corecta: R12 SI R25 egale -> trece gardul, net zero, DUK-valid."""
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [],
                      {"R12_1": 10000, "R12_2": 2100, "R25_1": 10000, "R25_2": 2100})
    assert res.R.get("R17_2") == res.R.get("R27_2") == 2100
    assert res.tva_de_plata == 0
    _oglinda_r12_r25(res)   # nu ridica
    duk = _duk_ok()
    if duk is None:
        pytest.skip("modul duk indisponibil")
    r = duk.valideaza(d300.build_xml(res), "d300", an=2026, luna=8, timeout=110)
    assert r["stare"] == "valid", r
