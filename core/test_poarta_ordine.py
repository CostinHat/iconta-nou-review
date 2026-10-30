# -*- coding: utf-8 -*-
"""GARDA ordinii hook-urilor și a locului porții.

ISTORIC. 08.10.2026 (decizia Costin pct.3: „Verificarea commit-msg rulează înaintea pytest, nu după.”): git rulează `pre-commit`
ÎNAINTEA mesajului, deci suita s-a mutat în `commit-msg`, după `verifica-mesaj`. 15.10.2026 (comanda Costin, verbatim în DECIZII
„Poarta o dată pe lot”: „Poarta completă: o singură dată pe lot, la închiderea lotului, înainte de publicarea pe producție. [...] Muți
poarta din hook-ul commit-msg pe mutarea lui main [...]”): suita a ieșit din commit cu totul.

    pre-commit: ruff  ->  commit-msg: verifica-mesaj (atât)
    închiderea lotului: scripts/poarta_lot.sh -> poarta-suita (prospețime, pytest, verificator, cifre, plasa) -> verdictul
    mutarea lui main: reference-transaction cere `VERDE <sha>` (core/test_garda_main.py)

23.10.2026 (CLAUDE.md §5: „Dacă poarta pică: se repară cauza, apoi se rulează testele căzute și tot ce depinde de reparație.” și
„Durata fiecărei părți a porții se măsoară și se raportează.”; DECIZII 23.10.2026 „Comanda 12.1”): poarta nu se mai oprește la prima
parte roșie — rulează toate părțile, în aceeași ordine, și scrie înregistrarea rulării (`<git-common-dir>/poarta_rulari/<sha>.json`).

CE FACE IMPOSIBIL:
  * ca un commit să pornească suita (structural: nici `pre-commit`, nici `commit-msg` nu cheamă pytest / `poarta-suita`; funcțional,
    pe hook-ul adevărat: un mesaj bun trece fără „[poarta] pytest”);
  * o a doua pornire a porții complete: în tot depozitul, `poarta-suita` e chemată NUMAI de `scripts/poarta_lot.sh`;
  * ca poarta să judece altceva decât commitul (arborele ≠ indexul -> respins înainte de pytest);
  * ca o parte roșie să ascundă căzutele celorlalte (funcțional, pe `poarta-suita` adevărată, cu uneltele imitate: oricare parte roșie,
    toate cinci rulează, iar JSON-ul are rc, durata și căzutele fiecăreia).
"""
import json
import os
import shlex
import subprocess
import tempfile
import time

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HOOKS = os.path.join(_RAD, "scripts", "githooks")


def _linii_cod(nume):
    """Liniile de cod ale unui script `sh` (fără comentarii), ca liste de cuvinte."""
    out = []
    with open(os.path.join(_HOOKS, nume), encoding="utf-8") as f:
        for linie in f:
            try:
                t = shlex.split(linie, comments=True)
            except ValueError:
                continue
            if t:
                out.append(t)
    return out


def test_pre_commit_nu_mai_porneste_suita():
    """Suita e după mesaj; în `pre-commit` mesajul nu există. MUTAȚIE: linia `"$PY" -m pytest -q` pusă înapoi în `pre-commit`
    -> pică."""
    cuvinte = [w for t in _linii_cod("pre-commit") for w in t]
    assert cuvinte.count("pytest") == 0 and sum(w.count("verificator_conformitate") for w in cuvinte) == 0, cuvinte
    assert sum(w.count("RUFF") for w in cuvinte) >= 1, "ruff a dispărut din pre-commit"


def test_commit_msg_verifica_numai_mesajul():
    """[15.10.2026] `commit-msg` cheamă `verifica-mesaj` (cu `|| exit 1`) și NIMIC din poartă. MUTAȚIE: linia `poarta-suita` pusă
    înapoi în `commit-msg` -> pică."""
    linii = _linii_cod("commit-msg")
    mesaj = [t for t in linii if any(w.endswith("/verifica-mesaj") for w in t)]
    assert len(mesaj) == 1 and mesaj[0][-3:] == ["||", "exit", "1"], linii
    cuvinte = [w for t in linii for w in t]
    assert [w for w in cuvinte if w.endswith("/poarta-suita") or w == "pytest" or w.startswith("verificator_conformitate")] == [], cuvinte
    suita = [w for t in _linii_cod("poarta-suita") for w in t]
    assert suita.count("pytest") >= 1 and suita.count("verificator_conformitate.py") >= 1


