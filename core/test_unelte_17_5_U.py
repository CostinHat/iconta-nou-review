# -*- coding: utf-8 -*-
"""Probele lotului de unelte 17.5-U (U.1–U.7): 8019 eliberat sau refuzat, eroarea de infrastructură care nu consumă o rulare, așteptarea porții fără auto-potrivire, manifestul care nu se
rescrie, motivul opririi în alertă, testele care citesc locurile schimbate, inventarul testelor roșii pe bază. Fără DB, fără 8019 real: depozite git temporare, jurnale și stări false."""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
PY = sys.executable
LOT = "17.5-U"


def _acum(delta=0):
    return (datetime.datetime.now().astimezone() + datetime.timedelta(seconds=delta)).isoformat(timespec="seconds")


# ── U.3 — scripts/asteapta_poarta.sh ─────────────────────────────────────────────────────────────────────────────────────────────────────────
class Depozit:
    """Un depozit git temporar cu jurnal (LOT_JURNAL), poarta_verdicte.log și starea lotului, citite de scripts/asteapta_poarta.py."""

    def __init__(self, tmp):
        os.makedirs(str(tmp), exist_ok=True)
        self.dir = str(tmp / "dep")
        os.makedirs(self.dir)
        subprocess.run(["git", "init", "-q"], cwd=self.dir, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "x"], cwd=self.dir, check=True)
        self.jurnal = str(tmp / "jurnal.log")
        self.comun = os.path.join(self.dir, ".git")
        self.procese = []
        self.n = 0

    def head(self):
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.dir, capture_output=True, text=True).stdout.strip()

    def pid_viu(self):
        p = subprocess.Popen(["sleep", "60"])
        self.procese.append(p)
        return p.pid

    def pid_mort(self):
        p = subprocess.Popen(["true"])
        p.wait()
        return p.pid

    def faza(self, faza, inceput, sfarsit=None, rezultat="verde", pid=None, sha="aaaaaaaaaaaa", lot=LOT):
        """Scrie perechea inceput/sfarsit (sfarsit None = fără sfarsit)."""
        self.n += 1
        id_ = "%d-%d" % (self.n, self.n)
        pid = self.pid_mort() if pid is None else pid
        rows = [[lot, faza, "inceput", inceput, sha, "-", id_, str(pid), ""]]
        if sfarsit:
            rows.append([lot, faza, "sfarsit", sfarsit, sha, rezultat, id_, str(pid), ""])
        with open(self.jurnal, "a", encoding="utf-8") as f:
            f.writelines("\t".join(r) + "\n" for r in rows)

    def verdict(self, tip, data, sha="b" * 40, lot=LOT):
        linie = ("%s %s lucru/x %s manifest=h completa lot=%s" % (tip, sha, data, lot)) if tip != "INFRA" else "INFRA %s lucru/x %s lot=%s 8019 ocupat de pid 1 (uvicorn)" % (sha, data, lot)
        with open(os.path.join(self.comun, "poarta_verdicte.log"), "a", encoding="utf-8") as f:
            f.write(linie + "\n")

    def stare(self, **kw):
        json.dump(dict({"complete": [], "reluari": [], "regresii": [], "oprit": None}, **kw), open(os.path.join(self.comun, "lot_stare_17_5_U.json"), "w"))

    def ruleaza(self, *argv, lot=LOT, marja=None, marja_pid=None):
        env = dict(os.environ, LOT_JURNAL=self.jurnal)
        env.pop("LOT", None)
        if marja is not None:
            env["MARJA_RELANSARE_S"] = str(marja)
        if marja_pid is not None:
            env["MARJA_PID_S"] = str(marja_pid)
        r = subprocess.run(["sh", os.path.join(RAD, "scripts", "asteapta_poarta.sh"), *([lot] if lot else []), *argv], cwd=self.dir, env=env, capture_output=True, text=True, timeout=60)
        return r.returncode, r.stdout, r.stderr

    def inchide(self):
        for p in self.procese:
            p.kill()
            p.wait()


@pytest.fixture
def dep(tmp_path):
    d = Depozit(tmp_path)
    yield d
    d.inchide()


def _linie(out, rezultat, sha=None):
    m = re.fullmatch(r"poarta %s: (\w+) (\S+)\n" % re.escape(LOT), out)
    assert m, out
    assert m.group(1) == rezultat, out
    if sha is not None:
        assert m.group(2) == sha, out
    return m.group(2)


def test_p1_oprit_nevid_e_3_chiar_cu_verde_in_jurnalul_de_verdicte(dep):
    dep.verdict("VERDE", _acum(-5))
    dep.stare(oprit="infra ×3: 8019 ocupat")
    rc, out, _ = dep.ruleaza("1")
    assert rc == 3
    _linie(out, "oprit", "b" * 40)


def test_p2_verde_ultim_fara_faza_dupa_el_e_0_si_faza_din_aceeasi_secunda_nu_il_anuleaza(dep):
    t = _acum(-5)
    dep.faza("poarta_plasa", _acum(-60), _acum(-6))
    dep.verdict("VERDE", t)
    assert dep.ruleaza("1")[0] == 0
    dep.faza("poarta_verificator", t, t, pid=dep.pid_viu())          # „inceput” în aceeași secundă cu VERDE: anterioară verdictului
    rc, out, _ = dep.ruleaza("1")
    assert rc == 0
    _linie(out, "verde", "b" * 40)


def test_p3_rosu_ultim_fara_faza_dupa_el_e_1(dep):
    dep.verdict("ROSU", _acum(-5))
    rc, out, _ = dep.ruleaza("1")
    assert rc == 1
    _linie(out, "rosu")


@pytest.mark.parametrize("tip", ["VERDE", "ROSU"])
def test_p4_verdict_vechi_si_faza_noua_vie_e_9_nu_0_sau_1(dep, tip):
    dep.verdict(tip, _acum(-100))
    dep.faza("poarta_verificator", _acum(0), pid=dep.pid_viu())
    rc, out, _ = dep.ruleaza("1")
    assert rc == 9
    _linie(out, "in_curs", dep.head())


def test_p5_rosu_vechi_si_faza_noua_moarta_e_5(dep):
    dep.verdict("ROSU", _acum(-100))
    dep.faza("poarta_pytest", _acum(-30))
    rc, out, err = dep.ruleaza("1")
    assert rc == 5 and "poarta_pytest moartă" in err
    _linie(out, "intrerupt", dep.head())


def test_p6_verdictul_vechi_se_ignora_cu_dupa_mai_nou_si_iese_6(dep):
    dep.verdict("ROSU", _acum(-100))
    rc, out, _ = dep.ruleaza("1", "--dupa=" + _acum(-10))
    assert rc == 6
    _linie(out, "nepornita", "-")


def test_p7_inceput_cu_pid_mort_fara_verdict_e_5(dep):
    dep.faza("poarta_verificator", _acum(-30))
    assert dep.ruleaza("1")[0] == 5


