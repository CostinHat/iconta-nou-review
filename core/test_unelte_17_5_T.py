# -*- coding: utf-8 -*-
"""Lotul 17.5-T (unelte): probele uneltelor noi, pe jurnale și loguri false, pe treptele false ale porții și pe o clonă temporară.
  T.5  scripts/infra_g2.py (decizia pură), scripts/publica_lot.py::depasiri_praguri, scripts/jurnal_lot.py::_rez_run și marcaje_g2, scripts/poarta_rulare.py::remasoara_g2
  T.6  scripts/poarta_lib.py::ruleaza_trepte (proba de mediu înaintea plasei), scripts/poarta_rulare.py::decide (infra ×3)
  T.8  scripts/poarta_rulare.py (proba de contract la începutul oricărei rulări)
  T.2  scripts/verifica_lista_17_5_T.py (garda aserțiunilor testelor din listă)"""
import datetime
import json
import os
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import infra_g2 as IG  # noqa: E402
import jurnal_lot as JL  # noqa: E402
import poarta_lib as L  # noqa: E402
import poarta_rulare as PR  # noqa: E402
import publica_lot as PL  # noqa: E402

BAZA_ORA = datetime.datetime(2026, 11, 11, 15, 0, 0)


# ── T.5: logul în formatul real al veghei ────────────────────────────────────────────────────────────────────────
def _stamp(minut, faza="poarta_plasa", baza=BAZA_ORA):
    return "%s faza=%s load=1.20 0.90 0.80" % ((baza + datetime.timedelta(minutes=minut)).strftime("%F %H:%M:%S"), faza)


def _strain(pid, cpu_secunde, comanda="python3 /home/costin/alt_proiect/ruleaza.py", procent=12):
    return "   strain: pid %d cputimes %d %s (cpu %d%%)" % (pid, cpu_secunde, comanda, procent)


def _log(*stampuri):
    """stampuri = [(minut, [(pid, cputimes[, comanda])])] -> textul logului."""
    linii = []
    for minut, procese in stampuri:
        linii.append(_stamp(minut))
        linii += [_strain(*x) for x in procese]
    return "\n".join(linii) + "\n"


def _iso(minut, secunde=0, baza=BAZA_ORA):
    return (baza + datetime.timedelta(minutes=minut, seconds=secunde)).astimezone().isoformat(timespec="seconds")


FEREASTRA = (_iso(-1), _iso(40))
PRAG = 1000


def _decide(text, faza="poarta_plasa", durata=1500):
    return IG.decide(faza, durata, PRAG, FEREASTRA[0], FEREASTRA[1], text)


def test_g2_acelasi_proces_peste_30_pe_doua_intervale_consecutive_e_infra():
    # 60 s între stamp-uri; +30 s CPU = 50% și +40 s = 66%
    d = _decide(_log((0, [(777, 100)]), (1, [(777, 130)]), (2, [(777, 170)])))
    assert d["decizie"] == "infra" and d["dovada"]["pid"] == 777 and d["dovada"]["cpu"] == 66, d
    assert d["motiv"] == "infra: 777 python3 /home/costin/alt_proiect/ruleaza.py peste 30% susținut"


def test_g2_peste_30_pe_un_singur_interval_e_stop():
    assert _decide(_log((0, [(777, 100)]), (1, [(777, 140)]), (2, [(777, 142)])))["decizie"] == "stop"


def test_g2_exact_30_la_suta_e_stop():
    # 18 s de CPU în 60 s = exact 30%: nu e „peste 30%”
    assert _decide(_log((0, [(777, 100)]), (1, [(777, 118)]), (2, [(777, 136)])))["decizie"] == "stop"


def test_g2_doua_intervale_peste_30_la_pid_uri_diferite_e_stop():
    assert _decide(_log((0, [(777, 100), (888, 5)]), (1, [(777, 140), (888, 5)]), (2, [(777, 141), (888, 50)])))["decizie"] == "stop"


@pytest.mark.parametrize("comanda", ["java -jar DUKIntegrator.jar", "python -m core.firma_rezumat 4", "python verificator_conformitate.py",
                                     "bash /home/costin/veghe_code.sh", "bash orchestrator.sh", "bash veghe_incarcare.sh", "bash alerta_veghe.sh"])
def test_g2_procesul_portii_sau_al_veghei_nu_e_strain(comanda):
    assert _decide(_log((0, [(777, 100, comanda)]), (1, [(777, 140, comanda)]), (2, [(777, 190, comanda)])))["decizie"] == "stop"


