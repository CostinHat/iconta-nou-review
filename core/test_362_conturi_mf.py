# -*- coding: utf-8 -*-
"""[deficiența 362, retestul + decizia Costin 9.1 A.2, 19.10.2026] Import MF: conturile inversate (2813 ca imobilizare) intrau; terenul 2111
intra cu amortizare liniară pe 60 de luni; 2112 era respins ca „teren”, cu un mesaj despre C&D. Decizia A.2: „2112 (amenajări de
terenuri) se amortizează — CF art.28: liniar, 10 ani. Numai 2111 nu.”
Temei: CF art.28 alin.(4) lit.a): „Nu reprezintă active amortizabile: a) terenurile, inclusiv cele împădurite”; alin.(3) lit.f):
„amenajările de terenuri” sunt mijloace fixe amortizabile; alin.(12) lit.e): „pentru cheltuielile cu investițiile efectuate pentru
amenajarea terenurilor, liniar, pe o perioadă de 10 ani”."""
import datetime as _dt
from decimal import Decimal

import pytest

from core import d406_active as a, mijloace_fixe_import_api as imp

ANTET = "cod;denumire;valoare intrare;data PIF;durata luni;metoda;cont imobilizare;cont amortizare\n"


def _er(linie):
    r = imp.extrage((ANTET + linie + "\n").encode(), "mf.csv", data_preluare=_dt.date(2026, 9, 30))
    return [(e["regula"], e["mesaj"]) for e in imp.verifica_randuri(r)]


def test_conturi_inversate_respinse():
    er = _er("MF1;Strung;5000;2024-03-15;36;liniara;2813;2131")
    assert er == [("cont_imobilizare_invalid", "Strung: contul 2813 nu e un cont de imobilizări necorporale (20x) sau corporale (21x) — e "
                                               "un cont de amortizare; contul de imobilizare și cel de amortizare par inversate")], er


def test_terenul_cu_durata_respins():
    er = _er("MF2;Teren;50000;2020-01-10;60;liniara;2111;")
    # CF art.28 alin.(4) lit.a)
    assert er == [("durata_teren", "Teren: terenul (contul 2111) nu se amortizează (CF art.28 alin.(4) lit.a)) — durata trebuie să fie 0 sau "
                                   "goală, nu 60 de luni")], er


def test_amenajarea_de_teren_pe_10_ani_intra_si_se_amortizeaza_liniar():
    assert _er("MF3;Amenajare;12000;2024-01-10;120;liniara;2112;2811") == []
    mf = {"cod": "MF3", "valoare": 12000, "rezidual": 0, "dnf_luni": 120, "data_pif": _dt.date(2024, 1, 10), "metoda": "liniara",
          "cont_imobilizare": "2112"}
    assert a.amortizare_luna(mf, 2024, 2) == Decimal("100.00")   # alin.(12) lit.e): liniar, 10 ani -> 12.000 / 120


def test_amenajarea_pe_alta_durata_sau_degresiv_respinsa_fara_cd():
    er = _er("MF4;Alee;6000;2024-01-10;60;liniara;2112;2811")
    assert er == [("durata_amenajare_teren", "Alee: amenajările de terenuri (contul 2112) se amortizează liniar pe 10 ani, adică 120 de luni "
                                             "(CF art.28 alin.(12) lit.e)), nu 60 de luni")], er
    mf = {"cod": "MF5", "valoare": 6000, "rezidual": 0, "dnf_luni": 120, "data_pif": _dt.date(2024, 1, 10), "metoda": "degresiva",
          "cont_imobilizare": "2112"}
    with pytest.raises(ValueError) as e:
        a.amortizare_luna(mf, 2024, 2)
    assert str(e.value) == ("Mijlocul fix MF5 (contul 2112, deci amenajare de teren, CF art.28 alin.(12) lit.e)): metoda degresivă nu e "
                            "permisă de lege; permise: liniară. Temei: CF art.28 alin.(12) lit.e): amenajările de terenuri se amortizează "
                            "liniar, pe 10 ani."), str(e.value)   # fără C&D
