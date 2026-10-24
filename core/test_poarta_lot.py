# -*- coding: utf-8 -*-
"""GARDA lansatorului porții de lot `scripts/poarta_lot.sh` (15.10.2026, comanda Costin, verbatim în DECIZII „Poarta o dată pe lot”:
„Poarta completă: o singură dată pe lot, la închiderea lotului, înainte de publicarea pe producție. [...] main acceptă un commit doar
dacă jurnalul porții îl arată verde. [...] Maximum două rulări complete pe lot; dacă a doua pică, te oprești și raportezi.”).

Pe un depozit TEMPORAR, cu lansatorul adevărat și o `poarta-suita` de probă (iese cu codul din `PROBA_RC`; adevărata ar rula ~70 de
minute): verdictul se scrie în `<git-common-dir>/poarta_verdicte.log` (`VERDE|ROSU <sha> <ramura> <data>`), iar lansatorul REFUZĂ —
fără să pornească poarta — pe `main`, pe arbore murdar, pe un SHA deja VERDE și pe un SHA deja ROȘU.
MUTAȚIILE: fiecare din cele patru refuzuri scos din `poarta_lot.sh` -> testul lui pică.

POARTA COMPUSĂ (23.10.2026, CLAUDE.md §5: „Poarta completă se reia numai dacă reparația a atins piese folosite în mai multe locuri sau
dacă perimetrul ei nu e sigur. Verdictul pentru commitul reparat se compune din rularea completă anterioară plus rerularea țintită.”;
DECIZII 23.10.2026 „Comanda 12.1”). Pe `depozit_poarta` — un depozit temporar cu lansatorul, `poarta-suita`, `poarta_scurta.py` și
`perimetru.py` ADEVĂRATE și un `venv/bin/python` de probă care imită uneltele grele (pytest, verificatorul, cifrele, plasa; căzutele din
`PROBA_*`) și le înregistrează chemările — se probează: verdictul `… compus:<X>` pe rerulare verde / roșie, cu exact căzutele lui X plus
perimetrul reparației; refuzul (niciun verdict) fără rulare completă ROȘIE, pe perimetru nesigur, pe X care nu e strămoș, pe căzute
nenumărabile. MUTAȚIILE sunt la fiecare test."""
import json
import os
import shutil
import subprocess
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANSATOR = os.path.join(RAD, "scripts", "poarta_lot.sh")
PROBA = '#!/bin/sh\necho "[proba] poarta-suita"\nexit "${PROBA_RC:-0}"\n'


def _git(d, *a):
    r = subprocess.run(("git",) + a, cwd=d, capture_output=True, text=True,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                                GIT_COMMITTER_EMAIL="t@t"))
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


@pytest.fixture()
def depozit(tmp_path):
    d = tmp_path / "r"
    (d / "scripts" / "githooks").mkdir(parents=True)
    shutil.copy(LANSATOR, d / "scripts" / "poarta_lot.sh")
    (d / "scripts" / "githooks" / "poarta-suita").write_text(PROBA)
    _git(d, "init", "-q", "-b", "main")
    _git(d, "add", "scripts")
    _git(d, "commit", "-q", "-m", "baza")
    _git(d, "checkout", "-q", "-b", "lucru/lot9")
    return d


def _lanseaza(d, rc=0):
    r = subprocess.run(["sh", "scripts/poarta_lot.sh"], cwd=d, capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, PROBA_RC=str(rc)))
    return r.returncode, r.stdout + r.stderr


def _verdicte(d):
    p = d / ".git" / "poarta_verdicte.log"
    return [x.split()[:3] for x in p.read_text().splitlines()] if p.exists() else []


def test_verde_scrie_verdictul_commitului(depozit):
    d = depozit
    sha = _git(d, "rev-parse", "HEAD")
    cod, iesire = _lanseaza(d, 0)
    assert (cod, iesire.count("[proba] poarta-suita")) == (0, 1), iesire
    assert _verdicte(d) == [["VERDE", sha, "lucru/lot9"]]