def test_g2_intervalul_peste_schimbarea_datei_se_calculeaza_corect():
    baza = datetime.datetime(2026, 11, 11, 23, 58, 0)
    text = "\n".join([_stamp(0, baza=baza), _strain(5, 100), _stamp(1, baza=baza), _strain(5, 140), _stamp(2, baza=baza), _strain(5, 190), _stamp(3, baza=baza), _strain(5, 230)]) + "\n"
    d = IG.decide("poarta_plasa", 1500, PRAG, _iso(-1, baza=baza), _iso(10, baza=baza), text)
    assert d["decizie"] == "infra" and d["dovada"]["ora"].startswith("2026-11-12 00:0"), d


def test_g2_formatul_vechi_log_lipsa_si_stampuri_in_afara_ferestrei_sunt_stop():
    vechi = "15:00:00 faza=poarta_plasa load=1 1 1\n   strain: pid 777 (cpu 90%) python3 x.py\n15:01:00 faza=poarta_plasa load=1 1 1\n   strain: pid 777 (cpu 90%) python3 x.py\n"
    assert _decide(vechi)["decizie"] == "stop" and IG.format_vechi(vechi) == (2, 2)
    assert _decide(None)["decizie"] == "stop" and _decide("")["decizie"] == "stop"
    afara = _log((100, [(777, 100)]), (101, [(777, 140)]), (102, [(777, 190)]))     # stamp-uri la 16:40, fereastra se termină la 15:40
    assert _decide(afara)["decizie"] == "stop"


def test_g2_un_pid_lipsa_dintr_un_stamp_rupe_lantul():
    assert _decide(_log((0, [(777, 100)]), (1, [(777, 140)]), (2, [(888, 5)]), (3, [(777, 190)]), (4, [(777, 235)])))["decizie"] == "stop"


@pytest.mark.parametrize("faza", ["hook", "poarta_verificator"])
def test_g2_hook_si_poarta_verificator_raman_stop_chiar_cu_proces_strain_sustinut(faza):
    d = _decide(_log((0, [(777, 100)]), (1, [(777, 140)]), (2, [(777, 190)])), faza=faza)
    assert d["decizie"] == "stop" and "nu se reclasifică niciodată" in d["motiv"]


def test_g2_sub_prag_nu_se_cere_nimic():
    assert _decide(None, durata=PRAG)["decizie"] == "ok"


# ── T.5: depasiri_praguri, _rez_run, marcajul din jurnal ─────────────────────────────────────────────────────────
def _r(faza, id_, rez, sec):
    return (faza, id_, "2026-11-12T10:00:00+02:00", "2026-11-12T11:00:00+02:00", rez, sec)


LINII = ["unelte", "max poarta_plasa 1000", "max poarta_pytest 500"]


def test_prima_peste_prag_marcata_apoi_sub_prag_nu_da_stop_si_se_numara_separat():
    g2 = {}
    stop, _ = PL.depasiri_praguri([_r("poarta_plasa", "a", "infra_g2", 1500), _r("poarta_plasa", "b", "verde", 900)], LINII, g2=g2, marcaje={"a": ("infra: 777 x peste 30% susținut", "1800")})
    assert stop == [] and g2 == {"poarta_plasa": 1}


def test_prima_peste_prag_marcata_apoi_peste_prag_da_stop_cu_ambele_masuratori():
    stop, _ = PL.depasiri_praguri([_r("poarta_plasa", "a", "infra_g2", 1500), _r("poarta_plasa", "b", "verde", 1300)], LINII, g2={}, marcaje={"a": ("infra: 777 x peste 30% susținut", "1800")})
    assert len(stop) == 1 and stop[0].startswith("pragul „poarta_plasa” depășit: 1300s > 1000s") and "prima măsurare: 1800s" in stop[0], stop


def test_depasirea_simpla_pastreaza_textul_de_azi():
    stop, _ = PL.depasiri_praguri([_r("poarta_pytest", "a", "verde", 600)], LINII)
    assert stop == ["pragul „poarta_pytest” depășit: 600s > 500s"]


def test_rand_marcat_fara_remasurare_da_stop_marcata_infra_fara_remasurare():
    stop, _ = PL.depasiri_praguri([_r("poarta_plasa", "a", "infra_g2", 1500)], LINII, g2={})
    assert stop == ["faza poarta_plasa: marcată infra fără re-măsurare"]
    stop, _ = PL.depasiri_praguri([_r("poarta_plasa", "a", "infra_g2", 1500), _r("poarta_plasa", "b", "intrerupt", 20)], LINII, g2={})
    assert stop == ["faza poarta_plasa: marcată infra fără re-măsurare"]


