# -*- coding: utf-8 -*-
"""[lotul 13, pachetul `ops`] Forma dovezilor pe copia firmelor de test (`frontend_test/dovada/dovezi_lot13_ops.json`) și a mutațiilor de
capăt la capăt (`frontend_test/e2e/mut_lot13_ops.json`): o dovadă cu un pas sau o verificare pe care unealta nu le știe ar cădea abia la
rulare; o mutație a cărei ancoră nu mai e în fișier (sau e de două ori) n-ar mai face testul ei roșu.
Temei: N/A — formă de unealtă (CLAUDE.md §4: „rezolvată” = dovadă pe ecran + test permanent în poartă)."""
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOVEZI = os.path.join(RAD, "frontend_test", "dovada", "dovezi_lot13_ops.json")
MUTATII = os.path.join(RAD, "frontend_test", "e2e", "mut_lot13_ops.json")
FIRME_COPIE = {"tenant_9049", "tenant_9050", "tenant_9051", "tenant_9052", "tenant_9053", "tenant_9054", "tenant_9055", "tenant_9057"}


def _pasi():
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    import pasi
    return pasi


def test_dovezile_folosesc_numai_pasii_si_verificarile_uneltei():
    p = _pasi()
    d = json.load(open(DOVEZI, encoding="utf-8"))
    assert len(d) >= 10
    capturi = [x["captura"] for x in d]
    assert len(capturi) == len(set(capturi)), "captură cu același nume la două dovezi"
    for x in d:
        assert x["firma"] in FIRME_COPIE, x["nr"]
        assert x["descriere"] and x["captura"].endswith(".png"), x["nr"]
        for pas in x["pasi"]:
            assert [k for k in pas if k in p.PASI], (x["nr"], pas)
        for v in x["verifica"]:
            assert [k for k in v if k in p.VERIFICARI], (x["nr"], v)


def test_dovezile_pe_datele_dinainte_de_reparatie_au_vechi_in_nume():
    """CLAUDE.md §4: „inclusiv pe documentele create înainte de reparație” — captura lor poartă `vechi` (regula 3a)."""
    d = json.load(open(DOVEZI, encoding="utf-8"))
    assert {x["nr"] for x in d if "vechi" in x["captura"]} >= {"522", "518", "527", "533", "541"}


def test_mutatiile_au_ancora_unica_si_testul_lor():
    m = json.load(open(MUTATII, encoding="utf-8"))
    teste = open(os.path.join(RAD, "frontend_test", "e2e", "e2e_lot13_ops.py"), encoding="utf-8").read()
    assert len(m) >= 20
    for x in m:
        assert open(os.path.join(RAD, x["fisier"]), encoding="utf-8").read().count(x["ancora"]) == 1, x["test"]
        assert x["inlocuire"] != x["ancora"]
        fis, nume = x["test"].split("::")
        assert fis == "frontend_test/e2e/e2e_lot13_ops.py" and ("def %s(" % nume) in teste, x["test"]
