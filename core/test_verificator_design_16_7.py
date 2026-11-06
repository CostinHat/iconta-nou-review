# -*- coding: utf-8 -*-
"""Lotul 16.7 (unelte) — rândurile a și b ale verificatorului de design (759, 760), agregatorul matricei, registrul completat, perimetrul lotului, comparația de praguri
din publica_lot.py (rulările „intrerupt”) și plasa din poarta_lib.py (cod nenul fără raport junit proaspăt = ROȘU). Fără Chromium.
(4) și (5) rulează numai când lotul curent e 16.7 (ieșirile calibrării și ale matricei există); cu VERIFICATOR_RAD_16_7 setată rulează numai (1) și (2)."""
import importlib.util
import json
import os
import subprocess
import sys
import textwrap

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAD_VERIFICAT = os.environ.get("VERIFICATOR_RAD_16_7") or RAD
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_7")
sys.path.insert(0, os.path.join(RAD, "scripts"))
SARE_CU_RAD = pytest.mark.skipif(bool(os.environ.get("VERIFICATOR_RAD_16_7")), reason="rădăcină verificată dată: numai (1) și (2)")


def _incarca(cale, nume, rad):
    """Încarcă un modul din rădăcina `rad`, cu nume unic și cu scripts/ al ei primul în sys.path (importurile lui dintre scripturi vin din aceeași rădăcină)."""
    scripts = os.path.join(rad, "scripts")
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location("%s_%s" % (nume, abs(hash(rad))), os.path.join(scripts, cale))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        sys.path.remove(scripts)


def _lot_curent():
    import jurnal_lot
    return jurnal_lot.lot_curent()


# ── (1) criteriul și promptul ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_randurile_a_si_b_cer_x_si_actiunea_o_singura_data_iar_promptul_le_repeta():
    V = _incarca("verificator_design.py", "vd167", RAD_VERIFICAT)
    a, b = V.RANDURI["a"], V.RANDURI["b"]
    assert "✕" in a and "40 × 40" in a and "nu apare în bara de sus" not in a
    assert "o singură dată pe ecran" in b
    V.RAD = RAD_VERIFICAT   # promptul se citește din rădăcina verificată
    p = V.prompt(["Control fiscal"], "/tmp/x")
    assert a in p and b in p


# ── (2) agregatorul matricei ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _js(a=(), b=(), eroare=None):
    return {"pica": {"a": list(a), "b": list(b)}, "eroare_deschidere": eroare}


@pytest.mark.parametrize("js_pe_rez,asteptat", [
    ((_js(), _js()), ("VERDE", "VERDE")),
    ((_js(a=["lipsește „✕” (închidere) în dreapta sus a barei de sus"]), _js()), ("ROSU", "VERDE")),
    ((_js(a=["x"]), _js(b=["acțiunea principală „X” apare și în conținut (2 ori pe ecran)"])), ("ROSU", "ROSU")),
    (("timeout", _js(a=["x"])), ("NEDESCHIS", "NEDESCHIS")),      # NEDESCHIS+ROSU
    ((None, _js()), ("NEDESCHIS", "NEDESCHIS")),                  # NEDESCHIS+VERDE: JSON lipsă
    ((_js(eroare="pasul n-a găsit butonul"), _js()), ("NEDESCHIS", "NEDESCHIS")),
    ((_js(a=["nicio fereastră de lucru deschisă"], b=["nicio fereastră de lucru deschisă"]), _js()), ("NEDESCHIS", "NEDESCHIS")),
])
def test_agregatorul_matricei_cu_precedenta_nedeschis_rosu_verde(js_pe_rez, asteptat):
    M = _incarca("matrice_16_7.py", "mx167", RAD_VERIFICAT)
    a, b, _ = M.rand_intrare("Un ecran", dict(zip(("1920x1080", "1366x768"), js_pe_rez)))
    assert (a, b) == asteptat