def test_rulari_infra_si_intrerupte_se_ignora_ca_azi():
    infra = {}
    stop, intrerupte = PL.depasiri_praguri([_r("poarta_plasa", "a", "infra", 3000), _r("poarta_plasa", "b", "intrerupt", 4000), _r("poarta_plasa", "c", "verde", 900)], LINII, infra)
    assert stop == [] and infra == {"poarta_plasa": 1} and intrerupte == {"poarta_plasa": 1}


def test_rez_run_cu_infra_g2_amestecat_cu_verde_e_infra_nu_rosu():
    assert JL._rez_run(["verde", "infra_g2"]) == "infra"
    assert JL._rez_run(["verde", "infra_g2", "rosu_1"]) == "rosu"
    assert JL._rez_run(["verde", "verde"]) == "verde"


def _jurnal(tmp_path, monkeypatch, durata, faza="poarta_plasa", lot="17.5-X"):
    cale = tmp_path / "jurnal.log"
    monkeypatch.setenv("LOT_JURNAL", str(cale))
    JL._scrie(str(cale), [lot, faza, "inceput", _iso(0), "abc", "-", "id1", os.getpid(), ""])
    JL._scrie(str(cale), [lot, faza, "sfarsit", _iso(0, durata), "abc", "verde", "id1", os.getpid(), ""])
    return str(cale)


def _praguri(tmp_path, lotf="17_5_X", max_plasa=1000):
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / "scripts" / ("praguri_%s.txt" % lotf)).write_text("unelte\nmax poarta_plasa %d\nmax poarta_pytest 500\n" % max_plasa)
    return str(tmp_path)


def test_remasoara_g2_marcheaza_prima_masurare_si_cere_remasurare(tmp_path, monkeypatch):
    cale = _jurnal(tmp_path, monkeypatch, 1500)
    rad = _praguri(tmp_path)
    (tmp_path / "incarcare.log").write_text(_log((0, [(777, 100)]), (1, [(777, 140)]), (2, [(777, 190)])))
    monkeypatch.setenv("POARTA_LOG_INCARCARE", str(tmp_path / "incarcare.log"))
    assert PR.remasoara_g2("17.5-X", "17_5_X", rad, "poarta_plasa", {"id": "id1"}) is True
    marcaje = JL.marcaje_g2("17.5-X", cale)
    assert marcaje["id1"][0].startswith("infra: 777 python3 /home/costin/alt_proiect/ruleaza.py peste 30% susținut") and marcaje["id1"][1] == "1500"
    durate = JL.durate("17.5-X", cale)
    assert durate[0][4] == "infra_g2"


def test_remasoara_g2_fara_dovada_sau_fara_prag_sau_sub_prag_nu_marcheaza(tmp_path, monkeypatch):
    cale = _jurnal(tmp_path, monkeypatch, 1500)
    rad = _praguri(tmp_path)
    monkeypatch.setenv("POARTA_LOG_INCARCARE", str(tmp_path / "lipsa.log"))
    assert PR.remasoara_g2("17.5-X", "17_5_X", rad, "poarta_plasa", {"id": "id1"}) is False          # fără log
    (tmp_path / "scripts" / "praguri_17_5_X.txt").write_text("unelte\n")
    assert PR.remasoara_g2("17.5-X", "17_5_X", rad, "poarta_plasa", {"id": "id1"}) is False          # lotul fără rând `max` (ca 17.5-T însuși)
    assert JL.marcaje_g2("17.5-X", cale) == {}


def test_remasoara_g2_nu_se_aplica_la_hook_si_poarta_verificator(tmp_path, monkeypatch):
    _jurnal(tmp_path, monkeypatch, 1500, faza="poarta_verificator")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "praguri_17_5_X.txt").write_text("unelte\nmax poarta_verificator 100\n")
    (tmp_path / "incarcare.log").write_text(_log((0, [(777, 100)]), (1, [(777, 140)]), (2, [(777, 190)])))
    monkeypatch.setenv("POARTA_LOG_INCARCARE", str(tmp_path / "incarcare.log"))
    assert PR.remasoara_g2("17.5-X", "17_5_X", str(tmp_path), "poarta_verificator", {"id": "id1"}) is False


