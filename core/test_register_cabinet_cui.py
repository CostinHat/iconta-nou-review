# -*- coding: utf-8 -*-
"""GARD register_cabinet_cui: la inregistrarea self-service, CUI-ul validat (cel care a trecut
provision_tenant) se persista SI pe accounting_firms.cui, nu doar pe firma-tenant. Altfel
get_cabinet il citeste NULL si ecranul Setari cabinet ramane gol desi userul l-a tastat."""
import io
import re


def _corp_register():
    src = io.open("main.py", encoding="utf-8").read()
    m = re.search(r"def register\(date: RegisterIn\):([\s\S]+?)\n@app\.", src)
    assert m, "nu gasesc handlerul register in main.py"
    return m.group(1)


def test_register_persista_cui_pe_cabinet():
    corp = _corp_register()
    assert "provision_tenant" in corp, "register nu mai provisioneaza firma proprie"
    assert 'actualizeaza_cabinet(conn, r["firm_id"], cui=_cui)' in corp, \
        "register nu persista CUI-ul pe accounting_firms dupa provisionare (cui pierdut pe drum)"
