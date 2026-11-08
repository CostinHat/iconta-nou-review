# -*- coding: utf-8 -*-
"""Lotul 17.5-A (unelte) — pragurile automate din jurnalul de loturi (scripts/praguri_automate.py), fazele timpului de lucru (scripts/jurnal_lot.py: `deriva_lucru`, `lucru`) și raportul de timp
(scripts/raport_timp_lot.py). Jurnale sintetice, fără 8019, fără Chromium, fără baza de test, fără rețea; nimic nu se scrie în jurnalul real sau în ~/ghid_incoming.
Scripturile se încarcă în corpul fiecărui test (nu la import), ca fișierul să poată fi rulat și pe commitul de bază."""
import datetime
import importlib.util
import os
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODULE_PARTAJATE = ("jurnal_lot", "poarta_lib", "praguri_automate", "raport_timp_lot")
BAZA = datetime.datetime(2026, 1, 5, 10, 0, 0).astimezone()
PID_MORT = str(2 ** 22 + 17)   # peste pid_max: `os.kill(pid, 0)` dă ESRCH


def _incarca(nume, rad=RAD):
    """Încarcă scripts/<nume>.py din rădăcina `rad`, cu nume unic; modulele dintre scripturi se reîncarcă din aceeași rădăcină."""
    scripts = os.path.join(rad, "scripts")
    for m in _MODULE_PARTAJATE:
        sys.modules.pop(m, None)
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location("%s_17_5a_%s" % (nume, abs(hash(rad))), os.path.join(scripts, nume + ".py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        sys.path.remove(scripts)


def ora(s):
    return (BAZA + datetime.timedelta(seconds=s)).isoformat(timespec="seconds")


class Jurnal:
    """Constructor de jurnal sintetic (9 câmpuri separate cu tab)."""

    def __init__(self):
        self.linii = []
        self.n = 0

    def rand(self, lot, faza, ev, s, rez="-", id_="x", pid="1", det=""):
        self.linii.append("\t".join([lot, faza, ev, ora(s), "abc123", rez, id_, pid, det]))

    def faza(self, lot, faza, a, b, rez="verde", det="", id_=None, pid="1"):
        self.n += 1
        id_ = id_ or "%s-%s-%d" % (lot, faza, self.n)
        self.rand(lot, faza, "inceput", a, "-", id_, pid, det)
        if b is not None:
            self.rand(lot, faza, "sfarsit", b, rez, id_, pid)
        return id_

    def publicat(self, lot, a, b, rez="publicat"):
        self.faza(lot, "publicare", a, b, rez)

    def scrie(self, cale):
        cale.write_text("\n".join(self.linii) + "\n", encoding="utf-8")
        return str(cale)


def _lot_poarta(j, lot="T", comitari=((60, 100), (200, 240), (300, 340)), porti=(((500, 560, "verde"), (560, 700, "verde"), (700, 900, "verde_cu_restante")),), publicare=1000):
    """Un lot sintetic: pornire la 0, commituri (hook), rulări de poartă (verificator, pytest, plasa) și publicarea."""
    j.faza(lot, "pornire", 0, 0, "ok")
    for a, b in comitari:
        j.faza(lot, "hook", a, b)
    for p in porti:
        for (a, b, rez), faza in zip(p, ("poarta_verificator", "poarta_pytest", "poarta_plasa")):
            j.faza(lot, faza, a, b, rez)
    if publicare is not None:
        j.faza(lot, "publicare", publicare, publicare + 30, "publicat")
    return j


def _derivate(jm, j, lot="T"):
    rows = [ln.split("\t") for ln in j.linii]
    return jm.deriva_lucru(rows, lot)


def _sec(x):
    return round((datetime.datetime.fromisoformat(x["sfarsit"]) - datetime.datetime.fromisoformat(x["inceput"])).total_seconds())


def _per_faza(derivate):
    iesire = {}
    for x in derivate:
        iesire.setdefault(x["faza"], []).append(x)
    return iesire


# ── (1) selecția loturilor ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _jurnal_loturi():
    j = Jurnal()
    # ordinea din fișier ≠ ordinea publicării: D se publică primul, A ultimul
    for lot, pub, hook in (("A", 5000, 10), ("B", 4000, 20), ("C", 3000, 30), ("D", 2000, 40)):
        j.faza(lot, "hook", pub - 500, pub - 500 + hook)
        j.faza(lot, "poarta_verificator", pub - 400, pub - 400 + hook)
        j.publicat(lot, pub, pub + 10)
    j.faza("E", "hook", 6000, 6099)
    j.publicat("E", 6100, 6110, "nepublicat")
    return j


def test_selectia_implicita_ia_ultimele_trei_loturi_publicate_in_ordinea_publicarii_si_ignora_nepublicatul(tmp_path):
    P = _incarca("praguri_automate")
    rows = [ln.split("\t") for ln in _jurnal_loturi().linii]
    assert P.selecteaza(rows) == ["C", "B", "A"]
    assert P.selecteaza(rows[:0]) == []
    assert P.selecteaza(rows, loturi=["E", "D"]) == ["E", "D"]
    j = Jurnal()
    j.faza("A", "hook", 0, 10)
    j.publicat("A", 20, 30)
    assert P.selecteaza([ln.split("\t") for ln in j.linii]) == ["A"]


def test_inainte_de_ia_numai_loturile_publicate_inaintea_primului_rand_al_lotului_dat(tmp_path):
    P = _incarca("praguri_automate")
    j = _jurnal_loturi()
    j.faza("L", "hook", 4500, 4510)   # primul rând al lui L: după publicarea lui D, C și B, înaintea lui A
    rows = [ln.split("\t") for ln in j.linii]
    assert P.selecteaza(rows, inainte_de="L") == ["D", "C", "B"]
    assert P.selecteaza(rows, inainte_de="NECUNOSCUT") == ["C", "B", "A"]   # lot fără rânduri: nu se filtrează nimic


# ── (2) rulările «intrerupt» și cele roșii ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_rularea_intrerupt_nu_intra_in_maxim_dar_se_numara_iar_cea_rosie_completa_intra(tmp_path):
    P = _incarca("praguri_automate")
    j = Jurnal()
    j.faza("A", "hook", 0, 50)
    j.faza("A", "hook", 100, 337, "rosu_1")
    j.faza("A", "hook", 400, 1018, "intrerupt")       # 618 s: mai lungă decât toate cele complete
    j.faza("A", "hook", 2000, None, pid=PID_MORT)       # început fără sfârșit, proces mort: tot «intrerupt»
    j.faza("A", "hook", 3000, None, pid=str(os.getpid()))   # în curs: nici completă, nici întreruptă
    rows = [ln.split("\t") for ln in j.linii]
    c = P.calculeaza(rows, ["A"], ("hook",))["hook"]
    assert (c["maxim"], c["complete"], c["intrerupte"]) == (237, 2, 2)
    assert P.prag(c["maxim"]) == 285


def test_la_egalitate_de_maxim_ramane_lotul_cel_mai_recent(tmp_path):
    P = _incarca("praguri_automate")
    j = Jurnal()
    j.faza("A", "hook", 0, 94)
    j.faza("B", "hook", 100, 194)
    rows = [ln.split("\t") for ln in j.linii]
    assert P.calculeaza(rows, ["A", "B"], ("hook",))["hook"]["lot"] == "B"


# ── (3) rotunjirea în sus ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("maxim,asteptat", [(92, 111), (84, 101), (602, 723), (100, 120), (0, 0)])
def test_pragul_este_maximul_inmultit_cu_unu_virgula_doi_rotunjit_in_sus(maxim, asteptat):
    assert _incarca("praguri_automate").prag(maxim) == asteptat


# ── (4)–(6) fișierul de praguri ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _jurnal_complet(tmp_path):
    j = Jurnal()
    for lot, pub in (("A", 5000), ("B", 4000), ("C", 3000)):
        for f, d in (("hook", 92), ("poarta_verificator", 84), ("poarta_pytest", 602), ("poarta_plasa", 100)):
            j.faza(lot, f, pub - 900, pub - 900 + d)
        j.publicat(lot, pub, pub + 10)
    return j.scrie(tmp_path / "jurnal.log")


def test_faza_fara_nicio_rulare_completa_da_iesire_1_si_nu_scrie_fisierul(tmp_path, capsys):
    P = _incarca("praguri_automate")
    j = Jurnal()
    j.faza("A", "hook", 0, 50)
    j.publicat("A", 100, 110)
    cale = j.scrie(tmp_path / "j.log")
    iesire = tmp_path / "out"
    assert P.main(["N", "unelte", "--jurnal", cale, "--iesire", str(iesire)]) == 1
    assert "lipsesc date pentru poarta_verificator" in capsys.readouterr().out
    assert not iesire.exists() or not list(iesire.iterdir())


def test_fisier_existent_este_refuzat_iar_suprascrie_il_rescrie(tmp_path):
    P = _incarca("praguri_automate")
    cale = _jurnal_complet(tmp_path)
    out = tmp_path / "out"
    a = ["N.1", "produs", "--jurnal", cale, "--iesire", str(out)]
    assert P.main(a) == 0
    fisier = out / "praguri_N_1.txt"
    fisier.write_text("alt continut\n", encoding="utf-8")
    assert P.main(a) == 1
    assert fisier.read_text(encoding="utf-8") == "alt continut\n"
    assert P.main(a + ["--suprascrie"]) == 0
    assert fisier.read_text(encoding="utf-8").startswith("produs\n")


def test_formatul_produs_si_unelte_fara_text_de_completat_iar_adauga_vine_la_sfarsit(tmp_path, capsys):
    P = _incarca("praguri_automate")
    cale = _jurnal_complet(tmp_path)
    adauga = tmp_path / "adauga.txt"
    adauga.write_text("fisiere_permise\n  scripts/x.py\n", encoding="utf-8")
    out = tmp_path / "out"
    assert P.main(["17.6", "produs", "--jurnal", cale, "--iesire", str(out), "--adauga", str(adauga)]) == 0
    produs = (out / "praguri_17_6.txt").read_text(encoding="utf-8").splitlines()
    assert produs[0] == "produs" and produs[1] == "lot: 17.6"
    assert produs[2:6] == ["max hook 111", "max poarta_verificator 101", "max poarta_pytest 723", "max poarta_plasa 120"]
    assert "runde_verificator_max: 2" in produs
    assert produs[-2:] == ["fisiere_permise", "  scripts/x.py"]
    assert any(ln.startswith("sursa pragurilor 17.6:") for ln in produs)
    assert "AVERTISMENT" not in capsys.readouterr().out
    assert P.main(["17.7", "produs", "--jurnal", cale, "--iesire", str(out)]) == 0
    assert "lipsește fisiere_permise" in capsys.readouterr().out
    assert P.main(["17.8", "unelte", "--jurnal", cale, "--iesire", str(out)]) == 0
    unelte = (out / "praguri_17_8.txt").read_text(encoding="utf-8")
    assert unelte.splitlines()[0] == "unelte" and "runde_verificator_max: 0" in unelte
    assert not any(ln.startswith("max ") for ln in unelte.splitlines())
    assert "hook ≤ 111 s (= 92 × 1,2" in unelte
    for t in (unelte, "\n".join(produs)):
        assert "DE COMPLETAT DE ARHITECT" not in t


def test_fisierul_generat_este_citit_de_publica_lot_fara_modificari(tmp_path):
    P = _incarca("praguri_automate")
    cale = _jurnal_complet(tmp_path)
    out = tmp_path / "out"
    adauga = tmp_path / "adauga.txt"
    adauga.write_text("fisiere_permise\n  scripts/x.py\n", encoding="utf-8")
    assert P.main(["17.6", "produs", "--jurnal", cale, "--iesire", str(out), "--adauga", str(adauga)]) == 0
    assert P.main(["17.8", "unelte", "--jurnal", cale, "--iesire", str(out)]) == 0
    PL = _incarca("publica_lot")
    import re
    linii = (out / "praguri_17_6.txt").read_text(encoding="utf-8").splitlines()
    durate_ok = [("hook", "i", "a", "b", "verde", 111), ("poarta_plasa", "i", "a", "b", "verde", 120)]
    assert PL.depasiri_praguri(durate_ok, linii) == ([], {})
    stop, intr = PL.depasiri_praguri([("hook", "i", "a", "b", "verde", 112), ("hook", "j", "a", "b", "intrerupt", 900)], linii)
    assert stop == ["pragul „hook” depășit: 112s > 111s"] and intr == {"hook": 1}
    assert any(re.search(r"runde_verificator_max:\s*(\d+)", ln) and re.search(r"runde_verificator_max:\s*(\d+)", ln).group(1) == "2" for ln in linii)
    assert PL.lista_permisa("\n".join(linii)) == ["scripts/x.py"]
    # un lot «unelte»: prima linie decide, iar `depasiri_praguri` nu găsește niciun rând `max`
    rad = tmp_path / "rad"
    (rad / "scripts").mkdir(parents=True)
    (rad / "scripts" / "praguri_17_8.txt").write_text((out / "praguri_17_8.txt").read_text(encoding="utf-8"), encoding="utf-8")
    assert PL.lot_unelte(str(rad), "17_8") is True
    assert PL.depasiri_praguri([("hook", "i", "a", "b", "verde", 99999)], (out / "praguri_17_8.txt").read_text(encoding="utf-8").splitlines())[0] == []


# ── (8) fazele timpului de lucru ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_lot_cu_o_poarta_verde_are_fazele_si_identitatea_pana_la_publicare():
    jm = _incarca("jurnal_lot")
    j = _lot_poarta(Jurnal())
    d = _per_faza(_derivate(jm, j))
    assert [_sec(x) for x in d["lucru_pana_la_commit"]] == [60]
    assert [_sec(x) for x in d["lucru_pana_la_poarta"]] == [440]
    assert [(_sec(x), x["rezultat"]) for x in d["asteptare_poarta"]] == [(400, "verde")]
    assert [_sec(x) for x in d["pana_la_publicare"]] == [100]
    assert "reparatie_dupa_rosu" not in d and "dupa_verde" not in d
    assert sum(_sec(x) for f in ("lucru_pana_la_commit", "lucru_pana_la_poarta", "asteptare_poarta", "pana_la_publicare") for x in d[f]) == 1000
    # patru intervale între commituri: [0,60] [60,200] [200,300] [300,500]
    assert [(_sec(x)) for x in d["pytest_intre_commituri"]] == [60, 140, 100, 200]


def test_poarta_rosie_apoi_verde_are_o_reparatie_iar_doua_verzi_au_dupa_verde():
    jm = _incarca("jurnal_lot")
    rosu_apoi_verde = (((500, 560, "verde"), (560, 700, "rosu_1"), (700, 900, "verde")), ((1500, 1560, "verde"), (1560, 1700, "verde"), (1700, 1800, "verde")))
    d = _per_faza(_derivate(jm, _lot_poarta(Jurnal(), porti=rosu_apoi_verde, publicare=1900)))
    assert [(_sec(x), x["rezultat"]) for x in d["asteptare_poarta"]] == [(400, "rosu"), (300, "verde")]
    assert [_sec(x) for x in d["reparatie_dupa_rosu"]] == [600]
    assert "dupa_verde" not in d
    assert [_sec(x) for x in d["pana_la_publicare"]] == [100]
    doua_verzi = (((500, 560, "verde"), (560, 700, "verde"), (700, 900, "verde")), ((1500, 1560, "verde"), (1560, 1700, "verde"), (1700, 1800, "verde")))
    d = _per_faza(_derivate(jm, _lot_poarta(Jurnal(), porti=doua_verzi, publicare=1900)))
    assert [_sec(x) for x in d["dupa_verde"]] == [600] and "reparatie_dupa_rosu" not in d


def test_rulare_de_poarta_intrerupta_este_rosie_iar_reluarea_de_infrastructura_ramane_in_aceeasi_rulare():
    jm = _incarca("jurnal_lot")
    intrerupt = (((500, 560, "verde"), (560, 700, "intrerupt"), (700, 900, "verde")),)
    d = _per_faza(_derivate(jm, _lot_poarta(Jurnal(), porti=intrerupt)))
    assert [x["rezultat"] for x in d["asteptare_poarta"]] == ["rosu"]
    # reluare de infrastructură: poarta_pytest «rosu_1» urmat de poarta_pytest «verde», fără poarta_verificator între ele; rândurile de ore egale se judecă în ordinea din fișier
    j = Jurnal()
    j.faza("T", "pornire", 0, 0, "ok")
    j.faza("T", "hook", 60, 100)
    j.faza("T", "poarta_verificator", 500, 560)
    j.faza("T", "poarta_pytest", 560, 700, "rosu_1")
    j.faza("T", "poarta_pytest", 700, 700, "verde")
    j.faza("T", "poarta_plasa", 700, 900)
    d = _per_faza(_derivate(jm, j))
    assert [(_sec(x), x["rezultat"]) for x in d["asteptare_poarta"]] == [(400, "verde")]
    assert "reparatie_dupa_rosu" not in d and "dupa_verde" not in d


def test_commit_dupa_prima_poarta_nu_da_interval_spre_poarta_si_lotul_fara_publicare_nu_are_pana_la_publicare():
    jm = _incarca("jurnal_lot")
    porti = (((500, 560, "verde"), (560, 700, "rosu_1"), (700, 900, "verde")), ((1500, 1560, "verde"), (1560, 1700, "verde"), (1700, 1800, "verde")))
    d = _per_faza(_derivate(jm, _lot_poarta(Jurnal(), comitari=((60, 100), (200, 240), (300, 340), (1000, 1040)), porti=porti, publicare=None)))
    assert "pana_la_publicare" not in d
    assert [_sec(x) for x in d["pytest_intre_commituri"]] == [60, 140, 100, 700]   # nicio ieșire spre poartă; ultimul interval = [c3, c4]
    assert all(x["sfarsit"] != ora(500) for x in d["pytest_intre_commituri"])


def test_identitatea_pe_un_lot_cu_trei_commituri_inaintea_portii_si_cu_ore_egale():
    jm = _incarca("jurnal_lot")
    # commit chiar în secunda începutului de lot și în secunda începutului porții: ore egale, ordinea din fișier
    j = _lot_poarta(Jurnal(), comitari=((0, 40), (100, 140), (200, 240), (500, 520)), porti=(((500, 560, "verde"), (560, 700, "verde"), (700, 900, "verde")),))
    d = _per_faza(_derivate(jm, j))
    total = sum(_sec(x) for f in ("lucru_pana_la_commit", "lucru_pana_la_poarta", "asteptare_poarta", "reparatie_dupa_rosu", "dupa_verde", "pana_la_publicare") for x in d.get(f, []))
    assert total == 1000
    assert [_sec(x) for x in d["lucru_pana_la_commit"]] == [0]


def test_doua_randuri_de_publicare_si_doua_randuri_sfarsit_pe_acelasi_id():
    jm = _incarca("jurnal_lot")
    j = _lot_poarta(Jurnal(), publicare=None)
    j.faza("T", "publicare", 800, 805, "stop")       # înaintea ultimului verdict (900): nu servește
    j.faza("T", "publicare", 1000, 1030, "publicat")
    d = _per_faza(_derivate(jm, j))
    assert [_sec(x) for x in d["pana_la_publicare"]] == [100]
    # un id cu două rânduri «sfarsit» (faza «verificator» din 16.x): rămâne ultimul rând
    j = Jurnal()
    i = j.faza("V", "verificator", 0, 100)
    j.rand("V", "verificator", "sfarsit", 150, "verde", i)
    assert jm.rulari([ln.split("\t") for ln in j.linii], "V")[0]["secunde"] == 150


def test_lucru_scrie_perechi_este_idempotent_si_nu_atinge_randurile_vechi(tmp_path, monkeypatch):
    jm = _incarca("jurnal_lot")
    cale = _lot_poarta(Jurnal()).scrie(tmp_path / "j.log")
    vechi = open(cale, "rb").read()
    n1 = jm.lucru("T", cale)
    nou = open(cale, "rb").read()
    assert n1 > 0 and n1 % 2 == 0 and nou.startswith(vechi)
    assert jm.lucru("T", cale) == 0 and open(cale, "rb").read() == nou
    rows = [ln.split("\t") for ln in nou.decode().splitlines()]
    derivate = [r for r in rows if r[1] in jm.FAZE_LUCRU]
    assert all(len(r) == 9 and r[8].startswith("derivat=1") and r[6].startswith("derivat-T-") for r in derivate)
    assert not any(x["intrerupt"] for x in jm.rulari(rows, "T"))   # perechi: nu sunt marcate «intrerupt»
    monkeypatch.setenv("LOT_JURNAL", cale)
    assert subprocess.run([sys.executable, os.path.join(RAD, "scripts", "jurnal_lot.py"), "lucru", "T"], capture_output=True, text=True).stdout.strip() == "0 rânduri noi"


# ── numărătoarea pytest ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_numaratoarea_pytest_exclude_colectarile_hook_ul_si_poarta_iar_intervalul_hook_e_inchis():
    jm = _incarca("jurnal_lot")
    j = _lot_poarta(Jurnal())
    j.faza("T", "pytest", 10, 20, det="argumente=-q core/x.py")                 # Code, interval [0,60]
    j.faza("T", "pytest", 30, 31, det="argumente=--collect-only -q e2e/x.py")   # colectare
    j.faza("T", "pytest", 60, 65, det="argumente=-q core/test_deficiente.py")   # chiar în secunda începutului hook-ului: în fază
    j.faza("T", "pytest", 100, 105, det="argumente=-q core/test_deficiente.py") # chiar în secunda sfârșitului hook-ului: în fază
    j.faza("T", "pytest", 150, 190, det="argumente=-q core/y.py")               # Code, interval [60,200]
    j.faza("T", "pytest", 560, 690, det="argumente=-q -n 3 core/")              # în poartă
    d = [x for x in _derivate(jm, j) if x["faza"] == "pytest_intre_commituri"]
    assert [x["detalii"] for x in d] == ["rulari=1 colectari=1", "rulari=1 colectari=0", "rulari=0 colectari=0", "rulari=0 colectari=0"]


# ── jurnalul real nu se atinge de uneltele noi ─────────────────────────────────────────────────────────────────────────────────────────────
def test_uneltele_noi_citesc_jurnalul_fara_sa_scrie_in_el(tmp_path):
    P = _incarca("praguri_automate")
    RT = _incarca("raport_timp_lot")
    j = _lot_poarta(Jurnal())
    j.publicat("Z", 2000, 2010)
    j.faza("Z", "hook", 1000, None, pid=PID_MORT)   # început fără sfârșit, proces mort
    cale = j.scrie(tmp_path / "j.log")
    vechi = open(cale, "rb").read()
    P.main(["N", "unelte", "--jurnal", cale, "--iesire", str(tmp_path / "o")])
    RT.main(["Z", "--jurnal", cale, "--arhitect", str(tmp_path / "nu_exista.tsv"), "--iesire", str(tmp_path / "t.md")])
    RT.main(["T", "--jurnal", cale, "--arhitect", str(tmp_path / "nu_exista.tsv"), "--iesire", str(tmp_path / "t2.md")])
    assert open(cale, "rb").read() == vechi


# ── (9) raportul de timp ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _jurnal_raport():
    j = Jurnal()
    j.faza("R", "pornire", 0, 0, "ok")
    j.faza("R", "hook", 600, 780)
    j.faza("R", "pytest", 610, 700, det="argumente=-q core/test_deficiente.py")           # în hook
    j.faza("R", "pytest", 100, 400, det="argumente=-q core/a.py")                          # Code: 300 s
    j.faza("R", "pytest", 300, 500, det="argumente=-q core/b.py")                          # Code: se suprapune cu precedenta -> reuniune 100–500
    j.faza("R", "pytest", 50, 55, det="argumente=--collect-only -q e2e/a.py")              # colectare
    j.faza("R", "pytest", 5000, 7000, "intrerupt", det="argumente=-q core/c.py")           # întreruptă: în «toate sesiunile», nu în tabelul (a)
    j.faza("R", "poarta_verificator", 1200, 1260)
    j.faza("R", "poarta_pytest", 1260, 1860)
    j.faza("R", "pytest", 1300, 1800, det="argumente=-q -n 3 core/")                       # în poartă
    j.faza("R", "poarta_plasa", 1860, 2400)
    j.faza("R", "publicare", 2500, 2530, "publicat")
    return j


def test_raportul_de_timp_imparte_fara_dubla_numaratoare_si_nu_da_minute_rularilor_intrerupt(tmp_path):
    RT = _incarca("raport_timp_lot")
    cale = _jurnal_raport().scrie(tmp_path / "j.log")
    text = RT.raport("R", cale, str(tmp_path / "nu_exista.tsv"))
    assert "- timp total (primul → ultimul rând al lotului): 116.7 min" in text    # 0 -> 7000 (sesiunea întreruptă, constatată la 7000)
    assert "pytest, toate sesiunile: 6 sesiuni, " in text and "din care întrerupte: 1, 33.3 min" in text
    # poartă 1200–2400 = 20,0 min; pytest Code = reuniunea 100–500 (6,7 min) + sesiunea întreruptă 5000–7000 (33,3 min) = 40,0 min; restul = 116,7 − 60,0
    assert "poartă 20.0 min; pytest Code 40.0 min; restul 56.7 min" in text
    assert "colectări 1; pornite în hook 1; pornite în poartă 1; ale lui Code 3" in text
    linie = [ln for ln in text.splitlines() if ln.startswith("| pytest |")][0]
    assert linie.split("|")[2].strip() == "5" and linie.split("|")[3].strip() == "1"   # 5 complete, 1 întreruptă
    assert "fără jurnal arhitect" in text


def test_jurnalul_arhitectului_cu_comentarii_lipsa_si_rand_stricat(tmp_path):
    RT = _incarca("raport_timp_lot")
    cale = _jurnal_raport().scrie(tmp_path / "j.log")
    a = tmp_path / "arhitect.tsv"
    a.write_text("# comentariu\n\nR\tcoada_scrisa\t%s\tcomanda\nR\tverdict_extern\t%s\tx\nR\tverdict_extern\t%s\ty\nALT\traport_code\t%s\t\n" % (ora(-900), ora(100), ora(900), ora(-3000)), encoding="utf-8")
    t = RT.raport("R", cale, str(a))
    assert "runde externe: 2" in t and "pauză de la precedentul: 16.7 min" in t   # (100 − (−900)) = 1000 s
    assert "pregătire: lipsă" in t   # nu există lot publicat înaintea lui R cu raport_code
    a.write_text("R\tcoada_scrisa\tnu-e-o-ora\tx\n", encoding="utf-8")
    assert "fără jurnal arhitect" in RT.raport("R", cale, str(a))
    assert "fără jurnal arhitect" in RT.raport("R", cale, str(tmp_path / "lipseste.tsv"))


def test_pregatirea_este_coada_scrisa_minus_raportul_lotului_publicat_inaintea_lui(tmp_path):
    RT = _incarca("raport_timp_lot")
    j = Jurnal()
    j.faza("P", "hook", 0, 10)
    j.publicat("P", 100, 110)
    j.faza("R", "hook", 1000, 1010)
    cale = j.scrie(tmp_path / "j.log")
    a = tmp_path / "a.tsv"
    a.write_text("P\traport_code\t%s\t\nR\tcoada_scrisa\t%s\t\n" % (ora(200), ora(800)), encoding="utf-8")
    t = RT.raport("R", cale, str(a))
    assert "pregătire: 10.0 min (coada_scrisa R − raport_code" in t and "al lotului P)" in t


# ── (10) invarianța cititorilor pe copia jurnalului real ───────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not os.environ.get("JURNAL_COPIE"), reason="JURNAL_COPIE (copia jurnalului real) lipsește")
def test_rezumat_pe_copia_jurnalului_real_este_identic_cu_cel_al_commitului_de_baza(tmp_path):
    copie = os.environ["JURNAL_COPIE"]
    baza = subprocess.run(["git", "merge-base", "HEAD", "main"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    vechi = tmp_path / "vechi" / "scripts"
    vechi.mkdir(parents=True)
    for f in ("jurnal_lot.py", "poarta_lib.py"):
        (vechi / f).write_text(subprocess.run(["git", "show", "%s:scripts/%s" % (baza, f)], cwd=RAD, capture_output=True, text=True, check=True).stdout, encoding="utf-8")
    ies = {}
    for nume, script in (("vechi", str(vechi / "jurnal_lot.py")), ("nou", os.path.join(RAD, "scripts", "jurnal_lot.py"))):
        j = tmp_path / ("%s.log" % nume)
        j.write_bytes(open(copie, "rb").read())
        r = subprocess.run([sys.executable, script, "rezumat", "17.2-B"], capture_output=True, text=True, env=dict(os.environ, LOT_JURNAL=str(j)), cwd=RAD)
        assert r.returncode == 0 and r.stdout
        ies[nume] = r.stdout
    assert ies["vechi"] == ies["nou"]


# ── (11) publica_lot: raportul de timp căzut nu oprește publicarea ─────────────────────────────────────────────────────────────────────────
def test_lucru_si_timp_nu_ridica_exceptie_cand_jurnalul_lipseste_sau_derivarea_cade(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("LOT_JURNAL", str(tmp_path / "nu_exista" / "j.log"))
    monkeypatch.setenv("HOME", str(tmp_path))
    PL = _incarca("publica_lot")
    mesaje = PL.lucru_si_timp("LOT_FARA_JURNAL")
    assert isinstance(mesaje, list) and mesaje
    # derivarea cade: eroarea se tipărește, iar raportul de timp se încearcă oricum
    def cade(*a, **k):
        raise RuntimeError("derivare căzută")
    monkeypatch.setattr(PL.JL, "lucru", cade)
    mesaje = PL.lucru_si_timp("LOT_FARA_JURNAL")
    assert any(m.startswith("EROARE lucru") and "derivare căzută" in m for m in mesaje)
    assert "EROARE lucru" in capsys.readouterr().out