# ── treapta falsă: worktree fals, e2e_poarta.py fals (aceeași formă ca în core/test_verificator_design_16_7.py) ────
FALS_E2E = """import os, sys
P = %(p)r
doar = [a for a in sys.argv[1:] if a.startswith("--doar=")]
proba = len(doar) == 1 and "::" in doar[0]
open(os.path.join(P, "apeluri"), "a").write(("proba " if proba else "plasa ") + doar[0][len("--doar="):] + "\\n")
if proba:
    cod = int(open(os.path.join(P, "cod_proba")).read())
    jx = [x for x in os.environ.get("PYTEST_ADDOPTS", "").split("=", 1)[1:]]
    if cod == 1 and jx and os.path.exists(os.path.join(P, "proba_cu_failure")):
        open(jx[0], "w").write('<testsuites><testsuite><testcase classname="e2e_p" name="test_p"><failure message="%%s"/></testcase></testsuite></testsuites>' %% open(os.path.join(P, "proba_cu_failure")).read())
    sys.exit(cod)
open(os.path.join(P, "martor"), "w").write("rulat")
sys.exit(0)
"""


def _wt(tmp_path, cod_proba=0, mesaj_failure=None, proba_in_arbore=True):
    wt, j, p = tmp_path / "wt", tmp_path / "J", tmp_path / "P"
    (wt / "scripts" / "bin").mkdir(parents=True)
    (wt / "frontend_test" / "e2e").mkdir(parents=True)
    (wt / "docs" / "dovezi" / "17_5_T").mkdir(parents=True)
    j.mkdir()
    p.mkdir()
    (wt / "scripts" / "baza_test.sh").write_text("#!/bin/sh\nexit 0\n")
    (wt / "scripts" / "e2e_poarta.py").write_text(FALS_E2E % {"p": str(p)})
    (wt / "frontend_test" / "e2e" / "e2e_p.py").write_text("def test_p():\n    pass\n")
    if proba_in_arbore:
        (wt / L.PROBA_MEDIU).write_text("e2e_p.py::test_p\ndurate: 3.1 3.0 3.2\n")
    (p / "cod_proba").write_text(str(cod_proba))
    if mesaj_failure:
        (p / "proba_cu_failure").write_text(mesaj_failure)
    os.symlink(os.path.join(RAD, "venv"), wt / "venv")
    return str(wt), str(j), p


def _plasa(wt, j, **kw):
    return L.ruleaza_trepte(wt, j, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False, sonda_8019=lambda: False, opreste_8019=lambda: None, **kw)


# ── T.6: proba de mediu înaintea plasei ──────────────────────────────────────────────────────────────────────────
def test_proba_cazuta_inseamna_treapta_infra_si_plasa_nu_porneste(tmp_path):
    wt, j, p = _wt(tmp_path, cod_proba=3)
    trepte, teste = _plasa(wt, j)
    ses = [t for t in teste if t["nume"] == "plasa_e2e::sesiune"]
    assert len(ses) == 1 and ses[0]["infra"] and ses[0]["mesaj"].startswith("proba de mediu e2e_p.py::test_p:"), teste
    assert not (p / "martor").exists()                                   # plasa n-a pornit
    assert (p / "apeluri").read_text() == "proba e2e_p.py::test_p\n"
    assert L.rezultat_treapta(3, []) == "infra" and ses[0]["tip"] == "conexiune"


def test_proba_verde_si_plasa_porneste_cu_durata_probei_in_trepte(tmp_path):
    wt, j, p = _wt(tmp_path, cod_proba=0)
    trepte, teste = _plasa(wt, j)
    assert (p / "martor").exists() and (p / "apeluri").read_text().splitlines()[0] == "proba e2e_p.py::test_p"
    assert "proba_mediu" in trepte and trepte["plasa_e2e"] >= trepte["proba_mediu"]
    assert not [t for t in teste if t["rezultat"] == "pica"]


def test_proba_cazuta_cu_failure_e_de_tip_aserțiune_cu_primul_rand_al_mesajului(tmp_path):
    wt, j, p = _wt(tmp_path, cod_proba=1, mesaj_failure="AssertionError: lipsă butonul X")
    _, teste = _plasa(wt, j)
    ses = [t for t in teste if t["nume"] == "plasa_e2e::sesiune"][0]
    assert ses["tip"] == "aserțiune" and ses["mesaj"] == "proba de mediu e2e_p.py::test_p: AssertionError: lipsă butonul X"