def test_p8_sfarsit_intrerupt_fara_verdict_e_5_si_cu_verde_ulterior_e_0(dep):
    dep.faza("poarta_pytest", _acum(-60), _acum(-50), rezultat="intrerupt")
    assert dep.ruleaza("1")[0] == 5
    dep.verdict("VERDE", _acum(-5))
    assert dep.ruleaza("1")[0] == 0


def test_p9_sfarsit_intrerupt_si_faza_noua_vie_e_9_iar_fara_faza_noua_e_5(dep):
    dep.faza("poarta_pytest", _acum(-60), _acum(-50), rezultat="intrerupt")
    assert dep.ruleaza("1")[0] == 5
    dep.faza("poarta_plasa", _acum(0), pid=dep.pid_viu())
    assert dep.ruleaza("1")[0] == 9


def test_p10_pid_reutilizat_de_alt_proces_pornit_dupa_inceput_e_mort(dep):
    pid = dep.pid_viu()
    dep.faza("poarta_verificator", _acum(-100), pid=pid)           # procesul trăiește, dar a pornit mult după rândul „inceput”
    assert dep.ruleaza("1", marja_pid=2)[0] == 5
    dep.faza("poarta_plasa", _acum(0), pid=pid)                     # același pid, dar cu start în marja de 2 s de rândul „inceput” al acestei faze: viu
    assert dep.ruleaza("1", marja_pid=2)[0] == 9                   # viu (cazul 2) înaintea mortului (cazul 3)


def test_p11_faza_vie_si_faza_moarta_in_n_e_9_cazul_2_inaintea_lui_3(dep):
    dep.faza("poarta_verificator", _acum(-30))
    dep.faza("poarta_pytest", _acum(0), pid=dep.pid_viu())
    assert dep.ruleaza("1")[0] == 9


def test_p12_faze_incheiate_normal_fara_verdict_peste_marja_e_5_si_in_marja_e_9(dep):
    dep.faza("poarta_verificator", _acum(-300), _acum(-250))
    dep.faza("poarta_pytest", _acum(-250), _acum(-200))
    rc, out, err = dep.ruleaza("1", marja=100)
    assert rc == 5 and "poartă încheiată fără verdict" in err
    assert dep.ruleaza("1", marja=1000)[0] == 9


def test_p13_rosu_1_si_infra_amestecate_fara_verdict_peste_marja_e_5_iar_cu_un_rosu_dupa_ele_e_1(dep):
    dep.faza("poarta_pytest", _acum(-300), _acum(-250), rezultat="rosu_1")
    dep.faza("poarta_plasa", _acum(-250), _acum(-200), rezultat="infra")
    assert dep.ruleaza("1", marja=100)[0] == 5
    dep.verdict("ROSU", _acum(-100))
    assert dep.ruleaza("1", marja=100)[0] == 1


def test_p14_infra_ultim_cu_o_intrare_peste_marja_e_4_si_in_marja_e_9(dep):
    dep.verdict("INFRA", _acum(-1000))
    dep.stare(infra=[{"sha": "b" * 40, "data": _acum(-1000), "motiv": "m"}])
    rc, out, _ = dep.ruleaza("1", marja=100)
    assert rc == 4
    _linie(out, "infra", "b" * 40)
    assert dep.ruleaza("1", marja=100000)[0] == 9


def test_p15_infra_si_faza_noua_vie_e_9_iar_cu_faza_noua_moarta_e_5_nu_4(dep):
    dep.verdict("INFRA", _acum(-1000))
    dep.stare(infra=[{"sha": "b" * 40, "data": _acum(-1000), "motiv": "m"}])
    dep.faza("poarta_verificator", _acum(0), pid=dep.pid_viu())
    assert dep.ruleaza("1", marja=100)[0] == 9
    dep.faza("poarta_pytest", _acum(-10))
    assert dep.ruleaza("1", marja=100)[0] == 9                     # vie înaintea mortei
    dep.procese[0].kill()
    dep.procese[0].wait()
    assert dep.ruleaza("1", marja=100)[0] == 5


def test_p16_infra_cu_trei_intrari_si_oprit_e_3(dep):
    dep.verdict("INFRA", _acum(-1000))
    dep.stare(oprit="infra ×3: 8019 ocupat", infra=[{"sha": "b" * 40, "data": _acum(-1000), "motiv": "m"}] * 3)
    assert dep.ruleaza("1")[0] == 3


def test_p17_niciun_rand_al_lotului_e_6_iar_alt_lot_cu_prefix_comun_nu_se_potriveste(dep):
    dep.verdict("VERDE", _acum(-5), lot="17.5-E2")
    dep.faza("poarta_verificator", _acum(-5), _acum(-2), lot="17.5-E2")
    rc, out, _ = dep.ruleaza("1", lot="17.5-E")
    assert rc == 6
    _linie_e = re.fullmatch(r"poarta 17\.5-E: nepornita -\n", out)
    assert _linie_e, out
    assert dep.ruleaza("1")[0] == 6


def test_p18_auto_potrivirea_un_argument_cu_textul_poarta_rulare_py_nu_tine_scriptul_in_bucla(dep):
    t0 = time.time()
    r = subprocess.run(["sh", os.path.join(RAD, "scripts", "asteapta_poarta.sh"), LOT, "3", "--dupa=" + _acum(0)], cwd=dep.dir, env=dict(os.environ, LOT_JURNAL=dep.jurnal, POARTA_X="poarta_rulare.py"),
                       capture_output=True, text=True, timeout=30)
    p = subprocess.Popen(["sleep", "30", "poarta_rulare.py"])         # un proces cu textul în linia de comandă nu schimbă nimic
    try:
        rc, out, _ = dep.ruleaza("2")
    finally:
        p.kill()
        p.wait()
    assert r.returncode == 6 and rc == 6 and time.time() - t0 < 15


@pytest.mark.parametrize("argv,lot", [((), None), (("abc",), LOT), (("5", "--dupa"), LOT), (("5", "--dupa="), LOT), (("5", "--dupa=nu-e-iso"), LOT), (("5", "--x"), LOT)])
def test_p19_argument_invalid_e_2_cu_uzul_pe_stderr_si_stdout_gol(dep, argv, lot):
    rc, out, err = dep.ruleaza(*argv, lot=lot)
    assert rc == 2 and out == "" and "Uz:" in err, (argv, rc, err)


def test_p20_secunde_max_541_e_2_iar_540_se_accepta(dep):
    rc, out, err = dep.ruleaza("541")
    assert rc == 2 and out == "" and "Uz:" in err
    dep.verdict("VERDE", _acum(-5))
    assert dep.ruleaza("540")[0] == 0


def test_p21_dupa_fara_fus_orar_e_2_cu_motivul_pe_stderr(dep):
    rc, out, err = dep.ruleaza("5", "--dupa=2026-11-09T10:00:00")
    assert rc == 2 and out == "" and "fus orar" in err and "Traceback" not in err