def test_acelasi_sha_verde_nu_se_mai_ruleaza(depozit):
    d = depozit
    assert _lanseaza(d, 0)[0] == 0
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0 and iesire.count("are deja poarta VERDE") == 1, iesire
    assert len(_verdicte(d)) == 1


def test_rularile_continua_pana_la_verde(depozit):
    """Regula 3d (comanda Costin 11.2, 22.10.2026; supersedează „maximum două rulări pe lot”, 15.10.2026): roșu -> reparație -> roșu ->
    reparație -> verde; fiecare commit nou pornește poarta, fără limită de rulări."""
    d = depozit
    assert _lanseaza(d, 1)[0] == 1
    _git(d, "commit", "-q", "--allow-empty", "-m", "reparatia")
    assert _lanseaza(d, 1)[0] == 1
    _git(d, "commit", "-q", "--allow-empty", "-m", "a doua reparatie")
    cod, iesire = _lanseaza(d, 0)
    assert cod == 0 and iesire.count("[proba] poarta-suita") == 1, iesire
    assert [v[0] for v in _verdicte(d)] == ["ROSU", "ROSU", "VERDE"]


def test_acelasi_sha_rosu_nu_se_reia(depozit):
    """Regula 3d: pe roșu se repară CODUL; aceeași rulare pe același commit nu repară nimic (și ar trece un test instabil pe noroc)."""
    d = depozit
    assert _lanseaza(d, 1)[0] == 1
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0 and iesire.count("are deja poarta ROSIE") == 1, iesire
    assert [v[0] for v in _verdicte(d)] == ["ROSU"]


def test_arborele_murdar_e_refuzat(depozit):
    d = depozit
    (d / "nou.py").write_text("x = 1\n")
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0 and iesire.count("    ?? nou.py") == 1, iesire
    assert _verdicte(d) == []


def test_pe_main_e_refuzat(depozit):
    d = depozit
    _git(d, "checkout", "-q", "main")
    cod, iesire = _lanseaza(d, 0)
    assert cod == 1 and iesire.count("[proba] poarta-suita") == 0, iesire
    assert _verdicte(d) == []



# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#  DEPOZITUL DE PROBĂ CU POARTA ADEVĂRATĂ (folosit și de core/test_poarta_ordine.py, core/test_poarta_scurta.py, core/test_deficiente.py)
# ═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#: `venv/bin/python` de probă: înregistrează chemarea în `$PROBA_CHEMARI` și imită uneltele grele; orice altceva (`-c`, scripturile
#: `poarta_scurta.py` / `perimetru.py`) -> pythonul adevărat al testelor. Căzutele: nodurile din `PROBA_PROASPAT` / `PROBA_PYTEST` /
#: `PROBA_PLASA` (separate prin spațiu), cu rezumatul pytest; `PROBA_PLASA_FARA_REZUMAT=1` = plasa cade fără listă (aplicația n-a pornit).
PY_PROBA = """#!/bin/sh
echo "$*" >> "$PROBA_CHEMARI"
cazute() {
    if [ -n "$1" ]; then
        for n in $1; do echo "FAILED $n - AssertionError: proba"; done
        echo "$2$(echo $1 | wc -w) failed, 5 passed in 0.10s"
        exit 1
    fi
    echo "${2}5 passed in 0.10s"
    exit 0
}
if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then
    case "$*" in *"-k proaspat"*) cazute "$PROBA_PROASPAT" "" ;; *) cazute "$PROBA_PYTEST" "" ;; esac
fi
case "$1" in
    verificator_conformitate.py) echo "TOTAL: ${PROBA_VERIFICATOR:-0} candidate"; exit 0 ;;
    scripts/cifre_referinta.py) echo "[cifre] proba"; exit "${PROBA_CIFRE:-0}" ;;
    scripts/e2e_poarta.py) [ -n "$PROBA_PLASA_FARA_REZUMAT" ] && { echo "[e2e] aplicatia n-a pornit"; exit 3; }
                           cazute "$PROBA_PLASA" "[e2e] " ;;
esac
exec "%s" "$@"
"""
FISIERE_PROBA = {
    ".gitignore": "venv/\n.poarta_jurnal.log\n__pycache__/\n",
    "main.py": "# radacina de compunere (proba)\n",
    "core/__init__.py": "",
    "core/a.py": "X = 1\n",
    "core/b.py": "Y = 1\n",
    "core/test_a.py": "import core.a\n\n\ndef test_unu():\n    assert core.a.X\n",
    "core/test_b.py": "import core.b\n\n\ndef test_doi():\n    assert core.b.Y\n",
    "core/test_c.py": "def test_trei():\n    assert True\n",
    "frontend_test/e2e/e2e_x.py": "def test_e():\n    assert True\n",
    "scripts/e2e_poarta.py": "# plasa (proba; chemarea o imita venv/bin/python)\n",
    "scripts/scan_trasee.py": "def citeste_rute():\n    return []\n",
}