def _chemari_poarta_suita():
    """Fișierele urmărite (în afara testelor) care CHEAMĂ `poarta-suita`: în scripturile `sh` (`.sh`, hook-urile fără extensie), o linie
    de cod (nu comentariu, nu `echo`) care o numește; în `.py`, un literal-șir care e calea ei (`"…/poarta-suita"`) — o pomenire în
    docstring nu e o chemare."""
    import re as _re
    fis = subprocess.run(["git", "ls-files"], cwd=_RAD, capture_output=True, text=True).stdout.split()
    gasite = []
    for f in fis:
        if f.startswith("core/test_") or f == "scripts/githooks/poarta-suita":
            continue
        sh = f.endswith(".sh") or (f.startswith("scripts/githooks/") and "." not in os.path.basename(f))
        if not (sh or f.endswith(".py")) or not os.path.isfile(os.path.join(_RAD, f)):
            continue
        for linie in open(os.path.join(_RAD, f), encoding="utf-8", errors="replace"):
            if sh:
                cod = linie.split("#", 1)[0]
                gasit = bool(_re.search(r"poarta-suita", cod)) and not _re.match(r"\s*echo\b", cod)
            else:
                gasit = bool(_re.search(r"""["'](?:[^"'\s]*/)?poarta-suita["']""", linie))
            if gasit:
                gasite.append(f)
                break
    return sorted(set(gasite))


def test_poarta_completa_pornita_numai_de_inchiderea_lotului():
    """[15.10.2026] „Poarta completă: o singură dată pe lot, la închiderea lotului”: în tot depozitul, numai `scripts/poarta_lot.sh`
    cheamă `poarta-suita`. MUTAȚIE: `sh "$DIR/poarta-suita"` pus înapoi în `commit-msg` (sau într-un script nou) -> pică."""
    assert _chemari_poarta_suita() == ["scripts/poarta_lot.sh"]


def _ruleaza(continut, pregatire=None, hook="commit-msg"):
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "init", "-q", "."], cwd=d, check=True, capture_output=True)
        msg = os.path.join(d, ".git", "COMMIT_EDITMSG")       # unde îl pune git (nu în arborele de lucru)
        with open(msg, "wb") as f:
            f.write(continut)
        for nume, cont in (pregatire or {}).items():
            with open(os.path.join(d, nume), "w") as f:
                f.write(cont)
        t0 = time.monotonic()
        r = subprocess.run(["sh", os.path.join(_HOOKS, hook)] + ([msg] if hook == "commit-msg" else []), cwd=d, capture_output=True, text=True,
                           timeout=300)
        return r.returncode, (r.stdout or "") + (r.stderr or ""), time.monotonic() - t0


def test_mesajul_respins_nu_porneste_suita():
    """Ordinea, ca efect, pe hook-ul adevărat: un mesaj cu octet de control e respins de `verifica-mesaj`, iar suita nici nu
    pornește. MUTAȚIE: ordinea inversată în `commit-msg` -> apare „[poarta] pytest” -> pică."""
    cod, iesire, _dur = _ruleaza(b"mesaj\n\ncu octet \x08 in el\n")
    assert cod == 1 and iesire.count("OCTETI DE CONTROL") >= 1, iesire
    assert iesire.count("[poarta] pytest") == 0, "suita a pornit înaintea verificării mesajului:\n%s" % iesire


