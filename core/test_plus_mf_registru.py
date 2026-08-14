# -*- coding: utf-8 -*-
"""#5 (ruptura mijloc-fix post-migrare, plimbare vizuala 14.08.2026): un mijloc fix corporal adaugat prin
'Plus la inventar' trebuie inscris in registrul mijloace_fixe (altfel amortizarea/D406 il sar - capatul
'citeste' exista, capatul 'scrie' lipsea pentru corporale post-migrare). Garda: validarea art.28 alin.5/8^1
pe calea de intrare (pura, fara DB)."""
import pytest
from core import inventariere as iv


def test_plus_mf_refuza_metoda_nepermisa_pe_categorie():
    # constructii (212x): legea permite doar liniara (art.28 alin.5 lit.a) -> degresiva refuzata
    with pytest.raises(ValueError):
        iv.pregateste_mf_plus({"valoare": 500000, "dnf_luni": 480, "data_pif": "2026-03-01",
                               "cont_imobilizare": "212", "metoda": "degresiva"})


def test_plus_mf_accepta_si_normalizeaza():
    reg = iv.pregateste_mf_plus({"valoare": 12000, "dnf_luni": 60, "data_pif": "2025-06-01",
                                 "cont_imobilizare": "2131", "metoda": "liniara", "denumire": "Strung CNC"})
    assert reg["dnf_luni"] == 60
    assert reg["metoda"] == "liniara"
    assert reg["cont_amortizare"] == "2813"
    assert reg["denumire"] == "Strung CNC"
    assert reg["data_pif"].year == 2025


def test_plus_mf_cere_dnf_si_pif():
    with pytest.raises(ValueError):   # fara dnf -> nu se poate amortiza
        iv.pregateste_mf_plus({"valoare": 5000, "data_pif": "2025-01-01", "cont_imobilizare": "2131"})
    with pytest.raises(ValueError):   # fara data pif (si fara 'data')
        iv.pregateste_mf_plus({"valoare": 5000, "dnf_luni": 24, "cont_imobilizare": "2131"})


def test_plus_mf_superaccelerata_doar_2026():
    # 2131 (subgrupa 2.1) + superaccelerata, PIF 2026 -> permis (art.28 alin.8^1, OUG 8/2026)
    reg = iv.pregateste_mf_plus({"valoare": 30000, "dnf_luni": 60, "data_pif": "2026-05-01",
                                 "cont_imobilizare": "2131", "metoda": "superaccelerata"})
    assert reg["metoda"] == "superaccelerata"
    with pytest.raises(ValueError):   # aceeasi metoda, PIF 2025 -> in afara ferestrei 2026
        iv.pregateste_mf_plus({"valoare": 30000, "dnf_luni": 60, "data_pif": "2025-05-01",
                               "cont_imobilizare": "2131", "metoda": "superaccelerata"})
