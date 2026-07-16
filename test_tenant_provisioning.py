# -*- coding: utf-8 -*-
"""Teste tenant_provisioning — validarea CUI la crearea unei firme noi.

Gasit prin retestarea sistematica a fluxului Cont&acces (16.07.2026): rutele de
inregistrare (register / register-gratuit) provisionau INAINTE de orice verificare
ANAF (best-effort, except: pass), fara nicio validare offline a cifrei de control -
deci cand ANAF era jos, un CUI malformat devenea tenant real si spargea toate
declaratiile ulterioare. Garda e in provision_tenant (punctul unic prin care trec
ambele rute). Algoritmul de control e din CLAUDE.md / Codul fiscal (obiectiv, lege).
"""
from core import tenant_provisioning as tp


def test_cui_valide():
    # CUI-uri reale, deja acceptate de validatorul oficial DUK in aceasta sesiune
    for c in ("14399840", "4221306", "14837428", "10000016", "20000021", "30000037"):
        assert tp.cui_valid(c), c


def test_cui_accepta_prefix_ro_si_spatii():
    assert tp.cui_valid("RO14399840")
    assert tp.cui_valid(" 14399840 ")


def test_cui_invalide_cifra_control():
    for c in ("10000017", "14399841", "4221307"):
        assert not tp.cui_valid(c), c


def test_cui_invalide_format():
    for c in ("", None, "1", "abcd", "12345678901"):  # gol/None/prea scurt/nenumeric/prea lung
        assert not tp.cui_valid(c), repr(c)
