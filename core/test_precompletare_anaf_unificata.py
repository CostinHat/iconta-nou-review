# -*- coding: utf-8 -*-
"""GARD precompletare_anaf_unificata: cele trei cai de creare a unei firme (register, add-firm,
import in masa) folosesc ACELASI helper de precompletare ANAF. Altfel setul de campuri diverge iar
(istoric: data inregistrarii TVA aparea la register dar nu la add-firm/import - Q9)."""
import io


def test_helper_unic_scrie_data_tva():
    prov = io.open("core/tenant_provisioning.py", encoding="utf-8").read()
    assert "def precompleteaza_din_anaf" in prov, "lipseste helperul unic de precompletare ANAF"
    assert "platitor_tva_anaf_inceput" in prov, "helperul nu scrie data inregistrarii TVA (Q9)"
    assert "tva_la_incasare" in prov and "reg_com" in prov, "helperul nu scrie setul complet"


def test_toate_caile_folosesc_helperul():
    # [P7 · valul use-case] Cele trei cai sunt corpuri de ruta, iar corpurile au plecat in
    # `core/uc_*.py`. Se numara in SURSA stratului de aplicatie — intrebarea („toate trei cheama
    # helperul unic?") nu se schimba cu fisierul.
    # [lotul 12, 642] cele trei căi cheamă helperul unic prin `precompleteaza_sau_semnaleaza` (același helper, sub un punct de revenire,
    # în tranzacția creării firmei); acela îl cheamă pe `precompleteaza_din_anaf` — verificat pe AST, nu pe text
    import ast
    from core import scan_sql_efectiv as _efectiv
    aplicatie = _efectiv.sursa_aplicatie()
    assert aplicatie.count("precompleteaza_sau_semnaleaza(") >= 3, \
        "nu toate cele 3 cai de creare firma (register/add-firm/import) cheama helperul unic"
    prov = ast.parse(io.open("core/tenant_provisioning.py", encoding="utf-8").read())
    fn = next(n for n in prov.body if isinstance(n, ast.FunctionDef) and n.name == "precompleteaza_sau_semnaleaza")
    assert [c.func.id for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
            and c.func.id == "precompleteaza_din_anaf"] == ["precompleteaza_din_anaf"], "ajutorul nu cheamă helperul unic"


def test_niciun_snapshot_anaf_inline_in_main():
    # snapshotul ANAF (data curenta) traieste DOAR in helper acum; daca reapare inline in main.py,
    # o cale a inceput iar sa scrie propriul subset -> divergenta revine.
    from core import scan_sql_efectiv as _efectiv
    aplicatie = _efectiv.sursa_aplicatie()
    assert "platitor_tva_anaf_data = CURRENT_DATE" not in aplicatie, (
        "UPDATE firma_profil cu snapshot ANAF a reaparut inline in stratul de aplicatie "
        "(divergenta pe cale)")