def test_matricea_precedenta_la_nivel_de_rand_si_cele_patru_cauze_de_nedeschis():
    M = _incarca("matrice_16_7.py", "mx167b", RAD_VERIFICAT)
    assert M.agrega(["VERDE", "VERDE"]) == "VERDE" and M.agrega(["ROSU", "VERDE"]) == "ROSU"
    assert M.agrega(["NEDESCHIS", "ROSU"]) == "NEDESCHIS" and M.agrega(["NEDESCHIS", "VERDE"]) == "NEDESCHIS"
    cauze = {"JSON lipsă": None, "timeout": M.STARE_TIMEOUT, "eroare": _js(eroare="eroare"), "fără fereastră": _js(a=["nicio fereastră de lucru deschisă"])}
    for nume, js in cauze.items():
        assert M.evalueaza(js, "a")[0] == "NEDESCHIS", nume
    # motivul: o dată dacă e la fel la ambele rezoluții, altfel cu rezoluția
    la_fel = M.rand_intrare("E", {"1920x1080": _js(a=["m"]), "1366x768": _js(a=["m"])})[2]
    diferit = M.rand_intrare("E", {"1920x1080": _js(a=["m"]), "1366x768": _js()})[2]
    assert la_fel == "a: m" and diferit == "a (1920x1080): m"
    # fereastra mică: numai motivele „✕”, rândul b = „-”
    mica = M.rand_intrare(M.FEREASTRA_MICA, {r: _js(a=["firma sau cabinetul în lucru nu apare cu CUI", "„✕” nu e de 40 × 40 (34 × 34)"], b=["x"]) for r in ("1920x1080", "1366x768")})
    assert mica[:2] == ("ROSU", "-") and "CUI" not in mica[2]


# ── (3) registrul ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@SARE_CU_RAD
def test_registrul_are_cele_unsprezece_nume_noi_si_detaliul_factura_fara_acelasi_ca():
    reg = json.load(open(os.path.join(RAD, "core", "catalog_ecrane.json"), encoding="utf-8"))
    V = _incarca("verificator_design.py", "vd167r", RAD)
    nume = [e["nume"] for e in reg]
    noi = ["Declarație %s F1 pasul 2" % d for d in "D104 D107 D110 D114 D177 D205 D307 D398 D710".split()] + ["Declarație D301 F3 pasul 2", "Fereastră mică — confirmare storno F1"]
    assert all(n in nume for n in noi)
    detaliu = next(e for e in reg if e["nume"] == "Detaliu factură F1")
    assert "acelasi_ca" not in detaliu and len(detaliu["pasi"]) == 4
    assert len(set(nume)) == len(nume) and len({V.slug(n) for n in nume}) == len(nume)
    assert len(reg) == 105


# ── (4) ieșirile calibrării și ale matricei, pe același P ─────────────────────────────────────────────────────────────────────────────────
def _git(*a):
    return subprocess.run(["git", *a], cwd=RAD, capture_output=True, text=True, check=True).stdout


@SARE_CU_RAD
def test_iesirile_poarta_acelasi_p_si_matricea_are_forma_ceruta():
    if _lot_curent() != "16.7":
        pytest.skip("lotul curent nu e 16.7")
    import hashlib
    prime = []
    for f in ("calibrare/calibrare_a.txt", "calibrare/calibrare_b.txt", "calibrare/regresie.txt", "matrice_inainte/sha.txt"):
        cale = os.path.join(DOVEZI, f)
        assert os.path.exists(cale), f
        prime.append(open(cale, encoding="utf-8").readline().split())
    sha = {p[0] for p in prime}
    assert len(sha) == 1, prime
    p = sha.pop().split("=")[1]
    for linie in prime:
        for camp in linie[1:]:
            fisier, h = camp.split("=")
            assert hashlib.sha256(open(os.path.join(RAD, fisier), "rb").read()).hexdigest() == h, fisier
    assert subprocess.run(["git", "merge-base", "--is-ancestor", p, "HEAD"], cwd=RAD).returncode == 0
    assert subprocess.run(["git", "diff", "--quiet", p, "HEAD", "--", "scripts/verificator_design.py", "scripts/verificator_design_masuri.js", "scripts/calibreaza_16_7.py",
                           "scripts/matrice_16_7.py", "core/catalog_ecrane.json"], cwd=RAD).returncode == 0
    reg = json.load(open(os.path.join(RAD, "core", "catalog_ecrane.json"), encoding="utf-8"))
    linii = open(os.path.join(DOVEZI, "matrice_inainte.csv"), encoding="utf-8").read().splitlines()
    assert linii[0] == "ecran,rand a,rand b,motiv"
    import csv
    randuri = list(csv.reader(linii[1:]))
    assert [r[0] for r in randuri] == [e["nume"] for e in reg]
    assert len([f for f in os.listdir(os.path.join(DOVEZI, "matrice_inainte")) if f.endswith(".json")]) == 2 * len(reg)


