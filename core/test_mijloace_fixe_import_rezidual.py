# -*- coding: utf-8 -*-
"""GARD — importul de mijloace fixe nu mai pune valoarea RĂMASĂ în `rezidual` (lot 19, defectul 6, 03.10.2026).

Motorul (d406_active.amortizat_la_data / amortizare_luna) amortizează `valoare - rezidual`: rezidualul e partea
NEAMORTIZABILĂ. Importul citea în `rezidual` coloana „rămas / neamortizat” (valoarea netă la export) și, fără nicio
coloană, punea rezidual = valoare — activul preluat nu se mai amortiza deloc. Temeiul: OMFP 1802/2014 pct.139 alin.(2).
"""
import datetime

from core import d406_active
from core.mijloace_fixe_import_api import extrage

ANTET = b"cod;denumire;valoare intrare;valoare ramasa;durata luni;data PIF;metoda;cont imobilizare\n"


def _luni_scurse(pif):
    azi = datetime.date.today()
    return min(60, (azi.year - pif.year) * 12 + azi.month - pif.month)


def test_coloana_ramas_nu_devine_rezidual():
    r = extrage(ANTET + b"MF1;Strung;12000;6000;60;2024-03-15;liniara;2131\n", "m.csv")[0]
    # OMFP 1802/2014 pct.139 alin.(2): „Valoarea amortizabilă este reprezentată de cost” — rămasul nu e rezidual
    assert r["rezidual"] == 0.0
    assert r["amortizat"] == 200.0 * _luni_scurse(datetime.date(2024, 3, 15))


def test_fara_coloana_rezidual_e_zero_nu_valoarea():
    r = extrage(b"cod;denumire;valoare;durata;pif;metoda;cont imobilizare\nMF3;Masina;60000;60;2025-01-10;liniara;2133\n",
                "m.csv")[0]
    # OMFP 1802/2014 pct.139 alin.(2): alocarea valorii amortizabile „pe întreaga durată” — nu zero amortizare
    assert r["rezidual"] == 0.0
    mf = dict(r, data_pif=datetime.date(2025, 1, 10))
    assert d406_active.amortizare_luna(mf, 2026, 10) == 1000


def test_coloana_rezidual_explicita_se_pastreaza():
    r = extrage(b"cod;denumire;valoare intrare;valoare rezidual;durata luni;data PIF;metoda;cont imobilizare\n"
                b"MF2;Autoturism;80000;20000;60;2023-06-01;liniara;2133\n", "m.csv")[0]
    assert (r["valoare"], r["rezidual"]) == (80000.0, 20000.0)


def test_ramas_care_nu_se_leaga_cu_calculul_da_avertisment():
    bun, rau = extrage(ANTET + b"MF1;Strung;12000;%d;60;2024-03-15;liniara;2131\n"
                       b"MF2;Laptop;6000;5900;36;2024-03-15;liniara;2131\n"
                       % (12000 - 200 * _luni_scurse(datetime.date(2024, 3, 15))), "m.csv")
    assert bun["avertismente"] == [] and bun["ok"]
    assert len(rau["avertismente"]) == 1 and not rau["ok"], rau["avertismente"]
    assert rau["avertismente"][0].startswith("valoarea rămasă din fișier (5900.00)"), rau["avertismente"]


def test_ramas_inaintea_valorii_de_intrare_nu_fura_coloana():
    r = extrage(b"cod;denumire;valoare ramasa;valoare intrare;durata luni;data PIF;metoda;cont imobilizare\n"
                b"MF1;Strung;6000;12000;60;2024-03-15;liniara;2131\n", "m.csv")[0]
    assert (r["valoare"], r["rezidual"]) == (12000.0, 0.0)