def test_mesajul_bun_trece_fara_suita():
    """[15.10.2026] Un commit nu mai pornește poarta: un mesaj bun trece de `commit-msg` în secunde, fără „[poarta] pytest”. MUTAȚIE:
    `poarta-suita` pusă înapoi în `commit-msg` -> apare „[poarta] pytest” (și respinge, pe depozitul gol) -> pică."""
    cod, iesire, _dur = _ruleaza("Reparație mică, cu diacritice: șțăîâ\n".encode("utf-8"))
    assert (cod, iesire.count("[poarta] pytest")) == (0, 0), iesire


def test_poarta_suita_pe_depozit_fara_teste_respinge():
    """Suita n-a dispărut din `poarta-suita`: chemată direct (cum o cheamă `poarta_lot.sh`), pornește pytest, care pe depozitul gol
    n-are teste și respinge. MUTAȚIE: linia pytest scoasă din `poarta-suita` -> pică."""
    cod, iesire, _dur = _ruleaza(b"x\n", hook="poarta-suita")
    assert iesire.count("[poarta] pytest") == 1, iesire
    assert cod == 1, "pe un depozit fără teste poarta trebuia să respingă:\n%s" % iesire


def test_arborele_diferit_de_index_e_respins_inainte_de_suita():
    """[15.10.2026] Verdictul porții privește COMMITUL: un fișier nou neadăugat (sau modificat și nepus) e respins înainte de pytest —
    altfel pytest ar judeca arborele de lucru, iar commitul ar înregistra indexul (`fdb20bd6`: poartă verde, exportul pica 9 gărzi).
    MUTAȚIE: verificarea `arbore_nepus` scoasă din `poarta-suita` -> suita pornește -> pică."""
    cod, iesire, _dur = _ruleaza("Reparație mică\n".encode("utf-8"), pregatire={"nepus.py": "x = 1\n"}, hook="poarta-suita")
    assert cod == 1 and iesire.count("[poarta] pytest") == 0, iesire
    assert iesire.count("    nepus.py") == 1, iesire


def test_hookurile_rulate_din_teste_nu_scriu_in_jurnalele_portii_reale():
    """[15.10.2026] Poarta lotului 2: `test_mesajul_bun_ajunge_la_suita` (azi `test_poarta_suita_pe_depozit_fara_teste_respinge`) a pornit `poarta-suita` pe un depozit de probă, care a scris în
    `/tmp/precommit_pytest.log` CÂT îl scria pytest-ul porții reale — logul a ieșit stricat și respingerea fără numele testului picat.
    Acum hook-urile scriu în `$POARTA_JURNALE` (implicit /tmp), iar sesiunea de teste îl pune pe un director al ei (`conftest.py`).
    MUTAȚIE: o cale `/tmp/precommit_` pusă înapoi într-un hook -> pică; `POARTA_JURNALE` scos din conftest -> pică."""
    import io
    for nume in ("poarta-suita", "pre-commit"):
        t = io.open(os.path.join(_HOOKS, nume), encoding="utf-8").read()
        assert t.count("/tmp/precommit_") == 0, nume
    d = os.environ.get("POARTA_JURNALE", "")
    assert d.startswith(tempfile.gettempdir()) and os.path.basename(d).startswith("poarta_jurnale_teste_"), d
    cod, iesire, _dur = _ruleaza("Reparație mică\n".encode("utf-8"), hook="poarta-suita")
    assert iesire.count("[poarta] pytest") == 1, iesire
    assert os.path.isfile(os.path.join(d, "precommit_pytest.log"))


