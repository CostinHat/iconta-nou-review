# -*- coding: utf-8 -*-
"""scripts/poarta_lib.py — piesele comune ale bazei și ale clasificării porții (comanda 16.1, pct.1a).
  nume_stabil / citeste_junit   rezultatul pe test, din raportul junit al pytest (numele = cale::test, fără parametri de rulare)
  asertiuni                     numărul de aserțiuni statice dintr-un test (nodurile `assert` și apelurile assert*/expect*/raises)
  hash_fisier                   sha256 pe fișier (hash-urile scripturilor porții, ale manifestului)"""
import ast
import hashlib
import os
import re
import subprocess
import xml.etree.ElementTree as ET

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def hash_fisier(cale):
    return hashlib.sha256(open(cale, "rb").read()).hexdigest() if os.path.exists(cale) else "lipsa"


def lot_fisier(lot):
    """Numele lotului în căi și fișiere de stare: `16.1-C2` -> `16_1_C2`."""
    return re.sub(r"[.\-]", "_", lot)


def lot_baza(lot):
    """Lotul a cărui bază (docs/dovezi/<lot>/baza.json) o folosește: un lot de corecție (`16.1-C2`) moștenește baza lotului de bază (`16.1`)."""
    return lot.split("-")[0]


def _git_text(rad, *a):
    r = subprocess.run(["git", *a], cwd=rad, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def manifest_refuzuri(rad, commit_baza, main="main", cale_manifest=None):
    """Creșterea manifestului în lot (16.1-C2, pct.1): manifestul curent diferă de cel de la commitul bazei numai prin rânduri ADĂUGATE pentru fișiere de test noi,
    prezente în diff-ul lotului față de `main` și absente pe `main`. Orice rând lipsă, modificat (și numărul de teste al unui fișier existent) sau adăugat pentru un
    fișier existent pe main ori în afara diff-ului = refuz cu numele fișierului. -> lista refuzurilor (goală = acceptat)."""
    def randuri(text):
        date, alte = {}, []
        for ln in text.splitlines():
            if ln.strip() and not ln.startswith("#"):
                date[ln.split("\t")[0]] = ln
            else:
                alte.append(ln)
        return date, alte
    vechi_t = _git_text(rad, "show", "%s:%s" % (commit_baza, MANIFEST))
    if vechi_t is None:
        return ["manifestul nu există la commitul bazei (%s)" % commit_baza[:8]]
    vechi, alte_v = randuri(vechi_t)
    nou, alte_n = randuri(open(cale_manifest or os.path.join(rad, MANIFEST), encoding="utf-8").read())
    diff = set((_git_text(rad, "diff", "--name-only", commit_baza, "HEAD") or "").split())
    ref = []
    if alte_v != alte_n:
        ref.append("%s: liniile de antet / comentarii s-au schimbat" % MANIFEST)
    for f in sorted(vechi):
        if f not in nou:
            ref.append("%s: rând lipsă" % f)
        elif nou[f] != vechi[f]:
            ref.append("%s: rând modificat (hash, număr de teste sau comandă)" % f)
    for f in sorted(set(nou) - set(vechi)):
        if subprocess.run(["git", "cat-file", "-e", "%s:%s" % (main, f)], cwd=rad, capture_output=True).returncode == 0:
            ref.append("%s: rând adăugat pentru un fișier existent pe %s" % (f, main))
        elif f not in diff:
            ref.append("%s: rând adăugat pentru un fișier care nu e în diff-ul lotului" % f)
    return ref


def nume_stabil(classname, name, rad):
    """`core.test_x.TestC` + `test_y[p]` -> `core/test_x.py::TestC::test_y[p]`; cu `classname` fără director (plasa e2e, rootdir = e2e) fișierul se caută în frontend_test/e2e."""
    parti = classname.split(".")
    for i in range(len(parti), 0, -1):
        for baza in ("", "frontend_test/e2e/"):
            cale = baza + "/".join(parti[:i]) + ".py"
            if os.path.isfile(os.path.join(rad, cale)):
                return "::".join([cale] + parti[i:] + [name])
    return "::".join([classname, name])


_INFRA = re.compile(r"(Connection refused|Connection reset|could not connect to server|server closed the connection|ECONNREFUSED|ERR_CONNECTION|"
                    r"Target page, context or browser has been closed|aplicația exportului n-a răspuns|OperationalError)", re.I)


def citeste_junit(cale, rad):
    """-> listă de {nume, rezultat: trece|pica|sarit, infra: bool, durata, mesaj}. Un fișier lipsă sau stricat = listă goală."""
    try:
        arbore = ET.parse(cale).getroot()
    except (OSError, ET.ParseError):
        return []
    rez = []
    for tc in arbore.iter("testcase"):
        r, mesaj = "trece", ""
        for fiu in tc:
            if fiu.tag in ("failure", "error"):
                r, mesaj = "pica", (fiu.get("message") or "") + " " + (fiu.text or "")[:2000]
            elif fiu.tag == "skipped" and r == "trece":
                r = "sarit"
        rez.append({"nume": nume_stabil(tc.get("classname", ""), tc.get("name", ""), rad), "rezultat": r,
                    "infra": r == "pica" and bool(_INFRA.search(mesaj)), "durata": round(float(tc.get("time") or 0), 3), "mesaj": mesaj[:300].strip()})
    return rez


def _numara(nod):
    n = 0
    for x in ast.walk(nod):
        if isinstance(x, ast.Assert):
            n += 1
        elif isinstance(x, ast.Call):
            f = x.func
            nume = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if nume.startswith(("assert", "expect")) or nume in ("raises", "fail"):
                n += 1
    return n


def asertiuni(rad, fisier):
    """-> {`Clasa::test` sau `test`: număr}, din AST; fișier lipsă sau care nu se parsează = {}."""
    try:
        arbore = ast.parse(open(os.path.join(rad, fisier), encoding="utf-8").read())
    except (OSError, SyntaxError):
        return {}
    rez = {}
    for nod in arbore.body:
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)) and nod.name.startswith("test"):
            rez[nod.name] = _numara(nod)
        elif isinstance(nod, ast.ClassDef):
            for f in nod.body:
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test"):
                    rez[nod.name + "::" + f.name] = _numara(f)
    return rez