class DepozitPoarta:
    """Depozitul de probă: `lanseaza(*argumente, **PROBA_)` rulează `scripts/poarta_lot.sh`, `suita(**PROBA_)` pe `poarta-suita`;
    `chemari()` = liniile de argumente ale uneltelor imitate, `verdicte()` / `rulare(sha)` = jurnalul și înregistrarea JSON."""

    def __init__(self, tmp_path):
        self.d = tmp_path / "r"
        self.jurnale = tmp_path / "jurnale"
        self.jurnale.mkdir()
        self.chem = tmp_path / "chemari.log"
        for rel, cont in FISIERE_PROBA.items():
            (self.d / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.d / rel).write_text(cont)
        for rel in ("scripts/poarta_lot.sh", "scripts/poarta_scurta.py", "scripts/perimetru.py", "scripts/githooks/poarta-suita"):
            (self.d / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(os.path.join(RAD, rel), self.d / rel)
        py = self.d / "venv" / "bin" / "python"
        py.parent.mkdir(parents=True)
        py.write_text(PY_PROBA % sys.executable)
        os.chmod(py, 0o755)
        _git(self.d, "init", "-q", "-b", "main")
        _git(self.d, "add", ".")
        _git(self.d, "commit", "-q", "-m", "baza")
        _git(self.d, "checkout", "-q", "-b", "lucru/lot9")

    def git(self, *a):
        return _git(self.d, *a)

    def comite(self, rel, cont, mesaj="reparatia"):
        (self.d / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.d / rel).write_text(cont)
        _git(self.d, "add", rel)
        _git(self.d, "commit", "-q", "-m", mesaj)
        return _git(self.d, "rev-parse", "HEAD")

    def _env(self, proba):
        self.chem.write_text("")
        return dict(os.environ, POARTA_JURNALE=str(self.jurnale), PROBA_CHEMARI=str(self.chem),
                    **{"PROBA_" + k.upper(): v for k, v in proba.items()})

    def lanseaza(self, *argumente, **proba):
        r = subprocess.run(["sh", "scripts/poarta_lot.sh"] + list(argumente), cwd=self.d, capture_output=True, text=True, timeout=300,
                           env=self._env(proba))
        return r.returncode, r.stdout + r.stderr

    def suita(self, **proba):
        r = subprocess.run(["sh", "scripts/githooks/poarta-suita"], cwd=self.d, capture_output=True, text=True, timeout=300,
                           env=self._env(proba))
        return r.returncode, r.stdout + r.stderr

    def chemari(self):
        return [x for x in self.chem.read_text().splitlines() if not x.startswith("-c ")]

    def verdicte(self):
        p = self.d / ".git" / "poarta_verdicte.log"
        return [x.split() for x in p.read_text().splitlines()] if p.exists() else []

    def rulare(self, sha):
        p = self.d / ".git" / "poarta_rulari" / ("%s.json" % sha)
        return json.loads(p.read_text()) if p.exists() else None

    def jurnal(self):
        p = self.d / ".poarta_jurnal.log"
        return p.read_text() if p.exists() else ""


@pytest.fixture()
def depozit_poarta(tmp_path):
    return DepozitPoarta(tmp_path)


def _rosu_complet(dp, **proba):
    """O rulare COMPLETĂ roșie pe HEAD (X): `pytest` și plasa cad pe câte un nod, dacă nu se spune altfel."""
    proba = proba or {"pytest": "core/test_c.py::test_trei", "plasa": "e2e_x.py::test_e"}
    x = dp.git("rev-parse", "HEAD")
    cod, iesire = dp.lanseaza(**proba)
    assert cod == 1 and dp.verdicte()[-1][:3] == ["ROSU", x, "lucru/lot9"] and len(dp.verdicte()[-1]) == 4, iesire
    return x


def test_compus_verde_reruleaza_cazutele_lui_x_plus_perimetrul_reparatiei(depozit_poarta):
    """Rularea completă a lui X cade pe `core/test_c.py::test_trei` și pe `e2e_x.py::test_e`; reparația atinge `core/a.py`. Compusul
    rulează EXACT: pytest pe perimetrul reparației (`core/test_a.py`) + nodul căzut, plasa pe nodul căzut (din index, fără `--arbore`),
    prospețimea, verificatorul, cifrele — și scrie `VERDE <H> <ramura> <data> compus:<X>` + înregistrarea lui H.
    MUTAȚIE: căzutele lui X scoase din selecție (`pytest_sel = list(teste)`) -> pică; sufixul `compus:` scos din `poarta_lot.sh` -> pică."""
    dp = depozit_poarta
    x = _rosu_complet(dp)
    h = dp.comite("core/a.py", "X = 2\n")
    cod, iesire = dp.lanseaza("--compus")
    assert cod == 0, iesire
    v = dp.verdicte()[-1]
    assert (v[:3], v[4:]) == (["VERDE", h, "lucru/lot9"], ["compus:%s" % x]), v
    assert sorted(dp.chemari()) == sorted([
        "-m pytest -q -k proaspat core/",
        "-m pytest -q -n 3 --dist loadfile core/test_a.py core/test_c.py::test_trei",
        "verificator_conformitate.py",
        "scripts/cifre_referinta.py --productie --verifica",
        "scripts/e2e_poarta.py --doar=e2e_x.py::test_e",
        "scripts/poarta_scurta.py --compus=%s" % x]), dp.chemari()
    r = dp.rulare(h)
    assert (r["tip"], r["compus_din"], r["verde"]) == ("compus", x, True), r
    assert sorted(r["parti"]) == ["cifre", "plasa", "proaspat", "pytest", "verificator"], r
    assert iesire.count("[compus] DURATE: ") == 1 and dp.jurnal().count("compus din %s" % x[:12]) == 1, iesire


def test_compus_rosu_scrie_rosu_compus(depozit_poarta):
    """Rerularea țintită pică (nodul lui X tot cade) -> `ROSU <H> <ramura> <data> compus:<X>`, exit nenul. MUTAȚIE: exit-ul compusului
    ignorat în `poarta_lot.sh` (`RC=0` după `poarta_scurta.py --compus`) -> pică."""
    dp = depozit_poarta
    x = _rosu_complet(dp)
    h = dp.comite("core/a.py", "X = 2\n")
    cod, iesire = dp.lanseaza("--compus", pytest="core/test_c.py::test_trei")
    assert cod == 1, iesire
    v = dp.verdicte()[-1]
    assert (v[:3], v[4:]) == (["ROSU", h, "lucru/lot9"], ["compus:%s" % x]), v
    assert dp.rulare(h)["parti"]["pytest"]["cazute"] == ["core/test_c.py::test_trei"]


@pytest.mark.parametrize("verdicte", [[], ["VERDE"]])
def test_compus_fara_rulare_completa_rosie_e_refuzat(depozit_poarta, verdicte):
    """Fără o rulare COMPLETĂ ROȘIE pe ramură (nicio rulare / numai una verde) nu are din ce se compune: refuz, niciun verdict nou,
    nicio unealtă pornită. MUTAȚIE: refuzul `[ -z "$X" ]` scos din `poarta_lot.sh` -> pică."""
    dp = depozit_poarta
    if verdicte:
        assert dp.lanseaza()[0] == 0
        dp.comite("core/a.py", "X = 2\n")
    inainte = dp.verdicte()
    cod, iesire = dp.lanseaza("--compus")
    assert cod == 1 and iesire.count("cere o rulare COMPLETA ROSIE anterioara") == 1, iesire
    assert dp.verdicte() == inainte and dp.chemari() == [], dp.chemari()


@pytest.mark.parametrize("atins,cont,motiv", [
    ("main.py", "# atins\n", "main.py — rutele sunt citite de scanere"),
    ("scripts/e2e_poarta.py", "# atins\n", "plasa atinsă integral"),
    ("core/nou.py", "Z = 1\n", "core/nou.py — fisier Python adaugat"),
    ("NOTE.txt", "x\n", "NOTE.txt — niciun test nu-l numește"),
])
def test_compus_refuzat_pe_perimetru_nesigur(depozit_poarta, atins, cont, motiv):
    """Perimetrul reparației nu se poate închide (`main.py`, plasa atinsă integral, un `.py` nou, un fișier pe care nu-l numește niciun
    test) -> REFUZ cu motivul, exit 2, niciun verdict pentru H, niciun test rulat: se rulează poarta completă.
    MUTAȚIE: `motive += incerte` scos din `plan_compus` -> pică (cazurile `main.py`, `core/nou.py`)."""
    dp = depozit_poarta
    _rosu_complet(dp)
    h = dp.comite(atins, cont)
    cod, iesire = dp.lanseaza("--compus")
    assert cod == 2 and iesire.count("REFUZ: compusul nu e sigur") == 1 and iesire.count(motiv) == 1, iesire
    assert [v for v in dp.verdicte() if v[1] == h] == [] and dp.rulare(h) is None
    assert [c for c in dp.chemari() if not c.startswith("scripts/poarta_scurta.py")] == [], dp.chemari()


def test_compus_refuzat_pe_x_care_nu_e_stramos(depozit_poarta):
    """Ultima rulare completă roșie e pe un X scos din istoria ramurii (reset) -> reparația nu pornește din ea: REFUZ, niciun verdict.
    MUTAȚIE: verificarea `merge-base --is-ancestor` scoasă din `plan_compus` -> pică."""
    dp = depozit_poarta
    baza = dp.git("rev-parse", "HEAD")
    dp.comite("core/b.py", "Y = 2\n", "x")
    x = _rosu_complet(dp)
    dp.git("reset", "-q", "--hard", baza)
    h = dp.comite("core/a.py", "X = 2\n")
    cod, iesire = dp.lanseaza("--compus")
    assert cod == 2 and iesire.count("%s nu e strămoș al lui HEAD" % x[:12]) == 1, iesire
    assert [v for v in dp.verdicte() if v[1] == h] == []


def test_compus_refuzat_cand_cazutele_lui_x_nu_se_pot_numara(depozit_poarta):
    """Plasa a căzut în X fără listă (aplicația n-a pornit: nimic de rerulat pe nume) -> nu se știe ce a căzut: REFUZ.
    MUTAȚIE: verificarea `cazute_complete` scoasă din `plan_compus` -> compusul trece -> pică."""
    dp = depozit_poarta
    x = _rosu_complet(dp, plasa_fara_rezumat="1")
    assert dp.rulare(x)["parti"]["plasa"] == dict(dp.rulare(x)["parti"]["plasa"], rc=3, cazute=[], cazute_complete=False)
    dp.comite("core/a.py", "X = 2\n")
    cod, iesire = dp.lanseaza("--compus")
    assert cod == 2 and iesire.count("plasa a căzut în %s (exit 3), dar lista testelor căzute nu e completă" % x[:12]) == 1, iesire