def test_poarta_ruleaza_toata_suita_in_paralel_fara_selectie():
    """[11.10.2026, comanda Costin pct.4e: „Fă poarta mai rapidă fără să scoți niciun test”] Poarta rulează pytest în paralel
    (pytest-xdist, `--dist loadfile`) pe TOATĂ suita: linia lui pytest n-are cale, `-k`, `-m`, `--deselect`, `--ignore` sau `-x` —
    nimic care să lase un test pe dinafară. MUTAȚIE: `--ignore=frontend_test` (sau `-k "not lent"`) pe linia pytest -> pică;
    `-n` scos (rulare serială, poarta înapoi la ~82 de minute) -> pică."""
    import io
    import re as _re
    t = io.open(os.path.join(_RAD, "scripts", "githooks", "poarta-suita"), encoding="utf-8").read()
    linii = [x for x in t.splitlines() if _re.match(r'^"\$PY" -m pytest\b', x)]
    assert len(linii) == 1, linii
    arg = linii[0].split(">")[0].split()[3:]
    assert arg[:1] == ["-q"] and arg.count("-n") == 1 and arg.count("--dist") == 1 and arg[arg.index("--dist") + 1] == "loadfile", arg
    # [30.10.2026, CLAUDE.md §5] singura excepție: lista scripts/poarta_forma.txt (teste de formă), prin `$IGN`
    straine = [a for a in arg if a not in ("-q", "-n", '"$NW"', "--dist", "loadfile", "$IGN")]
    assert straine == [], "pytest-ul porții alege teste: %s" % straine
    lista = [x.strip() for x in io.open(os.path.join(_RAD, "scripts", "poarta_forma.txt"), encoding="utf-8")
             if x.strip() and not x.startswith("#")]
    assert lista and all(_re.match(r"^core/test_\w+\.py$", x) and os.path.isfile(os.path.join(_RAD, x)) for x in lista), lista


def test_plasa_porneste_numai_dupa_verdictul_pytest():
    """[11.10.2026, măsurat] Plasa e2e pornește aplicația pe ACEEAȘI bază de test pe care rulează pytest, iar pornirea aplicației
    reface triggerele fiecărei firme. Suprapuse (proba din 11.10, 22:16): deadlock, pool-ul aplicației epuizat, plasa agățată două ore.
    Deci în poartă rularea plasei vine DUPĂ `asteapta_pytest` și după verdictul lui (`RC=$RC_PYTEST`), nu în timpul lui. MUTAȚIE: blocul
    plasei mutat înaintea așteptării lui pytest -> pică."""
    import io
    t = io.open(os.path.join(_RAD, "scripts", "githooks", "poarta-suita"), encoding="utf-8").read()
    linii = t.splitlines()
    porneste = next(i for i, x in enumerate(linii) if x.startswith('"$PY" -m pytest '))
    plasa = next(i for i, x in enumerate(linii) if x.startswith('"$PY" scripts/e2e_poarta.py'))
    asteapta = [i for i, x in enumerate(linii) if x.strip() == "asteapta_pytest"]
    verdict = [i for i, x in enumerate(linii) if x.strip() == "RC=$RC_PYTEST"]
    assert asteapta and verdict, (asteapta, verdict)
    assert porneste < min(asteapta) < min(verdict) < plasa, (porneste, asteapta, verdict, plasa)


def test_defectul_nereparat_poate_trimite_la_deficiente_cu_numarul():
    """[16.10.2026] Un defect lăsat nereparat se consemnează în `DEFICIENTE.md` (registrul canonic, CLAUDE.md §2.2.0): mesajul care
    spune „DEFICIENTE 271” are loc; fără loc, sau cu registrul fără număr, e respins. MUTAȚIE: `DEFICIENTE…` scos din `LOC` -> pică."""
    baza = "Lotul X\n\n- 271: cauza aflată — nereparat, la cerere%s.\n"
    assert _ruleaza((baza % " (DEFICIENTE 271)").encode("utf-8"))[0] == 0
    assert _ruleaza((baza % " (DEFICIENTE.md C40)").encode("utf-8"))[0] == 0
    for fara in ("", " (DEFICIENTE)"):
        cod, iesire, _dur = _ruleaza((baza % fara).encode("utf-8"))
        assert cod == 1 and iesire.count("nu spune UNDE") == 1, iesire


import pytest  # noqa: E402

from core.test_poarta_lot import depozit_poarta  # noqa: E402,F401 — fixtura depozitului cu poarta adevărată

#: chemările celor cinci părți, cum le înregistrează pythonul de probă
PARTILE = {"proaspat": "-m pytest -q -k proaspat core/", "pytest": "-m pytest -q -n 3 --dist loadfile",
           "verificator": "verificator_conformitate.py", "cifre": "scripts/cifre_referinta.py --productie --verifica",
           "plasa": "scripts/e2e_poarta.py "}