def test_fisier_de_proba_lipsa_sau_test_inexistent_e_rosu_cu_motiv_nu_infra(tmp_path):
    wt, j, p = _wt(tmp_path, proba_in_arbore=False)
    trepte, teste = _plasa(wt, j)
    pica = [t for t in teste if t["rezultat"] == "pica"]
    assert [t["nume"] for t in pica] == ["plasa_e2e::proba_mediu"] and not pica[0]["infra"] and "lipsește" in pica[0]["mesaj"]
    assert not (p / "martor").exists() and L.rezultat_treapta(1, pica) == "rosu_1"
    wt2, j2, p2 = _wt(tmp_path / "doi")
    (tmp_path / "doi" / "wt" / L.PROBA_MEDIU).write_text("e2e_p.py::test_disparut\n")
    _, teste = _plasa(wt2, j2)
    assert "nu mai există" in [t for t in teste if t["rezultat"] == "pica"][0]["mesaj"] and not (p2 / "martor").exists()


def test_proba_cazuta_in_remasurarea_g2_a_plasei_e_oprire_nu_infra(tmp_path):
    wt, j, p = _wt(tmp_path, cod_proba=3)
    (p / "cod_proba").write_text("0")
    chemari = []

    def dupa(faza, f):
        chemari.append(faza)
        (p / "cod_proba").write_text("3")                      # mediul se strică între prima măsurare și re-măsurare
        return faza == "poarta_plasa"
    with pytest.raises(L.OprirePoarta) as e:
        _plasa(wt, j, dupa_treapta=dupa)
    assert str(e.value).startswith("proba de mediu căzută în re-măsurare: e2e_p.py::test_p") and chemari == ["poarta_plasa"]


def test_remasurarea_ruleaza_numai_treapta_depasita_o_singura_data_si_nu_scrie_verdicte(tmp_path):
    wt, j, p = _wt(tmp_path)
    chemari = []
    verdicte, ultima = tmp_path / "poarta_verdicte.log", tmp_path / "poarta_ultima.txt"

    def dupa(faza, f):
        chemari.append(faza)
        return len(chemari) == 1
    trepte, teste = _plasa(wt, j, dupa_treapta=dupa)
    assert chemari == ["poarta_plasa"]                                                        # o singură re-măsurare: după ea callback-ul nu se mai cheamă
    apeluri = (p / "apeluri").read_text().splitlines()
    assert apeluri == ["proba e2e_p.py::test_p", "plasa e2e_x.py", "proba e2e_p.py::test_p", "plasa e2e_x.py"]      # numai plasa, de două ori, cu proba înaintea fiecăreia; niciun pytest
    assert not verdicte.exists() and not ultima.exists()


def test_decide_trei_cazaturi_ale_probei_cu_acelasi_mesaj_de_aserțiune_spun_regresie_probabila():
    stare = {"complete": [], "reluari": [], "regresii": [], "oprit": None, "infra": []}
    rez = {k: [] for k in __import__("poarta_clasifica").CURAT}
    rez["infra"] = ["plasa_e2e::sesiune"]
    motiv = "proba de mediu e2e_p.py::test_p: AssertionError: lipsă butonul X"
    for i in range(3):
        d = PR.decide(stare, rez, False, [], "abc", "2026-11-12T10:00:0%d" % i, motiv, None, "aserțiune")
        stare = d["stare"]
        assert d["infra"] and d["cod"] == (3 if i == 2 else 4)
        assert not stare["complete"]                                                          # nu consumă o rulare completă
    assert stare["oprit"] == "infra ×3: aserțiune repetată, regresie probabilă: " + motiv


def test_decide_trei_cazaturi_de_conexiune_raman_infra_x3_simplu():
    stare = {"complete": [], "reluari": [], "regresii": [], "oprit": None, "infra": []}
    rez = {k: [] for k in __import__("poarta_clasifica").CURAT}
    rez["infra"] = ["plasa_e2e::sesiune"]
    motiv = "proba de mediu e2e_p.py::test_p: aplicația n-a pornit"
    for i in range(3):
        d = PR.decide(stare, rez, False, [], "abc", "2026-11-12T10:00:0%d" % i, motiv, None, "conexiune")
        stare = d["stare"]
    assert stare["oprit"] == "infra ×3: " + motiv and PR.e_rulare_infra(rez)


# ── T.8: proba de contract la începutul porții, pe o clonă temporară cu lot de produs simulat ─────────────────────
LOT_P = "99.9-Z"
LOTF_P = "99_9_Z"


def _g(cwd, *a, **kw):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, **kw)


