# -*- coding: utf-8 -*-
"""Restrictii pe categorii de active la alegerea metodei de amortizare (CF art.28 alin.5 + alin.8^1).

Legea NU permite orice metoda pe orice activ; motorul (core/d406_active.py) refuza ce legea nu permite.
Legatura cont_imobilizare -> categorie = denumirea contului din OMFP 1802/2014 (in corpus):
  212 Constructii; 2131 Echipamente tehnologice (masini/utilaje/instalatii); 2132 Aparate de masura;
  2133 Mijloace de transport; 2134/217 Animale si plantatii; 214 Mobilier; 211 Terenuri.

Temeiuri verbatim:
  alin.5 lit.a: constructii -> DOAR liniara.
  alin.5 lit.b: echipamente tehnologice/masini/unelte/instalatii de lucru + computere -> lin/deg/accel.
  alin.5 lit.c: orice alt mijloc fix -> lin/deg (FARA accelerata).
  alin.8^1: superaccelerata DOAR subgrupa 2.1 (echipamente) / 2.4 (animale-plantatii), active NOI, PIF 2026.
"""
from datetime import date

import pytest

from core import d406_active as m


def _mf(cont, metoda, pif=date(2025, 12, 20), dnf_luni=60):
    return {"cod": "MF", "denumire": "t", "valoare": 100000, "rezidual": 0, "dnf_luni": dnf_luni,
            "data_pif": pif, "cont_imobilizare": cont, "cont_amortizare": "2813",
            "metoda": metoda, "activ": True}


# (cont, metoda, pif, permis?) — matrice derivata direct din alin.5 / alin.8^1
_P26 = date(2026, 12, 20)   # PIF in 2026 (fereastra superaccelerata)
_P25 = date(2025, 12, 20)
CAZURI = [
    # constructii (212) -> DOAR liniara (lit.a)
    ("212", "liniara", _P25, True),
    ("212", "degresiva", _P25, False),
    ("212", "accelerata", _P25, False),
    ("212", "superaccelerata", _P26, False),
    # echipamente tehnologice (2131) -> lit.b: lin/deg/accel
    ("2131", "liniara", _P25, True),
    ("2131", "degresiva", _P25, True),
    ("2131", "accelerata", _P25, True),
    ("2131", "superaccelerata", _P26, True),   # 2.1 + PIF 2026
    ("2131", "superaccelerata", _P25, False),  # subgrupa OK dar PIF nu-i 2026 -> refuz (fereastra alin.8^1)
    # aparate de masura (2132) -> lit.c: fara accelerata
    ("2132", "liniara", _P25, True),
    ("2132", "degresiva", _P25, True),
    ("2132", "accelerata", _P25, False),
    ("2132", "superaccelerata", _P26, False),
    # mijloace de transport (2133) -> lit.c: fara accelerata
    ("2133", "degresiva", _P25, True),
    ("2133", "accelerata", _P25, False),
    ("2133", "superaccelerata", _P26, False),
    # mobilier (214) -> lit.c: fara accelerata
    ("214", "degresiva", _P25, True),
    ("214", "accelerata", _P25, False),
    # animale/plantatii (2134, subgrupa 2.4) -> lit.c (fara accelerata) DAR superaccel permis (alin.8^1)
    ("2134", "degresiva", _P25, True),
    ("2134", "accelerata", _P25, False),
    ("2134", "superaccelerata", _P26, True),
    ("2134", "superaccelerata", _P25, False),  # PIF nu-i 2026
    ("217", "superaccelerata", _P26, True),    # active biologice = animale/plantatii
    # terenuri (211) -> neamortizabile
    ("211", "liniara", _P25, False),
    # cont lipsa/necunoscut -> lit.c (catch-ul legal): lin/deg da, accel/superaccel nu
    (None, "liniara", _P25, True),
    (None, "degresiva", _P25, True),
    (None, "accelerata", _P25, False),
    ("999", "accelerata", _P25, False),
]


@pytest.mark.parametrize("cont,metoda,pif,permis", CAZURI)
def test_restrictie_categorie(cont, metoda, pif, permis):
    mf = _mf(cont, metoda, pif)
    if permis:
        v = m.calc_asset(mf, pif.year + 1)     # nu ridica -> returneaza valuation
        assert v["depr_period"] >= 0
    else:
        with pytest.raises(ValueError) as ei:
            m.calc_asset(mf, pif.year + 1)
        assert "nu e permisa de lege" in str(ei.value)


def test_constructii_refuza_chiar_si_metoda_scrisa_altfel():
    """Normalizarea nu poate ocoli restrictia: 'ACCELERATA' pe constructie tot refuzata (lit.a)."""
    with pytest.raises(ValueError):
        m.calc_asset(_mf("212", "ACCELERATA"), 2026)


def test_refuzul_se_propaga_in_xml():
    """xml_asset/xml_assets NU emit un activ cu metoda ilegala - ridica ValueError (nu tac)."""
    with pytest.raises(ValueError):
        m.xml_asset(_mf("212", "degresiva"), 2026)
    with pytest.raises(ValueError):
        m.xml_assets([_mf("2131", "liniara"), _mf("212", "accelerata")], 2026)


def test_mesajul_de_refuz_citeaza_temeiul_si_permisele():
    """Mesajul spune categoria, ce e permis si temeiul legal (contabilul intelege de ce)."""
    try:
        m.calc_asset(_mf("2133", "accelerata"), 2026)
        assert False, "trebuia sa ridice"
    except ValueError as e:
        s = str(e)
        assert "transport" not in s or "categorie" in s   # contine categoria dedusa
        assert "permise" in s and "liniara" in s and "degresiva" in s
        assert "art.28" in s


def test_superaccel_pe_transport_citeaza_alin_8_1():
    try:
        m.calc_asset(_mf("2133", "superaccelerata", _P26), 2027)
        assert False
    except ValueError as e:
        assert "8^1" in str(e)