ROSII = {"proaspat": {"proaspat": "core/test_c.py::test_artefact_proaspat"}, "pytest": {"pytest": "core/test_c.py::test_trei"},
         "verificator": {"verificator": "3"}, "cifre": {"cifre": "1"}, "plasa": {"plasa": "e2e_x.py::test_e"}}


@pytest.mark.parametrize("rosie", [None] + sorted(ROSII))
def test_poarta_suita_ruleaza_toate_partile_dupa_una_rosie_si_scrie_rularea(depozit_poarta, rosie):
    """[23.10.2026] Oricare parte e roșie (sau niciuna), poarta rulează TOATE cinci, o dată fiecare, în ordine (prospețimea, pytest
    pornit înaintea verificatorului și a cifrelor, plasa după), iese 1 dacă vreuna e roșie, și scrie JSON-ul: per parte rc, durata și
    căzutele (complete față de rezumatul pytest), plus linia `DURATE` (VERDE / ROSU cu partea) în `.poarta_jurnal.log`.
    MUTAȚII: `exit 1` pus înapoi după verificatorul roșu -> cifrele și plasa nu mai rulează -> pică; `incheie` scos -> fără JSON -> pică."""
    dp = depozit_poarta
    sha = dp.git("rev-parse", "HEAD")
    cod, iesire = dp.suita(**(ROSII[rosie] if rosie else {}))
    assert cod == (1 if rosie else 0), iesire
    chem = dp.chemari()
    rulate = [next(n for n, c in PARTILE.items() if x.startswith(c)) for x in chem]
    assert sorted(rulate) == sorted(PARTILE) and rulate.index("proaspat") == 0 and rulate.index("plasa") == 4, chem
    r = dp.rulare(sha)
    assert (r["sha"], r["ramura"], r["tip"], r["verde"]) == (sha, "lucru/lot9", "completa", not rosie), r
    assert sorted(r["parti"]) == sorted(list(PARTILE) + ["arbore"]), r
    assert {n for n, p in r["parti"].items() if p["rc"]} == ({rosie} if rosie else set()), r["parti"]
    assert all(isinstance(p["durata_s"], int) and p["durata_s"] >= 0 for p in r["parti"].values()), r["parti"]
    # căzutele pe noduri (prospețime, pytest, plasa) sunt complete față de rezumatul pytest; verificatorul și cifrele n-au noduri
    assert all(r["parti"][n]["cazute_complete"] for n in ("proaspat", "pytest", "plasa")), r["parti"]
    if rosie in ("proaspat", "pytest", "plasa"):
        assert r["parti"][rosie]["cazute"] == [ROSII[rosie][rosie]], r["parti"][rosie]
    durate = [x for x in dp.jurnal().splitlines() if x.startswith("    DURATE: ")]
    assert len(durate) == 1 and durate[0].count(" ROSU " if rosie else " VERDE ") == 1, durate
    assert all(durate[0].count("%s " % n) >= 1 for n in ("proaspat", "pytest", "verificator", "cifre", "plasa", "poarta")), durate


def test_poarta_suita_cu_toate_partile_rosii_le_consemneaza_pe_toate(depozit_poarta):
    """Toate cinci roșii: cinci respingeri consemnate în jurnal, cinci rc nenule în JSON — nicio parte nu o ascunde pe alta."""
    dp = depozit_poarta
    toate = {k: v for d in ROSII.values() for k, v in d.items()}
    cod, iesire = dp.suita(**toate)
    assert cod == 1 and iesire.count("[poarta] ROSU: ") == 5, iesire
    assert dp.jurnal().count("=== ") == 5
    parti = dp.rulare(dp.git("rev-parse", "HEAD"))["parti"]
    assert sorted(n for n, p in parti.items() if p["rc"]) == sorted(PARTILE), parti
    assert json.dumps(parti, ensure_ascii=False).count("FAILED") == 0     # nodurile, nu rândurile brute