@pytest.fixture(scope="module")
def clona(tmp_path_factory):
    """Clona temporară a depozitului (la HEAD) cu un lot de produs simulat: poarta reală (scripts/poarta_rulare.py din clonă), treapta falsă a plasei care scrie un fișier-martor, baza_test.sh gol, verificator fals."""
    dep = str(tmp_path_factory.mktemp("clona") / "dep")
    subprocess.run(["git", "clone", "--local", "-q", RAD, dep], check=True)
    with open(os.path.join(dep, ".git", "info", "exclude"), "a") as f:
        f.write("/venv\n/import_fiscalos\n")
    os.symlink(os.path.join(RAD, "venv"), os.path.join(dep, "venv"))
    os.symlink(os.path.join(RAD, "import_fiscalos"), os.path.join(dep, "import_fiscalos"))
    # fișierele de lucru ale lotului (necomise încă în depozitul sursă, la rularea de lucru) se copiază peste clonă; comise, copia nu schimbă nimic
    for f in ("scripts/poarta_rulare.py", "scripts/poarta_lib.py", "scripts/publica_lot.py", "scripts/jurnal_lot.py", "scripts/infra_g2.py"):
        subprocess.run(["cp", os.path.join(RAD, f), os.path.join(dep, f)], check=True)
    sha = _g(dep, "rev-parse", "HEAD").stdout.strip()
    _g(dep, "checkout", "-q", "-b", "lucru/lot99-9z")
    _g(dep, "branch", "-f", "main", sha)
    return dep


