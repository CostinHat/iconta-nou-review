# -*- coding: utf-8 -*-
"""GARD register_cabinet_cui: la inregistrarea self-service, CUI-ul validat (cel care a trecut
provision_tenant) se persista SI pe accounting_firms.cui, nu doar pe firma-tenant. Altfel
get_cabinet il citeste NULL si ecranul Setari cabinet ramane gol desi userul l-a tastat."""


def _corp_register():
    # [P7 · valul use-case] Corpul lui `register` traieste in `core/uc_auth.py`.
    # Sursa functiei CU CORP, in ordinea straturilor: invelisul din `main.py` n-are decat
    # delegarea, iar munca — provisionarea si scrierea CUI-ului — e in `core/uc_auth.py`.
    # [15.10.2026, lotul 4] pașii de după contul nou (bun venit, anunț, firma din CUI) sunt comuni căii cu invitație și confirmării
    # înregistrării libere: stau în `uc_auth._dupa_cont_nou`, chemat de amândouă — acolo se caută provisionarea și CUI-ul.
    import ast
    from core import scan_sql_efectiv as _efectiv

    def _chemate(nume):
        s = _efectiv.sursa_functiei(nume)
        assert s, "nu gasesc %s in stratul de aplicatie" % nume
        return {x.func.id if isinstance(x.func, ast.Name) else x.func.attr for x in ast.walk(ast.parse(s.strip()))
                if isinstance(x, ast.Call) and isinstance(x.func, (ast.Name, ast.Attribute))}
    # [lotul 12, deficiența 642] firma proprie se creează în tranzacția contului, în `uc_auth._firma_proprie`, chemat de ambele căi
    assert _chemate("register") >= {"_register_cu_invitatie"}
    for ajutor in ("_register_cu_invitatie", "confirma_inregistrarea"):
        assert _chemate(ajutor) >= {"_firma_proprie", "_dupa_cont_nou"}, \
            "%s nu mai trece prin _firma_proprie (firma din CUI s-ar pierde pe o cale)" % ajutor
    src = _efectiv.sursa_functiei("_firma_proprie")
    assert src, "nu gasesc _firma_proprie"
    return src


def test_register_persista_cui_pe_cabinet():
    corp = _corp_register()
    assert "provision_tenant" in corp, "register nu mai provisioneaza firma proprie"
    assert 'actualizeaza_cabinet(conn, r["firm_id"], cui=_cui)' in corp, \
        "register nu persista CUI-ul pe accounting_firms dupa provisionare (cui pierdut pe drum)"