def cheie_asertiuni(nume):
    """`cale::[Clasa::]test[param]` -> (cale, `[Clasa::]test`)."""
    p = nume.split("::")
    return p[0], "::".join(p[1:]).split("[")[0]


# ---------------------------------------------------------------------------------------------------------------------------------------------
# rularea treptelor (comună bazei și candidatului): verificatorul de design, pytest pe nucleu, plasa e2e din manifest — fără oprire la prima roșie
# ---------------------------------------------------------------------------------------------------------------------------------------------
import contextlib   # noqa: E402
import sys   # noqa: E402
import time   # noqa: E402

MANIFEST = "scripts/plasa_16_2.manifest"
NUCLEU = "scripts/poarta_nucleu.txt"


def _rulare(cmd, cwd, env, log):
    t0 = time.time()
    with open(log, "w") as f:
        r = subprocess.run(cmd, cwd=cwd, env=env, stdout=f, stderr=subprocess.STDOUT)
    return r.returncode, round(time.time() - t0, 1)


def fisiere_nucleu(wt):
    return [ln.strip() for ln in open(os.path.join(wt, NUCLEU), encoding="utf-8") if ln.strip() and not ln.startswith("#")]


def fisiere_manifest(wt):
    return [ln.split("\t")[0] for ln in open(os.path.join(wt, MANIFEST), encoding="utf-8") if ln.strip() and not ln.startswith("#")]


@contextlib.contextmanager
def faza(lot, nume, detalii=""):
    """Faza în jurnalul lotului (început, sfârșit); lot None = fără jurnal (calibrări, baza)."""
    if lot is None:
        yield {}
        return
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import jurnal_lot as J
    id_ = J.inceput(lot, nume, detalii, pid=os.getpid())
    rez = {"rezultat": "intrerupt"}
    try:
        yield rez
    finally:
        J.sfarsit(lot, nume, id_, rez["rezultat"])