def _pregateste(dep, pasi, randuri, captura=True):
    """Pune în clonă dovezile lotului simulat (pasi.txt, jurnal_verificare.csv, captura), fișierele false ale treptelor și comite totul; -> directorul de martor."""
    baza = _g(dep, "merge-base", "HEAD", "main").stdout.strip()
    d = os.path.join(dep, "docs", "dovezi", LOTF_P)
    os.makedirs(d, exist_ok=True)
    martor = os.path.join(dep, "martor_plasa")
    if os.path.exists(martor):
        os.remove(martor)
    open(os.path.join(dep, "scripts", "praguri_%s.txt" % LOTF_P), "w").write("produs\nrunde_verificator_max: 1\n")
    open(os.path.join(d, "pasi.txt"), "w", encoding="utf-8").write(pasi)
    import hashlib
    man = hashlib.sha256(open(os.path.join(dep, "scripts", "plasa_16_2.manifest"), "rb").read()).hexdigest()
    json.dump({"antet": {"commit_baza": baza, "manifest_sha256": man}, "teste": []}, open(os.path.join(d, "baza.json"), "w"))
    os.makedirs(os.path.join(d, "capturi"), exist_ok=True)
    cap = os.path.join(d, "capturi", "a.png")
    if os.path.exists(cap):
        os.remove(cap)
    if captura:
        open(cap, "wb").write(b"\x89PNG")
    import csv
    with open(os.path.join(d, "jurnal_verificare.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lot", "parcurgere", "pas", "commit", "verificator", "captura", "verdict"])
        for r in randuri:
            w.writerow([LOT_P, "inainte", r["pas"], r["commit"].format(baza=baza), "code", os.path.join(os.path.relpath(d, dep), "capturi", "a.png"), r["verdict"]])
    open(os.path.join(dep, "scripts", "poarta_nucleu.txt"), "w").write("")
    open(os.path.join(dep, "scripts", "baza_test.sh"), "w").write("#!/bin/sh\nexit 0\n")
    open(os.path.join(dep, "scripts", "e2e_poarta.py"), "w").write("import os, sys\nif not any('::' in a for a in sys.argv):\n    open(%r, 'w').write('rulat')\n" % martor)
    open(os.path.join(dep, "verificator_conformitate.py"), "w").write("print('TOTAL: 0')\n")
    # niciodată portul 8019 real: clona are un verificator_design fals (portul „liber”, nimic de oprit); un test nu atinge serverul de lucru
    open(os.path.join(dep, "scripts", "verificator_design.py"), "w").write(
        "def elibereaza_port(port, sonda=None, opreste_fn=None, lot=None):\n    return True, ''\n\n\ndef _raspunde(port=8019):\n    return False\n\n\ndef opreste():\n    pass\n\n\ndef port_ocupat(port):\n    return False\n")
    _g(dep, "add", "-A")
    _g(dep, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--no-verify", "--allow-empty", "-m", "proba T.8")
    return martor


def _poarta(dep, tmp_path):
    env = dict(os.environ, LOT=LOT_P, LACAT_TEST_PID=str(os.getpid()), POARTA_PLASA_FIX="scripts/plasa_16_2.manifest", POARTA_JURNALE=str(tmp_path), LOT_JURNAL=str(tmp_path / "jurnal.log"))
    return subprocess.run([os.path.join(dep, "venv", "bin", "python"), "scripts/poarta_rulare.py"], cwd=dep, env=env, capture_output=True, text=True, timeout=900)


def _stare(dep):
    comun = _g(dep, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
    return os.path.join(comun, "lot_stare_%s.json" % LOTF_P)


TEXT_ORACOL = "a.1 | 1 | ecran | dom:#x | egal | 5 | descriere\nb.1 | 2 | ecran | dom:#y | egal | 6 | descriere\n"


@pytest.mark.parametrize("nume,pasi,randuri,captura", [
    ("pasi_cu_textul_oracolului", TEXT_ORACOL, [{"pas": "a.1", "commit": "{baza}", "verdict": "trece"}], True),
    ("randul_pasului_a_pe_alt_commit", "a.1\nb.1\n", [{"pas": "a.1", "commit": "0" * 40, "verdict": "trece"}], True),
    ("captura_randului_lipseste", "a.1\nb.1\n", [{"pas": "a.1", "commit": "{baza}", "verdict": "trece"}], False),
])
def test_proba_de_contract_roșu_refuza_inainte_de_prima_treapta_fara_stare(clona, tmp_path, nume, pasi, randuri, captura):
    martor = _pregateste(clona, pasi, randuri, captura)
    r = _poarta(clona, tmp_path)
    assert r.returncode == 1 and "[poarta] REFUZ: proba_contract:" in r.stdout, r.stdout + r.stderr
    assert not os.path.exists(martor)                                              # nicio treaptă n-a pornit
    assert not os.path.exists(_stare(clona))                                       # stare[complete], stare[infra], stare[oprit] neatinse
    assert "INFRA" not in r.stdout


def test_proba_de_contract_cu_dovezi_corecte_poarta_porneste(clona, tmp_path):
    martor = _pregateste(clona, "a.1\nb.1\n", [{"pas": "a.1", "commit": "{baza}", "verdict": "trece"}], True)
    r = _poarta(clona, tmp_path)
    assert "REFUZ" not in r.stdout and os.path.exists(martor), r.stdout + r.stderr


def test_proba_de_contract_lot_unelte_fara_pasi_porneste(clona, tmp_path):
    martor = _pregateste(clona, "a.1\n", [{"pas": "a.1", "commit": "{baza}", "verdict": "trece"}], True)
    os.remove(os.path.join(clona, "docs", "dovezi", LOTF_P, "pasi.txt"))
    open(os.path.join(clona, "scripts", "praguri_%s.txt" % LOTF_P), "w").write("unelte\n")
    _g(clona, "add", "-A")
    _g(clona, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--no-verify", "-m", "lot unelte fără pasi")
    r = _poarta(clona, tmp_path)
    assert "REFUZ" not in r.stdout and os.path.exists(martor), r.stdout + r.stderr


# ── T.2 (d): scripts/verifica_lista_17_5_T.py ────────────────────────────────────────────────────────────────────
import verifica_lista_17_5_T as VL  # noqa: E402

TEST_BAZA = '''import pytest

PRAG = 60


def _ajutor():
    return 1


def test_a():
    assert _ajutor() == 1
    assert PRAG == 60


def test_b():
    assert 1 == 1


def test_c():
    assert 2 == 2
'''

LISTA_TSV = "test\tcategorie\tcauza\tdecizia\tactiunea\n" + "".join(
    "frontend_test/e2e/e2e_x.py::test_%s\tTEST_VECHI\tc\tgrupa LUNA | 817\tT.2: x\n" % n for n in "abc")


def _depozit(tmp_path, noul, scoase="", fisier="frontend_test/e2e/e2e_x.py", sterge=False):
    """Depozit temporar: commitul de bază cu TEST_BAZA, apoi arborele P cu `noul` (sau fișier șters). -> (rad, baza)."""
    rad = str(tmp_path / "dep")
    os.makedirs(os.path.join(rad, "frontend_test", "e2e"))
    os.makedirs(os.path.join(rad, "docs", "dovezi", "17_5_T"))
    subprocess.run(["git", "init", "-q", rad], check=True)
    open(os.path.join(rad, fisier), "w", encoding="utf-8").write(TEST_BAZA)
    open(os.path.join(rad, VL.LISTA), "w", encoding="utf-8").write(LISTA_TSV)
    _g(rad, "add", "-A")
    _g(rad, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "baza")
    baza = _g(rad, "rev-parse", "HEAD").stdout.strip()
    if sterge:
        os.remove(os.path.join(rad, fisier))
    else:
        open(os.path.join(rad, fisier), "w", encoding="utf-8").write(noul)
    open(os.path.join(rad, VL.SCOASE), "w", encoding="utf-8").write(scoase)
    return rad, baza


def _erori(tmp_path, noul, **kw):
    rad, baza = _depozit(tmp_path, noul, **kw)
    return VL.verifica(rad, baza)


def test_lista_scaderea_aserțiunilor_e_eroare(tmp_path):
    noul = TEST_BAZA.replace("    assert PRAG == 60\n", "").replace("def test_a():", 'def test_a():\n    """[17.5-T] actualizat la 817 (static/js/luna_lucru.js:1)"""')
    randuri, erori = _erori(tmp_path, noul)
    assert any("test_a: aserțiunile au scăzut: 2 → 1" in e for e in erori), erori
    assert VL.main(["--rad", str(tmp_path / "dep"), "--baza", _g(str(tmp_path / "dep"), "rev-parse", "HEAD").stdout.strip()]) == 1


def test_lista_egal_sau_crestere_cu_marker_e_zero_erori_si_tabelul_are_cele_doua_numere(tmp_path):
    noul = TEST_BAZA.replace("PRAG = 60", "PRAG = 61").replace("def test_a():", 'def test_a():\n    """[17.5-T] actualizat la 817 (static/js/luna_lucru.js:1)"""').replace(
        "    assert PRAG == 60\n", "    assert PRAG == 61\n    assert _ajutor() == 1\n")
    randuri, erori = _erori(tmp_path, noul)
    assert erori == [], erori
    a = [r for r in randuri if r["test"].endswith("test_a")][0]
    assert (a["baza"], a["p"], a["grupa"]) == (2, 3, "LUNA") and a["marker"].startswith("[17.5-T] actualizat la 817")
    assert "PRAG" in a["alte"]                                                       # constanta de nivel modul modificată e numită
    assert [r["marker"] for r in randuri if not r["test"].endswith("test_a")] == ["-", "-"]


def test_lista_test_neatins_nu_cere_marker(tmp_path):
    randuri, erori = _erori(tmp_path, TEST_BAZA)
    assert erori == [] and all(r["baza"] == r["p"] for r in randuri)


def test_lista_test_atins_fara_marker_e_eroare(tmp_path):
    randuri, erori = _erori(tmp_path, TEST_BAZA.replace("assert 1 == 1", "assert 1 == 1\n    assert 3 == 3"))
    assert any("test_b: test atins fără marker" in e for e in erori), erori


def test_lista_marker_in_comentariu_pe_prima_linie_e_valid(tmp_path):
    noul = TEST_BAZA.replace("def test_b():\n", "def test_b():\n    # [17.5-T] stabilizat: cursă la pornirea validatorului DUK, așteaptă răspunsul paginii\n").replace("assert 1 == 1", "assert 1 == 1\n    assert 3 == 3")
    _, erori = _erori(tmp_path, noul)
    assert erori == [], erori


def test_lista_test_scos_cu_marker_e_zero_fara_marker_e_unu(tmp_path):
    fara = TEST_BAZA.replace("def test_c():\n    assert 2 == 2\n", "")
    _, erori = _erori(tmp_path, fara)
    assert len(erori) == 1 and "test_c: lipsește la P fără marker" in erori[0]
    cu = fara + "# [17.5-T] scos: test_c: verifica butonul scos prin decizia 817, 817\n"
    _, erori = _erori(tmp_path / "doi", cu)
    assert erori == [], erori


def test_lista_fisier_sters_cu_linie_in_scoase_e_zero_fara_linie_e_unu(tmp_path):
    _, erori = _erori(tmp_path, "", sterge=True)
    assert len(erori) == 3 and all("lipsește la P" in e for e in erori)
    scoase = "".join("frontend_test/e2e/e2e_x.py::test_%s | testul n-are obiect după decizie | 817\n" % n for n in "abc")
    _, erori = _erori(tmp_path / "doi", "", sterge=True, scoase=scoase)
    assert erori == [], erori
    scurt = "frontend_test/e2e/e2e_x.py::test_a | scurt | 817\n"                        # motiv sub 10 caractere = nu e linie valida
    _, erori = _erori(tmp_path / "trei", "", sterge=True, scoase=scurt)
    assert len(erori) == 3


def test_lista_de_lucru_ia_numai_t2_t3_t4_si_strange_parametrii():
    r = VL.lista_de_lucru(RAD)
    assert len(r) == len(set(r)) and all(x[1].startswith("test") and "[" not in x[1] for x in r)
