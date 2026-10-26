# -*- coding: utf-8 -*-
"""GARD (07.09.2026) — poarta scurta din PLAN_LUCRU regula 4 nu poate deveni o formalitate.

CE PAZESTE, si de ce fiecare proba e aici:

  CELE DOUA CAZURI DE ACCEPTANTA, cerute de Costin cand a comandat instrumentul: o atingere doar in
  `core/plati.py` NU trebuie sa atinga testele D406; una in `core/d112.py` trebuie sa atinga testele
  D112. Le-am probat o data, la constructie. Pinate aici, proba se REFACE la fiecare poarta — altfel
  ar fi ramas o amintire dintr-o dupa-amiaza.

  REFUZUL PE ARGUMENTE. `perimetru.py` accepta cai in argv, fiindca asa se PROBEAZA derivarea.
  Lansatorul nu are voie: ar insemna ca cel care tocmai a scris modificarea alege ce se ruleaza —
  exact ce interzice regula 5 („o exceptie luata o data face regula o formalitate").

  REFUZUL PE NESIGURANTA. Un `.md` atins, sau `main.py`, si derivarea nu mai poate inchide
  perimetrul. Atunci raspunsul e SUITA INTREAGA (15.10.2026; pana atunci poarta completa), nu un
  perimetru mai mic. *Un perimetru ghicit e mai rau decat o rulare lunga.*

  ANTI-VACUU. Daca `perimetru()` ar intoarce liste goale din orice motiv, toate probele de mai sus
  ar trece degeaba. De-aia se cere si ca perimetrul unui modul cunoscut sa NU fie gol.

  [23.10.2026, CLAUDE.md §5 — poarta compusa] BAZA DIFF-ULUI: `--fata-de=<X>` / `--compus=<X>` numesc un COMMIT, nu fisiere; lista
  atinselor vine tot din `git diff` (fata de X). Si CITIREA CAZUTELOR din rezumatul pytest: nodurile (inclusiv parametri cu „ - ”) si
  completitudinea (o lista trunchiata nu se poate compune). Compusul insusi: `core/test_poarta_lot.py`.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))

import perimetru as P            # noqa: E402
import poarta_scurta as PS       # noqa: E402


# ── cele doua cazuri de acceptanta ─────────────────────────────────────────
def test_o_atingere_in_plati_nu_atinge_testele_d406():
    """Cazul R43, verbatim din comanda. `plati.py` n-are nicio legatura cu SAF-T."""
    teste, incerte = P.perimetru(["core/plati.py"])
    assert incerte == []
    assert teste, "perimetru gol — anti-vacuu"
    # [17.10.2026] gărzile de arbore (`P.garzi_de_arbore`) intră la ORICE `.py` atins, deliberat — nu sunt legătura plăți -> D406
    d406 = [t for t in teste if t.lower().count("d406") and t not in P.garzi_de_arbore()]
    assert d406 == [], "perimetrul lui plati.py a ajuns la D406: %s" % d406
    assert set(teste) >= {"core/test_plata_izolare.py"}


def test_o_atingere_in_d112_atinge_testele_d112():
    """Celalalt caz din comanda. Aici legatura EXISTA, deci trebuie sa se vada."""
    teste, incerte = P.perimetru(["core/d112.py"])
    assert incerte == []
    assert set(teste) >= {"core/test_d112.py"}, "perimetrul lui d112.py nu contine testele lui"


def test_cele_doua_cazuri_chiar_difera():
    """CALIBRARE: daca derivarea ar intoarce acelasi lucru pentru orice intrare, cele doua probe de
    mai sus ar trece si cu un instrument mort. Se cere ca raspunsurile sa fie DIFERITE."""
    a, _ = P.perimetru(["core/plati.py"])
    b, _ = P.perimetru(["core/d112.py"])
    assert set(a) != set(b)
    assert len(b) > len(a)


# ── refuzurile ─────────────────────────────────────────────────────────────
def test_lansatorul_refuza_fisiere_pe_linia_de_comanda(capsys):
    """Perimetrul se DERIVA, nu se alege. Un lansator care accepta cai e un lansator care poate fi
    convins sa ruleze mai putin."""
    cod = PS.main(["core/plati.py"])
    assert cod == 3
    # structura iesirii, nu un sir: prima linie e refuzul, si numeste fisierul dat
    prima = capsys.readouterr().out.splitlines()[0]
    assert prima.startswith("REFUZ") and prima.rstrip().endswith("comanda.")


@pytest.mark.parametrize("atins,de_ce", [
    ("CONFORMITATE.md", "registru"),
    ("main.py", "rutele sunt citite de scanere care nu importa main"),
    ("static/js/ecrane/facturi_ecran.js", "fisier ne-Python"),
])
def test_derivarea_refuza_ce_nu_poate_vedea(atins, de_ce):
    """Cele trei clase pe care graful de import NU le vede. Fiecare, atinsa alaturi de cod, cere
    poarta completa."""
    _teste, incerte = P.perimetru([atins, "core/plati.py"])
    assert incerte, "derivarea a inchis perimetrul desi s-a atins %s" % atins


class _R:
    returncode = 0
    stdout = "TOTAL: 0 candidate\n"


def _lanseaza(monkeypatch, atinse, rc=0):
    monkeypatch.setattr(PS.P, "atinse_din_git", lambda: list(atinse))
    monkeypatch.setattr(PS.P, "netracked", lambda: [])
    rulate = []
    real = PS.subprocess.run

    def _run(cmd, cwd=None, **k):
        if cmd[0] == "git":                 # derivarea citește depozitul (git ls-files) — rămâne reală
            return real(cmd, cwd=cwd, **k)
        rulate.append(cmd)
        r = _R()
        r.returncode = rc
        return r
    monkeypatch.setattr(PS.subprocess, "run", _run)
    return PS.main([]), rulate


def test_lansatorul_ruleaza_toata_suita_cand_derivarea_python_nu_e_sigura(monkeypatch, capsys):
    """[15.10.2026] Nesiguranța din PYTHON (aici `main.py`, citit de scanere care nu-l importă) -> suita întreagă, fără selecție, pe
    procesele porții, cu exit-ul ei. MUTAȚIE: `return 2` în loc de `_ruleaza_tot` -> pică; o cale / `-k` în `SUITA_INTREAGA` -> pică."""
    cod, rulate = _lanseaza(monkeypatch, ["main.py", "core/plati.py"], rc=5)
    assert (cod, rulate) == (5, [PS.SUITA_INTREAGA])
    assert PS.SUITA_INTREAGA[1:] == ["-m", "pytest", "-q", "-n", "3", "--dist", "loadfile"], PS.SUITA_INTREAGA
    # se cere ca MOTIVELE sa fie tiparite, numarate ca randuri, nu cautate ca sir
    motive = [x for x in capsys.readouterr().out.splitlines() if x.startswith("   - ")]
    assert len(motive) == 1


def test_js_atins_nu_porneste_suita_ci_verificatorul_e2e_si_garzile_statice(monkeypatch):
    """[15.10.2026 seara, decizia Costin: „Când o comandă atinge JS/CSS, rularea țintită nu devine suita întreagă: rulezi e2e-ul
    ecranelor atinse, uneltele vizuale și verificatorul”] `login.js` atins: nicio suită întreagă; gărzile statice (printre ele
    `?v=`), verificatorul și e2e-ul ecranelor lui — derivat din id-urile DOM: înregistrarea liberă și invitațiile.
    MUTAȚIE: `imparte` lasă JS-ul în „python” -> perimetrul îl vede incert -> suita întreagă -> pică."""
    cod, rulate = _lanseaza(monkeypatch, ["static/js/ecrane/login.js"])
    assert cod == 0 and PS.SUITA_INTREAGA not in rulate, rulate
    (pytest_rulat,) = [c for c in rulate if c[1:3] == ["-m", "pytest"]]
    assert pytest_rulat.count("core/test_versionare_assets.py") == 1
    assert [c for c in rulate if c[1:] == ["verificator_conformitate.py"]]
    e2e = sorted(c[-1] for c in rulate if c[1:3] == ["scripts/e2e_poarta.py", "--arbore"])
    # [lotul 5, 15.10.2026] + e2e_lot5_c3.py: testul 267 (ciorna formularului de înregistrare) folosește id-urile formularului
    # [lotul 6, 16.10.2026] + e2e_lot6.py: testul 290 (eroarea dispare după corectare) folosește formularul de autentificare
    #   (`#login-email`, `#login-eroare`)
    # [lotul 11, 11.2 pct.4] + e2e_pozitii_validate.py: F008 (autentificarea) folosește formularul de intrare; + e2e_lot11_w2.py (440 / 445)
    # [lotul 12, 561] + e2e_lot12_start.py: clientul intră în portal prin formularul de autentificare (`#login-parola`, `#login-buton`)
    # [lotul 12, 642] + e2e_lot12_form2.py: formularul de înregistrare din invitație (`#reg-cui`, `#reg-buton`, `#reg-eroare`)
    # [lotul 12, C179] + e2e_lot12_cx7.py: datele ANAF ale CUI-ului pe formularul de înregistrare din invitație (`#reg-cui`,
    #   `#reg-cui-verifica`, `#reg-cui-info`)
    # [lotul 13, 560] + e2e_lot13_portal_p1.py: clientul invitat intră în portal din linkul emailului; testul așteaptă formularul de
    #   autentificare (`#login-email`) ca să dovedească că linkul l-a dus în cont, nu la formular
    # [lotul 13, 644 / 645] + e2e_lot13_admin.py: cabinetul suspendat nu intră cu parola, iar refuzul se citește pe formularul de
    #   autentificare (`#login-email`, `#login-parola`, `#login-buton`, `#login-eroare`)
    assert e2e == ["--doar=e2e_inregistrare_libera.py", "--doar=e2e_invitatii.py", "--doar=e2e_lot11_w2.py", "--doar=e2e_lot12_cx7.py",
                   "--doar=e2e_lot12_form2.py", "--doar=e2e_lot12_start.py", "--doar=e2e_lot13_admin.py", "--doar=e2e_lot13_portal_p1.py",
                   "--doar=e2e_lot5_c3.py", "--doar=e2e_lot6.py", "--doar=e2e_pozitii_validate.py"], e2e


def test_registrul_langa_python_nu_porneste_suita(monkeypatch):
    """Un registru atins alături de cod: gărzile de registru + perimetrul codului, nu suita întreagă (nesiguranța registrului nu e a
    Python-ului). MUTAȚIE: registrele lăsate în „python” -> incert -> suita -> pică."""
    cod, rulate = _lanseaza(monkeypatch, ["CONFORMITATE.md", "core/plati.py"])
    assert cod == 0 and PS.SUITA_INTREAGA not in rulate, rulate
    (pytest_rulat,) = rulate
    assert {"core/test_plata_izolare.py", "core/test_conformitate.py"} <= set(pytest_rulat), pytest_rulat


def test_commiturile_reale_de_azi_ar_fi_cerut_poarta_completa():
    """MASURAT, nu presupus: pe amandoua reparatiile de 06.09 perimetrul NU se poate inchide,
    fiindca amandoua au atins registre si `main.py`. Poarta scurta e pentru bucla DIN TURA, nu
    pentru commit — iar cifra asta tine afirmatia adevarata."""
    r43 = ["CONFORMITATE.md", "DECIZII.md", "core/plati.py", "main.py",
           "static/js/ecrane/facturi_ecran.js"]
    r94 = ["CONFORMITATE.md", "core/control_fiscal_api.py", "core/declaratii_api.py", "main.py"]
    for nume, lista in (("R43", r43), ("R94", r94)):
        _t, incerte = P.perimetru(lista)
        assert incerte, "%s: derivarea a inchis perimetrul, desi a atins registre si main.py" % nume


def test_perimetrul_nu_e_toata_suita():
    """Un perimetru care ia aproape tot nu deriva nimic, imbraca «ruleaza tot» in alt nume
    (PLAN_LUCRU, regula 5, prima forma esuata). Se cere sa ramana sub jumatate din fisierele de
    test, pe cazul cel mai larg dintre cele doua de acceptanta.

    [C5, 20.09.2026, decizia lui Costin] Proba a fost `core/d112.py` pana azi — o ALEGERE PROASTA:
    d112 e transitiv central prin `tenant_provisioning` (`tenant_provisioning -> firma_rezumat ->
    vector_fiscal_api -> firma_profil_api --import LOCAL--> d112`, iar unealta numara si importurile
    locale ca muchii). Deci „perimetrul lui d112" ≈ „toate testele DB" si creste cu 1 la fiecare test
    DB nou -> se apropia de ½ prin simpla crestere a suitei (a atins-o exact la 278/556 cand s-a
    adaugat un test de reconciliere bancara, fara nicio legatura cu d112). Proba noua = `capacitate_api`,
    VERIFICAT ca fiind efectiv periferic: NU e in inchiderea de import a lui `tenant_provisioning`, deci
    perimetrul lui NU creste cu testele DB; ramane la ~47/556 (marja mare, stabila). Vezi DECIZII (57)."""
    toate = [f for f in os.listdir(os.path.join(_RAD, "core"))
             if f.startswith("test_") and f.endswith(".py")]
    teste, _ = P.perimetru(["core/capacitate_api.py"])
    assert teste, "perimetrul probei e GOL — anti-vacuu: proba nu mai e importata de niciun test"
    assert len(teste) < len(toate) / 2, "%d din %d fisiere — prea larg ca sa fie o derivare" % (
        len(teste), len(toate))


def test_e2e_atins_direct_ruleaza_el_si_cine_il_importa(monkeypatch):
    """[lotul 5, comanda 3] Plasa atinsă direct rulează: un fișier e2e schimbat sau nou rulează el însuși (înainte, `e2e_lot5_id.py`,
    nou, n-a rulat: e2e-ul se alegea numai după id-urile DOM ale JS-ului atins), plus fișierele care îi importă ajutoarele; conftest-ul
    plasei atins -> plasa întreagă. MUTAȚIE: `e2e = {}` în loc de `e2e_din_plasa(atinse)` -> pică."""
    import glob

    def e2e_rulat(atinse):
        _cod, rulate = _lanseaza(monkeypatch, atinse)
        return sorted(c[-1][len("--doar="):] for c in rulate if c[1:3] == ["scripts/e2e_poarta.py", "--arbore"])
    assert e2e_rulat(["frontend_test/e2e/e2e_magazin.py"]) == ["e2e_magazin.py"]
    bloc_d = e2e_rulat(["frontend_test/e2e/e2e_bloc_d.py"])
    assert {"e2e_bloc_d.py", "e2e_lot5_c3.py", "e2e_lot5_id.py"} <= set(bloc_d) and "e2e_magazin.py" not in bloc_d, bloc_d
    toate = sorted(os.path.basename(e) for e in glob.glob(os.path.join(PS.RAD, "frontend_test", "e2e", "e2e_*.py")))
    assert e2e_rulat(["frontend_test/e2e/conftest.py"]) == toate


def test_populatia_din_name_status():
    """`git diff --name-status HEAD` -> căile `.py` adăugate / șterse / redenumite (la R, amândouă); `M` și ne-Python nu intră."""
    iesire = "A\tcore/migrare_noua.py\nM\tcore/plati.py\nD\tcore/vechi.py\nR087\tscripts/a.py\tscripts/b.py\nA\tDECIZII_X.md\n"
    assert P.populatie_din(iesire) == {"core/migrare_noua.py", "core/vechi.py", "scripts/a.py", "scripts/b.py"}


@pytest.mark.parametrize("nivel", ["direct", "subsistem", "integrare"])
def test_un_py_nou_e_incert_la_toate_nivelurile(monkeypatch, nivel):
    """[16.10.2026, poarta lotului 5] `core/migrare_nume_conturi_vechi.py`, nou, a dus `test_e2a_univers` peste plafon, iar rularea
    țintită nu l-a ales: graful de import nu vede cine ENUMERĂ directorul. Un `.py` nou / șters -> incert, la orice nivel.
    MUTAȚIE: `if a in sarite: continue` fără motivul din `_incerte_populatie` (lista goală) -> pică."""
    monkeypatch.setattr(P, "populatie_schimbata", lambda: {"core/migrare_noua.py"})
    _teste, incerte = P.nivel(nivel, ["core/migrare_noua.py"])
    assert [m for m in incerte if m.startswith("core/migrare_noua.py — ") and P.MOTIV_POPULATIE in m], incerte
    monkeypatch.setattr(P, "populatie_schimbata", lambda: set())
    teste, incerte = P.nivel(nivel, ["core/plati.py"])
    assert (incerte, bool(teste)) == ([], True), "un .py doar modificat rămâne derivabil"


def test_lansatorul_ruleaza_suita_cand_s_a_adaugat_un_py(monkeypatch):
    """Același caz, prin lansator: suita întreagă, cu exit-ul ei. Dacă git nu răspunde la `--name-status`, tot suita (fail-closed)."""
    monkeypatch.setattr(PS.P, "populatie_schimbata", lambda: {"core/migrare_noua.py"})
    cod, rulate = _lanseaza(monkeypatch, ["core/migrare_noua.py"], rc=4)
    assert (cod, rulate) == (4, [PS.SUITA_INTREAGA])
    monkeypatch.setattr(PS.P, "populatie_schimbata", lambda: None)
    cod, rulate = _lanseaza(monkeypatch, ["core/plati.py"], rc=6)
    assert (cod, rulate) == (6, [PS.SUITA_INTREAGA])



# ── [23.10.2026] baza diff-ului si citirea cazutelor ─────────────────────────────────────────────────────────
from core.test_poarta_lot import depozit_poarta  # noqa: E402,F401 — fixtura depozitului cu poarta adevărată


def test_fata_de_un_commit_ia_atinsele_din_diff_fata_de_el(depozit_poarta):
    """Arbore curat pe HEAD: fără bază, „niciunul”; `--fata-de=<X>` vede ce s-a comis de la X (`core/a.py`) și rulează perimetrul lui
    (`core/test_a.py`); un commit inexistent e refuzat (3), iar un fișier tot nu e primit. MUTAȚIE: `P.BAZA = …` scos din `main` ->
    „niciunul” și cu `--fata-de` -> pică."""
    dp = depozit_poarta
    x = dp.git("rev-parse", "HEAD")
    dp.comite("core/a.py", "X = 2\n")

    def ruleaza(*a):
        r = __import__("subprocess").run([str(dp.d / "venv" / "bin" / "python"), "scripts/poarta_scurta.py"] + list(a), cwd=dp.d,
                                         capture_output=True, text=True, timeout=120, env=dp._env({}))
        return r.returncode, r.stdout + r.stderr
    cod, iesire = ruleaza()
    assert (cod, iesire.count("ATINSE: niciunul")) == (0, 1), iesire
    cod, iesire = ruleaza("--fata-de=" + x)
    assert cod == 0 and iesire.count("ATINSE (1):") == 1 and iesire.count("    core/a.py") == 1, iesire
    assert [c for c in dp.chemari() if c.startswith("-m pytest")] == ["-m pytest -q --no-header core/test_a.py"], dp.chemari()
    assert ruleaza("--fata-de=nu-exista")[0] == 3 and ruleaza("--compus=nu-exista")[0] == 3
    assert ruleaza("--fata-de=" + x, "core/a.py")[0] == 3


def test_cazutele_se_citesc_pe_noduri_din_rezumatul_pytest(tmp_path):
    """`FAILED` / `ERROR` din rezumatul scurt -> noduri (fără dubluri; parametrul cu „ - ” rămâne întreg; un rând de log `ERROR    …`
    nu e nod). Lista e completă numai dacă are atâtea rânduri câte căzute numără rezumatul. MUTAȚIE: `numar_cazute(text) == randuri`
    înlocuit cu `True` -> lista trunchiată trece drept completă -> pică."""
    text = ("ERROR    core.db:db.py:12 conexiune\n"
            "FAILED core/test_a.py::test_x[a - b] - AssertionError: 1 - 2\n"
            "FAILED core/test_a.py::test_y - assert 0\n"
            "ERROR core/test_a.py::test_y - teardown\n"
            "ERROR core/test_b.py\n"
            "3 failed, 120 passed, 2 errors in 3.21s\n")
    assert PS.cazute_din_text(text) == (["core/test_a.py::test_x[a - b]", "core/test_a.py::test_y", "core/test_b.py"], 4)
    log = tmp_path / "p.log"
    log.write_text(text.replace("3 failed", "2 failed"))
    p = PS.parte(1, 7, [str(tmp_path / "lipsa.log"), str(log)])
    assert (p["rc"], p["durata_s"], p["cazute_complete"], len(p["cazute"])) == (1, 7, True, 3), p
    log.write_text(text)                                            # rezumatul numără 5, lista are 4 rânduri: trunchiată
    assert PS.parte(1, 7, [str(log)])["cazute_complete"] is False
    log.write_text("[e2e] aplicatia n-a pornit\n")                 # căzută fără rezumat
    assert PS.parte(3, 1, [str(log)])["cazute_complete"] is False
    assert PS.parte(0, 1, [str(tmp_path / "lipsa.log")])["cazute_complete"] is True
