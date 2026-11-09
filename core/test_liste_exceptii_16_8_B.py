"""Comanda 16.8-B, pct.5: scripts/verifica_liste_exceptii.py (C226) — FARA_ACTIUNE_PRINCIPALA (cadru.js) față de EXCEPTII_B (verificator_design.py).
Fără Chromium, fără 8019, fără baza de test, fără jurnal de loturi."""
import importlib.util
import json
import os
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CADRU = os.path.join(RAD, "static", "js", "cadru.js")
VERIF = os.path.join(RAD, "scripts", "verificator_design.py")
SCRIPT = os.path.join(RAD, "scripts", "verifica_liste_exceptii.py")


def _incarca():
    spec = importlib.util.spec_from_file_location("verifica_liste_exceptii_16_8_B_%s" % abs(hash(RAD)), SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


VL = _incarca()
TC, TV = open(CADRU, encoding="utf-8").read(), open(VERIF, encoding="utf-8").read()


def _inlocuieste(text, vechi, nou):
    assert text.count(vechi) == 1, vechi
    return text.replace(vechi, nou)


def test_fisierele_reale_sunt_verzi_si_numerele_se_potrivesc():
    assert VL.verifica(TC, TV) == []
    titluri, marcaje = VL.extrage_cadru(TC)
    exceptii = VL.extrage_verificator(TV)
    normale = {VL._normal(n) for n in exceptii}
    assert set(titluri) <= normale
    assert normale - set(titluri) == set(VL.DOAR_PY)
    assert len(marcaje) == len(VL.MARCAJE)


def _refuza(cadru, verificator):
    """-> motivele de refuz; aserțiunile stau în corpul testelor (poarta numără aserțiunile pe test)."""
    return VL.verifica(cadru, verificator)


def _are(motive, *cuvinte):
    return bool(motive) and all(any(c in m for m in motive) for c in cuvinte)


def test_refuza_capacitate_scos_din_cadru():
    assert _are(_refuza(_inlocuieste(TC, "|Capacitate|", "|"), TV), "Capacitate")


def test_refuza_titlu_adaugat_in_cadru():
    assert _are(_refuza(_inlocuieste(TC, "^(Sinteza zilei|", "^(Raportări|Sinteza zilei|"), TV), "Raportări")


def test_refuza_intrare_scoasa_sau_adaugata_in_exceptii():
    assert _are(_refuza(TC, _inlocuieste(TV, '"Sinteza zilei": "stare", ', "")), "Sinteza zilei")
    assert _are(_refuza(TC, _inlocuieste(TV, 'EXCEPTII_B = {', 'EXCEPTII_B = {"Contracte": "stare", ')), "Contracte")


def test_refuza_categorie_diferita_si_supervizor():
    assert _are(_refuza(TC, _inlocuieste(TV, '"Ghiduri": "meniu"', '"Ghiduri": "stare"')), "Ghiduri", "categoria")
    assert _are(_refuza(TC, _inlocuieste(TV, '"Supervizor": "stare", ', "")), "Supervizor", "DOAR_PY")
    assert _are(_refuza(_inlocuieste(TC, "^(Sinteza zilei|", "^(Supervizor|Sinteza zilei|"), TV), "Supervizor", "scoate-l din DOAR_PY")


def test_refuza_marcaj_si_conditie_meniu():
    assert _are(_refuza(_inlocuieste(TC, "· CUI /", "· CIF /"), TV), "marcajele")
    assert _are(_refuza(_inlocuieste(TC, "|| _esteMeniu(corp, bara);", ";"), TV), "_esteMeniu")


def test_refuza_ecranele_cu_actiune():
    assert _are(_refuza(TC, _inlocuieste(TV, 'EXCEPTII_B = {', 'EXCEPTII_B = {"Tipare de erori": "stare", ')), "Tipare de erori", "17.3")
    assert _are(_refuza(_inlocuieste(TC, "^(Sinteza zilei|", "^(Panou Admin — Sănătate server|Sinteza zilei|"), TV), "Panou Admin — Sănătate server", "17.3")


def test_refuza_forma_nerecunoscuta_si_valoare_straina():
    expr = "/^(Sinteza zilei|Capacitate|Operațiuni speciale|Facturi|Firme|Import date)$|· CUI /;"
    assert _are(_refuza(_inlocuieste(TC, expr, 'new Set(["Capacitate"]);'), TV), "nu e recunoscută")
    assert _are(_refuza(TC, _inlocuieste(TV, '"Capacitate": "stare"', '"Capacitate": "altceva"')), "altceva")


def test_cli_cu_copii_in_director_temporar(tmp_path):
    c, v = tmp_path / "cadru.js", tmp_path / "verificator_design.py"
    c.write_text(TC, encoding="utf-8")
    v.write_text(TV, encoding="utf-8")
    ok = subprocess.run([sys.executable, SCRIPT, "--cadru", str(c), "--verificator", str(v)], capture_output=True, text=True)
    assert ok.returncode == 0 and ok.stdout.startswith("[liste exceptii] VERDE: ")
    c.write_text(_inlocuieste(TC, "|Capacitate|", "|"), encoding="utf-8")
    rosu = subprocess.run([sys.executable, SCRIPT, "--cadru", str(c), "--verificator", str(v)], capture_output=True, text=True)
    assert rosu.returncode == 1 and rosu.stdout.startswith("[liste exceptii] REFUZ:") and "Capacitate" in rosu.stdout


def test_hook_apeleaza_scriptul_inaintea_sintaxei():
    h = open(os.path.join(RAD, "scripts", "inainte_de_commit.sh"), encoding="utf-8").read()
    i = h.index("scripts/verifica_liste_exceptii.py")
    assert i < h.index("node --check") and i < h.index("py_compile")


def test_lotul_nu_atinge_produsul():
    sys.path.insert(0, os.path.join(RAD, "scripts"))
    try:
        import jurnal_lot
        if jurnal_lot.lot_curent() != "16.8-B":
            pytest.skip("numai în lotul 16.8-B")
    finally:
        sys.path.remove(os.path.join(RAD, "scripts"))
    baza = json.load(open(os.path.join(RAD, "docs", "dovezi", "16_8_B", "baza.json"), encoding="utf-8"))["antet"]["commit_baza"]
    interzise = ["static/js/cadru.js", "scripts/verificator_design.py", "scripts/verificator_design_masuri.js", "core/catalog_ecrane.json"]
    assert subprocess.run(["git", "diff", "--quiet", baza, "HEAD", "--"] + interzise, cwd=RAD).returncode == 0
    atinse = subprocess.run(["git", "diff", "--name-only", baza, "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.split()
    permise = ("scripts/", "docs/dovezi/16_8_B/")
    fixe = {"core/test_lanseaza_sectiune_16_8_B.py", "core/test_liste_exceptii_16_8_B.py", "CLAUDE.md", "DEFICIENTE.md", "DECIZII.md", "PREDARE_LANT.md"}
    assert [f for f in atinse if not f.startswith(permise) and f not in fixe] == []