# ── (5) perimetrul lotului ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@SARE_CU_RAD
def test_diff_ul_lotului_ramane_in_fisierele_permise():
    if _lot_curent() != "16.7":
        pytest.skip("lotul curent nu e 16.7")
    import publica_lot as PL
    baza = json.load(open(os.path.join(DOVEZI, "baza.json"), encoding="utf-8"))["antet"]["commit_baza"]
    permise = PL.lista_permisa(open(os.path.join(RAD, "scripts", "praguri_16_7.txt"), encoding="utf-8").read())
    for f in _git("diff", "--name-only", baza, "HEAD").split():
        ok = any(f == p or (p.endswith("/") and f.startswith(p)) for p in permise) or f == "core/test_verificator_design_16_7.py" or f.startswith("docs/dovezi/16_7/")
        assert ok, f


# ── (6) comparația de praguri ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
@SARE_CU_RAD
def test_pragul_ignora_rularile_intrerupte_si_numara_intreruptele_pe_faza():
    import publica_lot as PL   # modulul din worktree-ul lotului, nu o copie
    praguri = ["unelte", "max poarta_pytest 600"]
    intrerupta = [("poarta_pytest", "1", "i", "-", "intrerupt", 618)]
    stop, intrerupte = PL.depasiri_praguri(intrerupta, praguri)
    assert stop == [] and intrerupte == {"poarta_pytest": 1}
    terminata = intrerupta + [("poarta_pytest", "2", "i", "s", "verde", 700)]
    stop, intrerupte = PL.depasiri_praguri(terminata, praguri)
    assert len(stop) == 1 and "700" in stop[0] and intrerupte == {"poarta_pytest": 1}
    assert PL.depasiri_praguri([("poarta_pytest", "3", "i", "s", "verde", 500)], praguri) == ([], {})


# ── (7) plasa: cod nenul fără raport junit proaspăt = ROȘU ────────────────────────────────────────────────────────────────────────────────
XML_VECHI = """<testsuites><testsuite><testcase classname="a" name="t1"><failure message="vechi"/></testcase><testcase classname="a" name="t2"><failure message="vechi"/></testcase></testsuite></testsuites>"""


def _wt(tmp_path, cod_e2e):
    """Worktree fals: baza_test.sh gol (restaureaza nu face nimic), e2e_poarta.py fals cu codul `cod_e2e`, venv al depozitului; niciodată worktree-ul real."""
    wt, j = tmp_path / "wt", tmp_path / "J"
    (wt / "scripts" / "bin").mkdir(parents=True)
    j.mkdir()
    (wt / "scripts" / "baza_test.sh").write_text("#!/bin/sh\nexit 0\n")
    (wt / "scripts" / "e2e_poarta.py").write_text("import sys\nsys.exit(%d)\n" % cod_e2e)
    os.symlink(os.path.join(RAD, "venv"), wt / "venv")
    (j / "poarta_e2e.xml").write_text(XML_VECHI)
    return str(wt), str(j)


@SARE_CU_RAD
@pytest.mark.parametrize("cod", [3, 1])
def test_plasa_cu_cod_nenul_fara_xml_nou_e_rosu_nu_picaturi_restante_vechi(tmp_path, cod):
    import poarta_lib as L
    wt, j = _wt(tmp_path, cod)
    trepte, teste = L.ruleaza_trepte(wt, j, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False, sonda_8019=lambda: False, opreste_8019=lambda: None)
    pica = [t for t in teste if t["rezultat"] == "pica"]
    assert [t["nume"] for t in pica] == ["plasa_e2e::sesiune"] and pica[0]["infra"], teste   # xml-ul vechi cu 2 picături n-a fost citit
    assert not os.path.exists(os.path.join(j, "poarta_e2e.xml"))


@SARE_CU_RAD
def test_plasa_opreste_8019_cand_raspunde_si_continua(tmp_path):
    import poarta_lib as L
    wt, j = _wt(tmp_path, 3)
    opriri = []
    _, teste = L.ruleaza_trepte(wt, j, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False, sonda_8019=lambda: True, opreste_8019=lambda: opriri.append(1))
    assert opriri == [1] and any(t["rezultat"] == "pica" for t in teste)
    opriri.clear()
    L.ruleaza_trepte(wt, j, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False, sonda_8019=lambda: False, opreste_8019=lambda: opriri.append(1))
    assert opriri == []
