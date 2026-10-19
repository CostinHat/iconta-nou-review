# -*- coding: utf-8 -*-
"""[deficiența 359, retestul + decizia Costin 9.1 A.1, 19.10.2026, verbatim în DECIZII „Comanda 9.1”] „Importul Mijloace fixe nu citește
coloana «amortizare» din modelul aplicației” și „359: amortizarea continuă cu cifra din fișierul preluat; diferența față de calcul rămâne
doar afișată.” Temei pentru rata de după preluare: CF art.28 alin.(6) („În cazul metodei de amortizare liniară, amortizarea se stabilește
prin aplicarea cotei de amortizare liniară la valoarea fiscală de la data intrării în patrimoniul contribuabilului”) — rata nu se reface.
Activul de probă: 6.000 lei, PIF 15.03.2024, 36 de luni, liniar (rata 166,67), preluat pe 30.09.2026 cu 3.300 lei amortizați (calculul
ar da 5.000,10)."""
import datetime as _dt
from decimal import Decimal

from core import d406_active as a, mijloace_fixe_import_api as imp

MF = {"cod": "MF1", "valoare": 6000, "rezidual": 0, "dnf_luni": 36, "data_pif": _dt.date(2024, 3, 15), "metoda": "liniara",
      "cont_imobilizare": "2131", "amortizare_preluata": 3300, "data_preluare": _dt.date(2026, 9, 30)}


def test_lunile_registrului_vechi_nu_se_mai_inregistreaza():
    assert a.amortizare_luna(MF, 2026, 9) == Decimal("0.00") and a.amortizare_luna(MF, 2025, 5) == Decimal("0.00")


def test_dupa_preluare_rata_metodei_de_la_cifra_din_fisier():
    # CF art.28 alin.(6): 6.000 / 36 = 166,67 pe lună, aceeași rată
    assert a.amortizare_luna(MF, 2026, 10) == Decimal("166.67")
    assert a.amortizat_la_data(MF, _dt.date(2026, 9, 30))["amortizat"] == Decimal("3300.00")   # cifra din fișier, nu 5.000,10
    assert a.amortizat_la_data(MF, _dt.date(2026, 12, 31))["amortizat"] == Decimal("3800.01")  # 3.300 + 3 × 166,67


def test_se_epuizeaza_exact_la_valoarea_amortizabila():
    plan = a._plan_dupa_preluare(MF)
    # (6.000 − 3.300) / 166,67 = 16,2 luni: 16 rate întregi (10/2026 – 01/2028) și restul de 33,28 în 02/2028
    assert len(plan) == 17 and plan[(2028, 2)] == Decimal("33.28") and Decimal(3300) + sum(plan.values()) == Decimal("6000.00")
    assert a.amortizare_luna(MF, 2028, 3) == Decimal("0.00")


def test_cifra_preluata_peste_calcul_se_opreste_mai_devreme():
    mf = dict(MF, amortizare_preluata=5900)
    plan = a._plan_dupa_preluare(mf)
    assert plan == {(2026, 10): Decimal("100.00")}, plan


def test_CALIBRARE_fara_preluare_calculul_e_neschimbat():
    mf = {k: v for k, v in MF.items() if k not in ("amortizare_preluata", "data_preluare")}
    assert a.amortizat_la_data(mf, _dt.date(2026, 9, 30))["amortizat"] == Decimal("5000.10")
    assert a.amortizare_luna(mf, 2026, 9) == Decimal("166.67")


def test_coloana_amortizare_se_citeste():
    t = ("cod;denumire;valoare intrare;data PIF;durata luni;metoda;cont imobilizare;cont amortizare;amortizare;valoare reziduala\n"
         "MF001;Laptop;6000;2024-03-15;36;liniara;2131;2813;3300;0\n").encode()
    r = imp.extrage(t, "mf.csv", data_preluare=_dt.date(2026, 9, 30))[0]
    assert r["amortizat_preluat"] == 3300.0, r
    assert r["motive"] == ["amortizarea preluată (3.300,00 lei) diferă de cea calculată la 30.09.2026 din PIF, durată și metodă (5.000,10 "
                           "lei): verifică data PIF, durata și metoda — după preluare amortizarea continuă de la cifra din fișier, cu rata "
                           "metodei; diferența rămâne doar afișată"], r["motive"]


def test_fara_coloana_randul_o_spune():
    t = ("cod;denumire;valoare intrare;data PIF;durata luni;metoda;cont imobilizare;cont amortizare;amortizare lunara\n"
         "MF001;Laptop;6000;2024-03-15;36;liniara;2131;2813;166,67\n").encode()
    r = imp.extrage(t, "mf.csv", data_preluare=_dt.date(2026, 9, 30))[0]
    assert r["amortizat_preluat"] is None and r["motive"] == [
        "amortizarea cumulată la 30.09.2026 nu e în fișier (nicio coloană „amortizare cumulată” sau „valoare rămasă”): se ia cea calculată "
        "din PIF, durată și metodă, 5.000,10 lei"], r