def test_p22_linia_de_iesire_si_sha_ul_ei_pe_fiecare_provenienta(dep, tmp_path):
    # 0 / 1: sha-ul lui V
    dep.verdict("VERDE", _acum(-5), sha="c" * 40)
    rc, out, _ = dep.ruleaza("1")
    assert rc == 0
    _linie(out, "verde", "c" * 40)
    # 3: fără V, sha-ul ultimei faze din N
    dep.stare(oprit="oprit de test aaa")
    d2 = Depozit(tmp_path / "alt")
    try:
        d2.faza("poarta_pytest", _acum(-30), _acum(-20), sha="d" * 12)
        d2.stare(oprit="oprit de test aaa")
        rc, out, _ = d2.ruleaza("1")
        assert rc == 3
        _linie(out, "oprit", "d" * 12)
    finally:
        d2.inchide()
    # 5 și 9: HEAD-ul curent, nu sha-ul unui V vechi cu alt sha
    dep.stare()
    dep.verdict("ROSU", _acum(-100), sha="e" * 40)
    dep.faza("poarta_pytest", _acum(-30))
    rc, out, _ = dep.ruleaza("1")
    assert rc == 5
    _linie(out, "intrerupt", dep.head())
    d3 = Depozit(tmp_path / "alt3")
    try:
        d3.verdict("ROSU", _acum(-100), sha="e" * 40)
        d3.faza("poarta_pytest", _acum(0), pid=d3.pid_viu())
        rc, out, _ = d3.ruleaza("1")
        assert rc == 9
        _linie(out, "in_curs", d3.head())
        assert "e" * 40 not in out
    finally:
        d3.inchide()
    # 4: sha-ul lui V; 6: „-”
    d4 = Depozit(tmp_path / "alt4")
    d4.verdict("INFRA", _acum(-1000), sha="f" * 40)
    d4.stare(infra=[{"sha": "f" * 40, "data": _acum(-1000), "motiv": "m"}])
    rc, out, _ = d4.ruleaza("1", marja=100)
    assert rc == 4
    _linie(out, "infra", "f" * 40)
    rc, out, err = d4.ruleaza("1", "--dupa=" + _acum(0))
    assert rc == 6 and out == "poarta %s: nepornita -\n" % LOT


def test_p23_rosu_vechi_si_faze_noi_incheiate_fara_verdict_nou_e_5_peste_marja_si_9_in_marja(dep):
    dep.verdict("ROSU", _acum(-1000))
    dep.faza("poarta_verificator", _acum(-300), _acum(-250))
    assert dep.ruleaza("1", marja=100)[0] == 5
    assert dep.ruleaza("1", marja=100000)[0] == 9


def test_p24_infra_cu_trei_intrari_si_oprit_gol_e_3(dep):
    dep.verdict("INFRA", _acum(-1000))
    dep.stare(infra=[{"sha": "b" * 40, "data": _acum(-1000), "motiv": "m"}] * 3)
    rc, out, _ = dep.ruleaza("1", marja=100)
    assert rc == 3
    _linie(out, "oprit", "b" * 40)


def test_p25_starea_ilizibila_e_eroare_de_unealta_7_nu_1_iar_argumentul_invalid_ramane_2(dep):
    with open(os.path.join(dep.comun, "lot_stare_17_5_U.json"), "w") as f:
        f.write("{nu e json")
    rc, out, err = dep.ruleaza("1")
    assert rc == 7 and out == "" and "eroare de unealtă" in err
    assert dep.ruleaza("abc")[0] == 2


def test_p26_reluarea_tipareste_linia_reia_si_nu_scrie_in_poarta_verdicte():
    """Pe o reluare, `decide` întoarce REIA_CURAT / REIA_ROSU și niciun rând pentru poarta_verdicte.log (`linie` None); `main` tipărește «[poarta] <verdict> <sha> (<ramura>) …» și scrie în
    poarta_verdicte.log numai când `decide` cere o linie (o încercare infra: INFRA; o rulare completă: VERDE / ROSU)."""
    import poarta_rulare as R
    clase = {k: [] for k in ("regresie", "restanta", "baza_mutata", "nou_regresie", "invalid", "infra", "asertiuni_scazute", "reparat", "noi_verzi")}
    for rez, verdict in ((clase, "REIA_CURAT"), (dict(clase, regresie=["frontend_test/e2e/e2e_y.py::test_y"]), "REIA_ROSU")):
        d = R.decide({"complete": [], "reluari": [], "regresii": [], "oprit": None}, rez, True, [], "s" * 40, "t", "", "r" * 40)
        assert d["verdict"] == verdict and d["linie"] is None
    sursa = open(os.path.join(RAD, "scripts", "poarta_rulare.py"), encoding="utf-8").read()
    assert 'print("[poarta] %s %s (%s) · %d teste' in sursa and re.search(r'elif d\["linie"\]:\n\s+open\(jv, "a"', sursa)
    assert len(re.findall(r'open\(jv, "a"', sursa)) == 2          # INFRA și VERDE / ROSU, ambele sub `d["linie"]`


# ── U.4 — scripts/genereaza_manifest_plasa.py nu scrie decât la --scrie ───────────────────────────────────────────────────────────────────────────
def _sha_fisier(c):
    import hashlib
    return hashlib.sha256(open(c, "rb").read()).hexdigest()


def _manifest_copie(tmp_path):
    c = str(tmp_path / "m.manifest")
    shutil.copy(os.path.join(RAD, "scripts", "plasa_16_2.manifest"), c)
    return c


def _gen(*argv):
    return subprocess.run([PY, os.path.join(RAD, "scripts", "genereaza_manifest_plasa.py"), *argv], cwd="/tmp", capture_output=True, text=True, timeout=120)


@pytest.mark.parametrize("cerere", ["--help", "-h"])
def test_u4_help_tipareste_uzul_pe_stdout_cu_ieșirea_0_si_manifestul_neatins(tmp_path, cerere):
    c = _manifest_copie(tmp_path)
    h = _sha_fisier(c)
    r = _gen(cerere, c)
    assert r.returncode == 0 and "Uz:" in r.stdout and "--scrie" in r.stdout and _sha_fisier(c) == h


@pytest.mark.parametrize("argv", [(), ("CALE",), ("--x",), ("--scrie", "--verifica", "CALE"), ("--x", "CALE")])
def test_u4_fara_optiune_calea_singura_optiunea_necunoscuta_si_scrie_cu_verifica_sunt_2_fara_scriere(tmp_path, argv):
    c = _manifest_copie(tmp_path)
    h = _sha_fisier(c)
    r = _gen(*[c if a == "CALE" else a for a in argv])
    assert r.returncode == 2 and r.stdout == "" and "Uz:" in r.stderr and _sha_fisier(c) == h, (argv, r.stdout[-200:], r.stderr[-300:])


def test_u4_scrie_refuza_un_rand_care_nu_e_in_lista_aprobata_cu_rândul_numit_si_copia_neschimbata(tmp_path):
    c = _manifest_copie(tmp_path)
    with open(c, "a", encoding="utf-8") as f:
        f.write("frontend_test/e2e/e2e_inventat_u4.py\tabc\t3\tpython -m pytest -q x\n")
    h = _sha_fisier(c)
    r = _gen("--scrie", c)
    assert r.returncode == 1 and "e2e_inventat_u4.py" in r.stdout and _sha_fisier(c) == h


