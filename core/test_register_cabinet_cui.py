# -*- coding: utf-8 -*-
"""GARD register_cabinet_cui: la inregistrarea self-service, CUI-ul validat (cel care a trecut
provision_tenant) se persista SI pe accounting_firms.cui, nu doar pe firma-tenant. Altfel
get_cabinet il citeste NULL si ecranul Setari cabinet ramane gol desi userul l-a tastat."""


def _corp_register():
    # [P7 · valul use-case] Corpul lui `register` traieste in `core/uc_auth.py`.
    # Sursa functiei CU CORP, in ordinea straturilor: invelisul din `main.py` n-are decat
    # delegarea, iar munca — provisionarea si scrierea CUI-ului — e in `core/uc_auth.py`.
    from core import scan_sql_efectiv as _efectiv
    src = _efectiv.sursa_functiei("register")
    assert src, "nu gasesc handlerul register in stratul de aplicatie"
    return src


def test_register_persista_cui_pe_cabinet():
    corp = _corp_register()
    assert "provision_tenant" in corp, "register nu mai provisioneaza firma proprie"
    assert 'actualizeaza_cabinet(conn, r["firm_id"], cui=_cui)' in corp, \
        "register nu persista CUI-ul pe accounting_firms dupa provisionare (cui pierdut pe drum)"
