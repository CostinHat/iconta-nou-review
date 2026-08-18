# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 14.4] GARD: intrarile care nu-s CUI NU dispar in tacere la validarea la ANAF.

Provocarea stratului de import 'firme' (lipesti CUI-uri, unul pe linie -> validare la ANAF) a scos un
drop TACUT: o intrare fara nicio cifra ('ABC', un antet de coloana, un typo) era curatata la gol si
eliminata inainte de a ajunge la ANAF -> contabilul lipea 3 randuri, vedea 2, fara niciun semn ca unul
a cazut. E chiar cazul pe care solduri_parteneri il numeste 'tacerea': aici era tacere TOTALA.
separa_cui() intoarce explicit (curatate, ignorate) ca ecranul sa poata arata ce a fost ignorat.
"""
from core import anaf_api


def test_intrarea_ne_cui_e_ignorata_nu_pierduta():
    curatate, ignorate = anaf_api.separa_cui(["14837428", "ABC", "12-34"])
    assert 14837428 in curatate
    assert 1234 in curatate            # '12-34' -> cifrele raman (acceptam separatori)
    assert "ABC" in ignorate           # NU dispare in tacere
    assert len(ignorate) == 1


def test_dedup_nu_e_ignorare():
    """Un CUI repetat (inclusiv cu prefix RO) se dedup - dar NU intra la 'ignorate' (nu-i eroare de contabil)."""
    curatate, ignorate = anaf_api.separa_cui(["14837428", "RO14837428", "14837428"])
    assert curatate == [14837428]
    assert ignorate == []


def test_blank_nu_e_ignorat():
    """Randurile pur goale nu se raporteaza (nu-s intrari reale)."""
    curatate, ignorate = anaf_api.separa_cui(["", "  ", "14837428"])
    assert curatate == [14837428]
    assert ignorate == []


def test_valideaza_cui_pastreaza_comportamentul():
    """Refactorul nu schimba ce CUI-uri curatate vede valideaza_cui (aceleasi ajung la ANAF)."""
    curatate, _ = anaf_api.separa_cui(["RO14837428", "14837428", "abc"])
    assert curatate == [14837428]
