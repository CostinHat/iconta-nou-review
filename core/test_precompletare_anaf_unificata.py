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
    main = io.open("main.py", encoding="utf-8").read()
    assert main.count("precompleteaza_din_anaf(") >= 3, \
        "nu toate cele 3 cai de creare firma (register/add-firm/import) cheama helperul unic"


def test_niciun_snapshot_anaf_inline_in_main():
    # snapshotul ANAF (data curenta) traieste DOAR in helper acum; daca reapare inline in main.py,
    # o cale a inceput iar sa scrie propriul subset -> divergenta revine.
    main = io.open("main.py", encoding="utf-8").read()
    assert "platitor_tva_anaf_data = CURRENT_DATE" not in main, \
        "UPDATE firma_profil cu snapshot ANAF a reaparut inline in main.py (divergenta pe cale)"