def test_u4_verifica_pe_o_copie_cu_hash_gresit_e_1_si_nu_scrie(tmp_path):
    c = str(tmp_path / "m.manifest")
    primul = next(ln for ln in open(os.path.join(RAD, "scripts", "plasa_16_2.manifest"), encoding="utf-8") if ln.strip() and not ln.startswith("#")).split("\t")
    open(c, "w", encoding="utf-8").write("\t".join([primul[0], "0" * 64, primul[2], primul[3]]))
    h = _sha_fisier(c)
    r = _gen("--verifica", c)
    assert r.returncode == 1 and "hash diferit" in r.stdout and _sha_fisier(c) == h


# ── U.5 — motivul opririi în alertă ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def _alerta_falsa(tmp_path):
    fals = tmp_path / "alerta_falsa.sh"
    fals.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$ALERTA_OUT"\n')
    fals.chmod(0o755)
    return str(fals), str(tmp_path / "alerta.out")


def _incheie(tmp_path, *argv):
    fals, out = _alerta_falsa(tmp_path)
    d = tmp_path / "oprit"
    d.mkdir(exist_ok=True)
    r = subprocess.run(["sh", os.path.join(RAD, "scripts", "incheie_lot.sh"), *argv], capture_output=True, text=True, timeout=30,
                       env=dict(os.environ, OPRIT_DIR=str(d), ALERTA_CMD=fals, ALERTA_OUT=out))
    argumente = open(out, encoding="utf-8").read().splitlines() if os.path.exists(out) else None
    return r, d, argumente


def test_u5_nepublicat_cu_motiv_il_da_alertei_si_scrie_fisierul(tmp_path):
    r, d, arg = _incheie(tmp_path, LOT, "nepublicat", "-", "poarta roșie după a doua rulare")
    assert r.returncode == 0 and (d / "OPRIT_17.5-U.txt").read_text().startswith("OPRIT — gata: 17.5-U nepublicat -")
    assert arg == ["lot", LOT, "nepublicat", "-", "poarta roșie după a doua rulare"]


@pytest.mark.parametrize("motiv", [None, "", "scurt", "   scurt   "])
def test_u5_nepublicat_fara_motiv_sau_sub_10_caractere_nu_refuza_si_alerta_primeste_motivul_implicit(tmp_path, motiv):
    argv = [LOT, "nepublicat", "-"] + ([] if motiv is None else [motiv])
    r, d, arg = _incheie(tmp_path, *argv)
    assert r.returncode == 0 and (d / "OPRIT_17.5-U.txt").exists() and "motiv implicit" in r.stdout
    assert arg == ["lot", LOT, "nepublicat", "-", "fără motiv declarat"]


def test_u5_publicat_nu_cere_motiv(tmp_path):
    r, d, arg = _incheie(tmp_path, LOT, "publicat", "a" * 40)
    assert r.returncode == 0 and "motiv implicit" not in r.stdout and arg == ["lot", LOT, "publicat", "a" * 40, ""]


def test_u5_motiv_stop_scoate_textul_de_dupa_nepublicat_si_are_motiv_de_rezerva():
    import motiv_oprire as M
    text = "[publica_lot] STOP: starea lotului nu arată o rulare completă curată (oprit=None)\n[publica_lot] STOP: lipsește raportul\nOPRIT — gata: 17.5-U nepublicat, starea lotului nu arată o rulare completă curată (oprit=None)\n"
    assert M.motiv_stop(text, 1) == "starea lotului nu arată o rulare completă curată (oprit=None)"
    rezerva = M.motiv_stop("Traceback (most recent call last):\nKeyError: 'complete'\n", 1)
    assert rezerva == "publica_lot.py a ieșit cu cod 1 fără linie OPRIT" and len(rezerva) > 10


def test_u5_ieșirea_reală_cu_stop_da_primul_stop_fara_prefix():
    """(ii) ieșirea reală a lui scripts/publica_lot.py cu STOP, produsă în worktree-ul lotului înainte de poartă (docs/dovezi/17_5_U/publica_stop.out)."""
    import motiv_oprire as M
    cale = os.path.join(RAD, "docs", "dovezi", "17_5_U", "publica_stop.out")
    if not os.path.exists(cale):
        pytest.skip("ieșirea reală cu STOP se produce în lot, înainte de poartă (punctul 6 (ii))")
    text = open(cale, encoding="utf-8").read()
    stopuri = [ln.split("[publica_lot] STOP: ", 1)[1] for ln in text.splitlines() if ln.startswith("[publica_lot] STOP: ")]
    assert stopuri and M.motiv_stop(text, 1) == stopuri[0]


def _depozit_publicare(tmp_path, publica_py):
    dep = tmp_path / "dep"
    (dep / "scripts").mkdir(parents=True)
    for f in ("publica_lot.sh", "incheie_lot.sh", "jurnal_lot.py", "poarta_lib.py", "motiv_oprire.py"):
        shutil.copy(os.path.join(RAD, "scripts", f), dep / "scripts" / f)
    (dep / "scripts" / "publica_lot.py").write_text(publica_py)
    (dep / ".gitignore").write_text("__pycache__/\n")
    for c in (["init", "-q", "-b", "lucru/lot17-5u"], ["add", "-A"], ["-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "x"]):
        subprocess.run(["git", *c], cwd=dep, check=True)
    return dep


def _ruleaza_publica(tmp_path, publica_py):
    dep = _depozit_publicare(tmp_path, publica_py)
    fals, out = _alerta_falsa(tmp_path)
    d = tmp_path / "oprit"
    d.mkdir()
    r = subprocess.run(["sh", "scripts/publica_lot.sh"], cwd=dep, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, OPRIT_DIR=str(d), ALERTA_CMD=fals, ALERTA_OUT=out, LOT=LOT, LOT_JURNAL=str(tmp_path / "j.log"), PYTHONDONTWRITEBYTECODE="1"))
    return r, d, open(out, encoding="utf-8").read().splitlines() if os.path.exists(out) else None


def test_u5_publica_lot_sh_cu_publica_lot_py_care_iese_cu_1_fara_linie_oprit_da_motivul_de_rezerva(tmp_path):
    r, d, arg = _ruleaza_publica(tmp_path, "import sys\nprint('ceva fără linia cerută')\nsys.exit(1)\n")
    assert r.returncode == 1 and (d / "OPRIT_17.5-U.txt").exists() and "ceva fără linia cerută" in r.stdout
    assert arg == ["lot", LOT, "nepublicat", "-", "publica_lot.py a ieșit cu cod 1 fără linie OPRIT"]


def test_u5_publica_lot_sh_cu_publica_lot_py_care_tipareste_linia_oprit_da_motivul_ei(tmp_path):
    r, d, arg = _ruleaza_publica(tmp_path, "import sys\nprint('[publica_lot] STOP: pragul depășit')\nprint('OPRIT — gata: 17.5-U nepublicat, pragul depășit')\nsys.exit(1)\n")
    assert r.returncode == 1 and (d / "OPRIT_17.5-U.txt").exists()
    assert arg == ["lot", LOT, "nepublicat", "-", "pragul depășit"]


# ── U.6 — scripts/teste_locuri_schimbate.py ──────────────────────────────────────────────────────────────────────────────────────────────────
def _git(dep, *a):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a], cwd=dep, capture_output=True, text=True, check=True).stdout.strip()


