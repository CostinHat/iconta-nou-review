# -*- coding: utf-8 -*-
"""GARD (audit tenant_006): avertismente D390 pe două goluri reale de raportare.
- [Q1a] aceeași operațiune IC pe DOUĂ căi (factură `directie=primita` + linie manuală/din ecranul
  D301 cu același tip/țară/cod/den) -> bazele se ADUNĂ în D390 (dublă raportare). calcul_d390 nu poate
  împiedica introducerea pe ambele căi; trebuie să SEMNALEZE „posibilă DUBLĂ raportare".
- [Q2] factură PRIMITĂ fără CUI furnizor -> exclusă corect din D390 (VIES cere cod TVA valid), dar pentru
  direcția `primita` un CUI gol e SUSPECT (posibilă achiziție IC cu cod lipsă): trebuie NUMITĂ, nu doar
  numărată anonim cu domesticele RO. Direcțional: o VÂNZARE (`emisa`) fără CUI = B2C normal, NU se numește."""
from core.d390 import calcul_d390


def _res(facturi, manual=None):
    prof = {"cui": "RO12345678", "nume": "Firma Test", "telefon": "0211234567"}
    return calcul_d390(prof, 2026, 6, facturi, manual)


def test_q1a_dubla_sursa_semnalata():
    facturi = [{"cui": "DE123456789", "nume": "Furnizor DE", "directie": "primita", "total": 1000, "tva": 0}]
    manual = [{"tip": "A", "tara": "DE", "cod": "123456789", "den": "Furnizor DE", "baza": 1000}]
    res = _res(facturi, manual)
    assert any("DUBL" in a and "raportare" in a for a in res.avertismente), res.avertismente


def test_q1a_o_singura_sursa_fara_fals_pozitiv():
    facturi = [{"cui": "DE123456789", "nume": "Furnizor DE", "directie": "primita", "total": 1000, "tva": 0}]
    res = _res(facturi)  # doar factura, nicio linie manuala -> fara avertisment de dubla sursa
    assert not any("DUBL" in a and "raportare" in a for a in res.avertismente), res.avertismente


def test_q2_primita_fara_cui_numita():
    facturi = [{"cui": "", "nume": "Furnizor fara CUI", "directie": "primita", "total": 500, "tva": 0}]
    res = _res(facturi)
    assert any("PRIMIT" in a and "Furnizor fara CUI" in a for a in res.avertismente), res.avertismente


def test_q2_emisa_fara_cui_nu_e_numita():
    # vanzare (emisa) fara CUI = client PF domestic normal -> NU primeste avertismentul suspect de primita
    facturi = [{"cui": "", "nume": "Client PF", "directie": "emisa", "total": 500, "tva": 0}]
    res = _res(facturi)
    assert not any("PRIMIT" in a and "fără CUI furnizor" in a for a in res.avertismente), res.avertismente