def ruleaza_trepte(wt, J, lot=None, pytest_ids=None, e2e_fisiere=None, procese="3", detalii="", verificator=True):
    """-> (durate pe treaptă, teste). `pytest_ids`/`e2e_fisiere` None = tot (nucleul / manifestul); listă = numai acelea (reluarea). Baza de test se restaurează înainte de
    pytest și înainte de plasa e2e (niciodată per test). Toate treptele rulează, și după una roșie."""
    py = "./venv/bin/python"
    env = dict(os.environ, POARTA_SARE="1", PATH=os.path.join(wt, "scripts", "bin") + ":" + os.environ.get("PATH", ""))
    trepte, teste = {}, []
    if verificator:
        with faza(lot, "poarta_verificator", detalii) as f:
            _, d = _rulare([py, "verificator_conformitate.py"], wt, env, os.path.join(J, "poarta_verificator.log"))
            tot = [ln for ln in open(os.path.join(J, "poarta_verificator.log"), errors="replace") if "TOTAL" in ln.upper()]
            trece = bool(tot) and "TOTAL: 0" in tot[-1]
            f["rezultat"] = "verde" if trece else "rosu"
        trepte["verificator"] = d
        teste.append({"nume": "verificator::TOTAL", "treapta": "verificator", "rezultat": "trece" if trece else "pica", "infra": False, "durata": d,
                      "mesaj": "" if trece else (tot[-1].strip() if tot else "fără TOTAL")})
    ids = fisiere_nucleu(wt) if pytest_ids is None else pytest_ids
    if ids:
        with faza(lot, "poarta_pytest", detalii) as f:
            _rulare(["sh", "scripts/baza_test.sh", "restaureaza"], wt, env, os.path.join(J, "poarta_restaurare_pytest.log"))
            jx = os.path.join(J, "poarta_pytest.xml")
            rc, d = _rulare([py, "-m", "pytest", "-q", "-n", procese, "--dist", "loadfile", "--junitxml=" + jx] + ids, wt, env, os.path.join(J, "poarta_pytest.log"))
            f["rezultat"] = "verde" if rc == 0 else "rosu_%d" % rc
        trepte["pytest"] = d
        r = citeste_junit(jx, wt)
        teste += [dict(t, treapta="pytest") for t in r]
        if rc not in (0, 1) and not r:   # pytest n-a ajuns să ruleze nimic (interpretare, import, interrupt): infrastructură, nu test
            teste.append({"nume": "pytest::sesiune", "treapta": "pytest", "rezultat": "pica", "infra": True, "durata": d, "mesaj": "cod %d fără raport junit" % rc})
    fis = [os.path.basename(x) for x in fisiere_manifest(wt)] if e2e_fisiere is None else e2e_fisiere
    if fis:
        with faza(lot, "poarta_plasa", detalii) as f:
            _rulare(["sh", "scripts/baza_test.sh", "restaureaza"], wt, env, os.path.join(J, "poarta_restaurare_e2e.log"))
            jx = os.path.join(J, "poarta_e2e.xml")
            rc, d = _rulare([py, "scripts/e2e_poarta.py"] + ["--doar=" + x for x in fis] + [os.path.join(J, "e2e_poarta_capturi")],
                            wt, dict(env, PYTEST_ADDOPTS="--junitxml=" + jx), os.path.join(J, "poarta_e2e.log"))
            f["rezultat"] = "verde" if rc == 0 else "rosu_%d" % rc
        trepte["plasa_e2e"] = d
        r = citeste_junit(jx, wt)
        teste += [dict(t, treapta="plasa_e2e") for t in r]
        if rc not in (0, 1) and not r:   # 3 = aplicația n-a pornit
            teste.append({"nume": "plasa_e2e::sesiune", "treapta": "plasa_e2e", "rezultat": "pica", "infra": True, "durata": d, "mesaj": "cod %d fără raport junit" % rc})
    return trepte, teste