def _depozit_locuri(tmp_path):
    dep = tmp_path / "loc"
    for c in ("static/js", "core", "frontend_test/e2e", "scripts"):
        (dep / c).mkdir(parents=True)
    (dep / "static/js/ecran.js").write_text('function deschideFereastra() { return "Salvează nota"; }\nconst v = "/static/x.js?v=aaaa1111";\nconst azi = new Date();\n')
    (dep / "core/test_citeste_locul.py").write_text('def test_a():\n    assert "deschideFereastra" in "x"\n')
    (dep / "frontend_test/e2e/e2e_nu_citeste.py").write_text('def test_b():\n    assert 1\n')
    (dep / "frontend_test/e2e/e2e_azi.py").write_text('import datetime\ndef test_c():\n    assert datetime.date.today()\n')
    (dep / "scripts/plasa_16_2.manifest").write_text("# m\nfrontend_test/e2e/e2e_azi.py\th\t1\tc\n")
    _git(dep, "init", "-q", "-b", "x")
    _git(dep, "add", "-A")
    _git(dep, "commit", "-q", "-m", "baza")
    return dep


def _locuri(dep, baza, commit):
    return subprocess.run([PY, os.path.join(RAD, "scripts", "teste_locuri_schimbate.py"), baza, commit, "--depozit=" + str(dep)], capture_output=True, text=True, timeout=60)


def test_u6_listeaza_testul_care_contine_locul_schimbat_si_nu_pe_celalalt(tmp_path):
    dep = _depozit_locuri(tmp_path)
    baza = _git(dep, "rev-parse", "HEAD")
    (dep / "static/js/ecran.js").write_text('function deschideFereastraNoua() { return "Salvează nota"; }\nconst v = "/static/x.js?v=bbbb2222";\nconst azi = new Date();\n')
    _git(dep, "commit", "-qam", "schimbat")
    r = _locuri(dep, baza, "HEAD")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "core/test_citeste_locul.py" in r.stdout or "deschideFereastra" in r.stdout
    (dep / "core/test_citeste_locul.py").write_text('def test_a():\n    assert "deschideFereastraNoua" in "x"\n')
    _git(dep, "commit", "-qam", "test")
    r = _locuri(dep, baza, "HEAD")
    assert re.search(r"core/test_citeste_locul\.py\s+în afara plasei", r.stdout) and "e2e_nu_citeste.py" not in r.stdout
    assert "e2e_azi.py                                                   în plasă" not in r.stdout.split("citesc data de azi")[0]
    assert re.search(r"citesc data de azi.*: da\): 1", r.stdout) and "e2e_azi.py" in r.stdout.split("citesc data de azi")[1]


def test_u6_o_linie_care_difera_numai_prin_hash_ul_de_versiune_nu_produce_locuri(tmp_path):
    dep = _depozit_locuri(tmp_path)
    baza = _git(dep, "rev-parse", "HEAD")
    (dep / "static/js/ecran.js").write_text('function deschideFereastra() { return "Salvează nota"; }\nconst v = "/static/x.js?v=cccc3333";\nconst azi = new Date();\n')
    _git(dep, "commit", "-qam", "numai hash")
    r = _locuri(dep, baza, "HEAD")
    assert r.returncode == 0 and "locuri schimbate: 0" in r.stdout and "teste care citesc locurile schimbate: 0 fișiere" in r.stdout


def test_u6_diff_gol_sau_commit_lipsa_e_1_cu_motivul(tmp_path):
    dep = _depozit_locuri(tmp_path)
    baza = _git(dep, "rev-parse", "HEAD")
    r = _locuri(dep, baza, baza)
    assert r.returncode == 1 and "nu atinge" in r.stdout
    r = _locuri(dep, baza, "0" * 40)
    assert r.returncode == 1 and "commit lipsă" in r.stdout


# ── U.7 — scripts/inventar_rosii_baza.py ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_u7_o_intrare_cu_sase_randuri_FAILED_da_cate_o_cauza_pe_fiecare_dintre_cele_sase(tmp_path):
    dep = tmp_path / "inv"
    for c in ("static/js", "frontend_test/e2e", "core"):
        (dep / c).mkdir(parents=True)
    (dep / "core/ceas_proba.py").write_text("DATA_REF = 1\n")
    (dep / "static/js/p1.js").write_text('const c = document.getElementById("camp-data-x");\nconst d = new Date();\n')
    (dep / "static/js/p2.js").write_text('const c = document.getElementById("alt-camp-yy");\nconst t = Date.now();\n')
    (dep / "frontend_test/e2e/e2e_x.py").write_text(
        "import datetime as _dt\nfrom core.ceas_proba import DATA_REF\nAZI = _dt.date.today()\n\n\n"
        "def test_inghetat():\n    assert DATA_REF and '#camp-data-x'\n\n\n"
        "def test_luna():\n    d = _dt.datetime.now()\n    assert d.month\n\n\n"
        "def test_azi():\n    assert AZI\n\n\n"
        "def test_pagina():\n    assert '#alt-camp-yy'\n\n\n"
        "def test_alta():\n    assert 1 == 1\n")
    _git(dep, "init", "-q", "-b", "x")
    _git(dep, "add", "-A")
    _git(dep, "commit", "-q", "-m", "baza")
    sha = _git(dep, "rev-parse", "HEAD")
    intrare = tmp_path / "intrare.txt"
    f = "frontend_test/e2e/e2e_x.py"
    intrare.write_text("aceleași fișiere roșii (main %s)\n%s | exit=1\n" % (sha, "e2e_x") + "".join("FAILED %s::%s\n" % (f, t) for t in ("test_inghetat", "test_luna", "test_azi", "test_pagina", "test_alta", "test_lipsa")) + "FIN\n")
    iesire = tmp_path / "iesire.txt"
    r = subprocess.run([PY, os.path.join(RAD, "scripts", "inventar_rosii_baza.py"), str(intrare), "--iesire=" + str(iesire), "--depozit=" + str(dep)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    randuri = {ln.split(" | ")[1]: ln.split(" | ")[2:] for ln in iesire.read_text(encoding="utf-8").splitlines()}
    assert len(randuri) == 6
    assert randuri["test_inghetat"][0] == "ceas înghețat" and randuri["test_inghetat"][1].startswith("static/js/p1.js:")
    assert randuri["test_luna"][0] == "luna curentă" and randuri["test_luna"][1] == "frontend_test/e2e/e2e_x.py:11"
    assert randuri["test_azi"][0] == "data de azi" and randuri["test_azi"][1] == "frontend_test/e2e/e2e_x.py:3"
    assert randuri["test_pagina"][0] == "ceasul paginii" and randuri["test_pagina"][1].startswith("static/js/p2.js:")
    assert randuri["test_alta"][0] == "altă cauză" and randuri["test_alta"][1] == "frontend_test/e2e/e2e_x.py:23"
    assert randuri["test_lipsa"][0] == "necunoscută"


# ── U.1 — verificator_design.elibereaza_port ─────────────────────────────────────────────────────────────────────────────────────────────────
SERVER_FALS = ("import socket, sys, time\ns = socket.socket()\ns.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)\ns.bind(('127.0.0.1', int(sys.argv[1])))\ns.listen(1)\n"
               "time.sleep(300)\n")


def _port_liber():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class ServerFals:
    """Un server fals pe un port dat: un script python al cărui nume conține «uvicorn», pornit din `director` într-o sesiune proprie."""

    def __init__(self, tmp_path, director, port):
        import verificator_design as VD
        os.makedirs(director, exist_ok=True)
        script = os.path.join(str(tmp_path), "uvicorn_fals.py")
        open(script, "w").write(SERVER_FALS)
        self.port, self.director = port, os.path.realpath(director)
        self.p = subprocess.Popen([PY, script, str(port)], cwd=director, start_new_session=True)
        for _ in range(50):
            if VD.port_ocupat(port):
                break
            time.sleep(0.1)
        assert VD.port_ocupat(port)

    def viu(self):
        return self.p.poll() is None

    def inchide(self):
        if self.p.poll() is None:
            self.p.kill()
        self.p.wait()


@pytest.fixture
def servere():
    lista = []
    yield lista
    for s in lista:
        s.inchide()


def _vd():
    import verificator_design as VD
    return VD


def test_u1_port_liber_nimic_de_oprit_si_nimic_in_jurnal(tmp_path, monkeypatch):
    monkeypatch.setenv("LOT_JURNAL", str(tmp_path / "j.log"))
    ok, motiv = _vd().elibereaza_port(_port_liber(), lot=LOT, unelte=[str(tmp_path)], productie=[])
    assert ok and motiv == "" and not os.path.exists(tmp_path / "j.log")


def test_u1_server_din_alt_director_e_refuzat_cu_pid_si_director_iar_serverul_ramane_viu(tmp_path, servere, capsys):
    port = _port_liber()
    srv = ServerFals(tmp_path, str(tmp_path / "alt"), port)
    servere.append(srv)
    ok, motiv = _vd().elibereaza_port(port, lot=LOT, unelte=[str(tmp_path / "unelte")], productie=[])
    err = capsys.readouterr().err
    assert not ok and motiv.startswith("%d ocupat de pid %d (" % (port, srv.p.pid))   # comanda din motiv se taie la 120 de caractere: calea temporară sub xdist poate ascunde numele scriptului
    assert ("pid %d" % srv.p.pid) in err and srv.director in err and srv.viu()


def test_u1_server_din_directorul_temporar_al_uneltelor_e_oprit_portul_e_liber_si_linia_din_jurnal(tmp_path, servere, monkeypatch, capsys):
    monkeypatch.setenv("LOT_JURNAL", str(tmp_path / "j.log"))
    port = _port_liber()
    srv = ServerFals(tmp_path, str(tmp_path / "unelte" / "arb"), port)
    servere.append(srv)
    ok, motiv = _vd().elibereaza_port(port, lot=LOT, unelte=[str(tmp_path / "unelte")], productie=[])
    assert ok and motiv == "" and not _vd().port_ocupat(port) and srv.p.wait(timeout=10) is not None
    out = capsys.readouterr().out
    assert str(srv.p.pid) in out and srv.director in out and "uvicorn_fals.py" in out and "pornit" in out
    rand = [ln.split("\t") for ln in open(tmp_path / "j.log", encoding="utf-8") if "\telibereaza_8019\t" in ln]
    assert [r[2] for r in rand] == ["inceput", "sfarsit"] and rand[1][5] == "ok"
    assert ("pid %d" % srv.p.pid) in rand[0][8] and srv.director in rand[0][8] and "uvicorn_fals.py" in rand[0][8] and "pornit" in rand[0][8]


def test_u1_pid_invizibil_sau_cwd_ilizibil_e_refuz_iar_serverul_ramane_viu(tmp_path, servere):
    port = _port_liber()
    srv = ServerFals(tmp_path, str(tmp_path / "unelte" / "arb"), port)
    servere.append(srv)
    real = _vd().proprietari_port(port)[0]
    for fals in ({"pid": None, "comanda": "", "director": None, "pornit": "?"}, dict(real, director=None)):
        ok, motiv = _vd().elibereaza_port(port, lot=LOT, unelte=[str(tmp_path / "unelte")], productie=[], proprietari=lambda _p, f=fals: [f])
        assert not ok and srv.viu()


def test_u1_cwd_sub_radacina_de_productie_e_refuz_chiar_cu_uvicorn_in_linia_de_comanda(tmp_path, servere):
    port = _port_liber()
    srv = ServerFals(tmp_path, str(tmp_path / "prod" / "iconta_nou"), port)
    servere.append(srv)
    ok, motiv = _vd().elibereaza_port(port, lot=LOT, unelte=[str(tmp_path)], productie=[str(tmp_path / "prod")])
    assert not ok and srv.viu() and "uvicorn" in srv.p.args[1]


def test_u1_blocul_vechi_cu_sonda_si_oprire_injectate_cheama_oprirea_o_singura_data_pe_sonda_true_si_deloc_pe_false():
    VD = _vd()
    opriri = []
    assert VD.elibereaza_port(8019, sonda=lambda: True, opreste_fn=lambda: opriri.append(1)) == (True, "") and opriri == [1]
    assert VD.elibereaza_port(8019, sonda=lambda: False, opreste_fn=lambda: opriri.append(1)) == (True, "") and opriri == [1]


def test_u1_porneste_refuza_cu_1_si_numele_procesului_cand_portul_e_ocupat(tmp_path, servere, monkeypatch, capsys):
    VD = _vd()
    port = _port_liber()
    srv = ServerFals(tmp_path, str(tmp_path / "x"), port)
    servere.append(srv)
    monkeypatch.setattr(VD, "PORT", port)
    assert VD.porneste() == 1
    err = capsys.readouterr().err
    assert "REFUZ" in err and ("pid %d" % srv.p.pid) in err and "uvicorn_fals.py" in err and srv.viu()


# ── U.2 — eroarea de infrastructură nu consumă o rulare ──────────────────────────────────────────────────────────────────────────────────────
REPLAY = os.path.join(RAD, "docs", "dovezi", "17_5_U", "replay_E")
CLASE = ("regresie", "restanta", "baza_mutata", "nou_regresie", "invalid", "infra", "asertiuni_scazute", "reparat", "noi_verzi")
SESIUNE = "plasa_e2e::sesiune"
DISPARUT = "frontend_test/e2e/e2e_x.py::test_x (a dispărut din rulare)"


def _rez(**kw):
    return dict({k: [] for k in CLASE}, **kw)


def _stare_proaspata():
    return {"complete": [], "reluari": [], "regresii": [], "oprit": None}


def _replay():
    stare = json.load(open(os.path.join(REPLAY, "lot_stare_17_5_E.json"), encoding="utf-8"))
    picate = json.load(open(os.path.join(REPLAY, "lot_picate_17_5_E.json"), encoding="utf-8"))
    return stare, picate


def test_u2_replay_E_copiile_au_starea_reala_a_lotului_17_5_E():
    stare, picate = _replay()
    assert stare["oprit"] == "eroare de infrastructură rămasă după o reluare: plasa_e2e::sesiune"
    assert len(stare["complete"]) == 1 and stare["complete"][0]["sha"].startswith("2458968b") and stare["complete"][0]["curat"] is False
    assert len(stare["regresii"]) == 74 and all(n.endswith("(a dispărut din rulare)") for n in stare["regresii"])
    assert len(picate["clase"]["regresie"]) == 74 and picate["clase"]["infra"] == [SESIUNE]
    assert open(os.path.join(REPLAY, "poarta_verdicte_rand_ROSU.txt"), encoding="utf-8").read().startswith("ROSU 2458968b")


def test_u2_1_pe_clasificarea_reala_din_E_decizia_e_incercare_infra_cod_4_fara_scrieri_in_complete_regresii_picate_oprit():
    import poarta_rulare as R
    stare, picate = _replay()
    d = R.decide(stare, picate["clase"], False, [], picate["sha"], "2026-11-10T10:00:00", "plasa_e2e::sesiune: cod 3 fără raport junit")
    assert d["infra"] and d["cod"] == 4 and d["linie"] == "INFRA" and d["verdict"] == "INFRA" and d["ultima"] is None and d["scrie_picate"] is False
    assert d["stare"]["complete"] == stare["complete"] and d["stare"]["regresii"] == stare["regresii"] and d["stare"]["reluari"] == stare["reluari"]
    assert len(d["stare"]["infra"]) == 1 and d["stare"]["oprit"] == stare["oprit"] and d["stare"]["oprit"]
    assert d["stare"]["infra"][0]["sha"] == picate["sha"]


def test_u2_2_scrierea_de_stare_din_main_pe_copii_lasa_lot_picate_si_regresiile_identice(tmp_path):
    import hashlib
    import poarta_rulare as R
    stare, picate = _replay()
    f_stare, f_picate = str(tmp_path / "lot_stare.json"), str(tmp_path / "lot_picate.json")
    shutil.copy(os.path.join(REPLAY, "lot_stare_17_5_E.json"), f_stare)
    shutil.copy(os.path.join(REPLAY, "lot_picate_17_5_E.json"), f_picate)
    h = hashlib.sha256(open(f_picate, "rb").read()).hexdigest()
    d = R.decide(stare, picate["clase"], False, [], picate["sha"], "2026-11-10T10:00:00", "m")
    R.scrie_stare(d, f_stare, f_picate, picate["sha"], sorted(picate["picate"]), picate["clase"])
    dupa = json.load(open(f_stare, encoding="utf-8"))
    assert hashlib.sha256(open(f_picate, "rb").read()).hexdigest() == h
    assert dupa["regresii"] == stare["regresii"] and len(dupa["regresii"]) == 74 and len(dupa["complete"]) == 1 and len(dupa["infra"]) == 1


def test_u2_3_o_incercare_infra_urmata_de_o_regresie_reala_noua_nu_e_a_doua_regresie_de_lot():
    import poarta_rulare as R
    stare = _stare_proaspata()
    infra = R.decide(stare, _rez(infra=[SESIUNE], regresie=[DISPARUT]), False, [], "s1", "t1", "m")
    assert infra["cod"] == 4 and infra["stare"]["oprit"] is None and infra["stare"]["regresii"] == []
    real = R.decide(infra["stare"], _rez(regresie=["frontend_test/e2e/e2e_y.py::test_y"]), False, [], "s2", "t2")
    assert real["stare"]["oprit"] is None and real["stare"]["regresii"] == ["frontend_test/e2e/e2e_y.py::test_y"] and real["stare"]["infra"] == []
    assert real["cod"] == 1 and real["linie"] == "ROSU" and len(real["stare"]["complete"]) == 1 and real["scrie_picate"]


def test_u2_4_infra_plus_o_regresie_reala_e_cazul_mixt_numarat_ca_azi():
    import poarta_rulare as R
    d = R.decide(_stare_proaspata(), _rez(infra=[SESIUNE], regresie=["frontend_test/e2e/e2e_y.py::test_y"]), False, [], "s1", "t1")
    assert not d["infra"] and d["linie"] == "ROSU" and len(d["stare"]["complete"]) == 1 and d["stare"]["oprit"].startswith("eroare de infrastructură") and d["cod"] == 3
    mixt_cu_raport = R.decide(_stare_proaspata(), _rez(infra=[SESIUNE, "frontend_test/e2e/e2e_z.py::test_z"]), False, [], "s1", "t1")
    assert not mixt_cu_raport["infra"] and mixt_cu_raport["cod"] == 3


@pytest.mark.parametrize("regresii,cod,linie", [([], 0, "VERDE"), (["frontend_test/e2e/e2e_y.py::test_y"], 1, "ROSU")])
def test_u2_5_fara_infra_se_numara_ca_azi(regresii, cod, linie):
    import poarta_rulare as R
    d = R.decide(_stare_proaspata(), _rez(regresie=regresii), False, [], "s1", "t1")
    assert not d["infra"] and d["cod"] == cod and d["linie"] == linie and len(d["stare"]["complete"]) == 1 and d["stare"]["oprit"] is None


def test_u2_6_trei_incercari_infra_consecutive_opresc_lotul_cu_infra_x3_si_ieșirea_3():
    import poarta_rulare as R
    stare = _stare_proaspata()
    coduri = []
    for k in range(3):
        d = R.decide(stare, _rez(infra=[SESIUNE], regresie=[DISPARUT]), False, [], "s1", "t%d" % k, "8019 ocupat de pid 1 (uvicorn)")
        stare = d["stare"]
        coduri.append(d["cod"])
    assert coduri == [4, 4, 3] and stare["oprit"] == "infra ×3: 8019 ocupat de pid 1 (uvicorn)" and len(stare["infra"]) == 3 and stare["complete"] == []


def _wt_infra(tmp_path, cod, xml=None):
    wt, j = tmp_path / "wt", tmp_path / "J"
    (wt / "scripts" / "bin").mkdir(parents=True, exist_ok=True)
    j.mkdir(exist_ok=True)
    (wt / "scripts" / "baza_test.sh").write_text("#!/bin/sh\nexit 0\n")
    fals = "import os, sys\n"
    if xml:
        fals += "x = [a for a in os.environ['PYTEST_ADDOPTS'].split() if a.startswith('--junitxml=')][0].split('=', 1)[1]\nopen(x, 'w').write(%r)\n" % xml
    fals += "sys.exit(%d)\n" % cod
    (wt / "scripts" / "e2e_poarta.py").write_text(fals)
    if not (wt / "venv").exists():
        os.symlink(os.path.join(RAD, "venv"), wt / "venv")
    return str(wt), str(j)


def _rezultate_plasa(jurnal):
    import jurnal_lot as JL
    return [r[5] for r in JL.citeste_jurnal(jurnal) if len(r) > 6 and r[1] == "poarta_plasa" and r[2] == "sfarsit"]


def test_u2_ii_plasa_care_iese_cu_3_fara_xml_e_infra_in_jurnal_iar_cu_o_picatura_in_xml_ramane_rosu_1(tmp_path, monkeypatch):
    import poarta_lib as L
    monkeypatch.setenv("LOT_JURNAL", str(tmp_path / "j.log"))
    wt, j = _wt_infra(tmp_path, 3)
    L.ruleaza_trepte(wt, j, LOT, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False, sonda_8019=lambda: False, opreste_8019=lambda: None)
    assert _rezultate_plasa(str(tmp_path / "j.log")) == ["infra"]
    xml = '<testsuites><testsuite><testcase classname="e2e_x" name="t1"><failure message="Connection refused"/></testcase></testsuite></testsuites>'
    wt, j = _wt_infra(tmp_path, 1, xml)
    L.ruleaza_trepte(wt, j, LOT, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False, sonda_8019=lambda: False, opreste_8019=lambda: None)
    assert _rezultate_plasa(str(tmp_path / "j.log")) == ["infra", "rosu_1"]


def test_u2_ii_8019_ocupat_de_un_proces_strain_plasa_nu_porneste_si_treapta_e_infra_cu_motivul(tmp_path, servere, monkeypatch):
    import poarta_lib as L
    monkeypatch.setenv("LOT_JURNAL", str(tmp_path / "j.log"))
    VD = _vd()
    port = _port_liber()
    srv = ServerFals(tmp_path, str(tmp_path / "strain"), port)
    servere.append(srv)
    martor = tmp_path / "martor"
    wt, j = _wt_infra(tmp_path, 0)
    open(os.path.join(wt, "scripts", "e2e_poarta.py"), "w").write("open(%r, 'w').write('rulat')\n" % str(martor))
    monkeypatch.setattr(VD, "PORT", port)
    orig = VD.elibereaza_port
    monkeypatch.setattr(VD, "elibereaza_port", lambda p=None, **kw: orig(port, unelte=[str(tmp_path / "unelte")], productie=[], **kw))
    _, teste = L.ruleaza_trepte(wt, j, LOT, pytest_ids=[], e2e_fisiere=["e2e_x.py"], verificator=False)
    sesiune = [t for t in teste if t["nume"] == "plasa_e2e::sesiune"]
    assert len(sesiune) == 1 and sesiune[0]["infra"] and sesiune[0]["mesaj"].startswith("%d ocupat de pid %d (" % (port, srv.p.pid))
    assert not martor.exists() and srv.viu() and _rezultate_plasa(str(tmp_path / "j.log")) == ["infra"]


def test_u2_rez_run_ordinea_rosu_infra_verde():
    import jurnal_lot as JL
    assert JL._rez_run(["verde", "infra"]) == "infra" and JL._rez_run(["verde", "infra", "rosu_1"]) == "rosu"
    assert JL._rez_run(["verde"]) == "verde" and JL._rez_run([]) == "rosu" and JL._rez_run(["verde_cu_restante", "infra"]) == "infra"
    assert JL._rez_run(["intrerupt", "infra"]) == "rosu"


def test_u2_runda_infra_urmata_de_una_verde_da_dupa_infra_iar_tabelul_nu_o_numara_rosie():
    import jurnal_lot as JL
    import raport_timp_lot as RT

    def rand(faza, tip, ora, rez, id_):
        return [LOT, faza, tip, ora, "s" * 12, rez, id_, "1", ""]
    t = datetime.datetime(2026, 11, 10, 10, 0, 0).astimezone()
    ora = lambda m: (t + datetime.timedelta(minutes=m)).isoformat(timespec="seconds")  # noqa: E731
    rows = [rand("pornire", "inceput", ora(0), "-", "p"), rand("pornire", "sfarsit", ora(0), "ok", "p"), rand("hook", "inceput", ora(1), "-", "h"), rand("hook", "sfarsit", ora(2), "verde", "h"),
            rand("poarta_verificator", "inceput", ora(3), "-", "v1"), rand("poarta_verificator", "sfarsit", ora(4), "verde", "v1"),
            rand("poarta_plasa", "inceput", ora(4), "-", "e1"), rand("poarta_plasa", "sfarsit", ora(5), "infra", "e1"),
            rand("poarta_verificator", "inceput", ora(15), "-", "v2"), rand("poarta_verificator", "sfarsit", ora(16), "verde", "v2"),
            rand("poarta_plasa", "inceput", ora(16), "-", "e2"), rand("poarta_plasa", "sfarsit", ora(25), "verde", "e2")]
    runde = JL.runde_poarta(rows, LOT)
    assert [r["rezultat"] for r in runde] == ["infra", "verde"]
    derivate = JL.deriva_lucru(rows, LOT)
    interval = [x for x in derivate if x["faza"] == "dupa_infra"]
    assert len(interval) == 1 and interval[0]["inceput"] == ora(5) and interval[0]["sfarsit"] == ora(3 + 12) and not [x for x in derivate if x["faza"] in ("dupa_verde", "reparatie_dupa_rosu")]
    rl = [{"faza": x["faza"], "id": "c", "inceput": x["inceput"], "sfarsit": x["sfarsit"], "rezultat": x["rezultat"], "secunde": JL._sec(x["inceput"], x["sfarsit"]), "complet": True, "intrerupt": False,
           "pid": "", "detalii": ""} for x in derivate]
    linie = next(ln for ln in RT.tabel_faze(rl) if ln.startswith("| asteptare_poarta"))
    assert linie.split("|")[4].strip() == "0"                     # rulări roșii: infra nu e numărată roșie
    assert "dupa_infra" in JL.FAZE_LUCRU


def test_u2_pragurile_ignora_rularile_infra_si_le_numara_separat():
    import publica_lot as P
    durate = [("poarta_plasa", "1", "a", "b", "infra", 9999), ("poarta_plasa", "2", "a", "b", "verde", 100), ("poarta_plasa", "3", "a", "b", "intrerupt", 8888)]
    infra = {}
    stop, intrerupte = P.depasiri_praguri(durate, ["max poarta_plasa 500"], infra)
    assert stop == [] and infra == {"poarta_plasa": 1} and intrerupte == {"poarta_plasa": 1}


def test_u2_main_tipareste_REIA_si_nu_scrie_in_poarta_verdicte_pe_reluare():
    import poarta_rulare as R
    stare, picate = _replay()
    d = R.decide(dict(stare, oprit=None), _rez(), True, [], "s1", "t1", "", "r" * 40)
    assert d["verdict"] == "REIA_CURAT" and d["linie"] is None and d["ultima"] is None and len(d["stare"]["reluari"]) == 1
    d = R.decide(_stare_proaspata(), _rez(regresie=["frontend_test/e2e/e2e_y.py::test_y"]), True, [], "s1", "t1", "", "r" * 40)
    assert d["verdict"] == "REIA_ROSU" and d["linie"] is None and d["ultima"] == "scrie"
