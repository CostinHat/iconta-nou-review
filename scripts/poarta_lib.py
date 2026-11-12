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
    """Lotul a cărui bază (docs/dovezi/<lot>/baza.json) o folosește: lotul însuși când își are baza (16.1-C3), altfel un lot de corecție (`16.1-C2`) moștenește baza lotului de bază (`16.1`)."""
    if os.path.exists(os.path.join(RAD, "docs", "dovezi", lot_fisier(lot), "baza.json")):
        return lot
    return lot.split("-")[0]


def _git_text(rad, *a):
    r = subprocess.run(["git", *a], cwd=rad, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def plasa_modificabile(rad, lotf, head="HEAD"):
    """Căile numite de arhitect pe liniile `plasa_modificabile` din scripts/praguri_<lotf>.txt, citite la commitul `head` (17.5-C0) -> mulțime; fără linie = goală."""
    text = _git_text(rad, "show", "%s:scripts/praguri_%s.txt" % (head, lotf)) or ""
    cai = set()
    for ln in text.splitlines():
        parti = ln.split()
        if parti and parti[0] == "plasa_modificabile":
            cai.update(parti[1:])
    return cai


def manifest_refuzuri(rad, commit_baza, main="main", cale_manifest=None, modificabile=()):
    """Creșterea manifestului în lot (16.1-C2, pct.1): manifestul curent diferă de cel de la commitul bazei numai prin rânduri ADĂUGATE pentru fișiere de test noi,
    prezente în diff-ul lotului față de `main` și absente pe `main`. Orice rând lipsă, modificat (și numărul de teste al unui fișier existent) sau adăugat pentru un
    fișier existent pe main ori în afara diff-ului = refuz cu numele fișierului. -> lista refuzurilor (goală = acceptat).
    Excepția 17.5-C0: un rând MODIFICAT pentru o cale din `modificabile` (numită de arhitect în praguri) se acceptă numai dacă fișierul e în diff, comanda e aceeași,
    numărul de teste nu a scăzut și sha256 din rând e hash-ul fișierului din arborele de lucru."""
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
            motiv = _motiv_modificare(rad, f, vechi[f], nou[f], diff) if f in modificabile else "hash, număr de teste sau comandă"
            if motiv:
                ref.append("%s: rând modificat (%s)" % (f, motiv))
    for f in sorted(set(nou) - set(vechi)):
        if subprocess.run(["git", "cat-file", "-e", "%s:%s" % (main, f)], cwd=rad, capture_output=True).returncode == 0:
            ref.append("%s: rând adăugat pentru un fișier existent pe %s" % (f, main))
        elif f not in diff:
            ref.append("%s: rând adăugat pentru un fișier care nu e în diff-ul lotului" % f)
    return ref


def _motiv_modificare(rad, f, rand_vechi, rand_nou, diff):
    """Motivul pentru care un rând modificat al unei căi din `modificabile` rămâne refuz; None = modificarea e permisă."""
    v, n = rand_vechi.split("\t"), rand_nou.split("\t")
    if len(v) < 4 or len(n) < 4:
        return "rând cu mai puțin de patru câmpuri"
    if f not in diff:
        return "fișierul nu e în diff-ul lotului"
    if n[3] != v[3]:
        return "comanda s-a schimbat"
    try:
        if int(n[2]) < int(v[2]):
            return "numărul de teste a scăzut %s -> %s" % (v[2], n[2])
    except ValueError:
        return "număr de teste ilizibil"
    if n[1] != hash_fisier(os.path.join(rad, f)):
        return "sha256 diferit de hash-ul fișierului"
    return None


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
    rez = {"rezultat": "intrerupt", "id": id_}
    try:
        yield rez
    finally:
        J.sfarsit(lot, nume, id_, rez["rezultat"])


def rezultat_treapta(rc, teste, inv=None):
    """Eticheta jurnalului pentru o treaptă (16.1-C3, pct.5): `verde` (cod 0); `verde_cu_restante` când toate picăturile treptei sunt restanțe numerotate (clasele a/b/c din inventar,
    nicio infrastructură); altfel `rosu_<cod>`. O treaptă `verde_cu_restante` rămâne o rulare completă la contorul de rulări (contorul numără rulările, nu etichetele); rândurile
    vechi ale jurnalului nu se rescriu.
    [17.5-U, U.2a] Cod nenul și niciun raport junit proaspăt (lista de teste goală) = `infra`, nu `rosu_<cod>`: treapta n-a rulat nicio probă. O picătură de infrastructură CU raport
    rămâne `rosu_1`."""
    if rc == 0:
        return "verde"
    if not teste:
        return "infra"
    import poarta_clasifica as C
    inv = C._inventar() if inv is None else inv
    pica = [t for t in teste if t["rezultat"] == "pica"]
    if pica and all(not t.get("infra") and C._numarat(t["nume"], inv) for t in pica):
        return "verde_cu_restante"
    return "rosu_%d" % rc


def _sonda_8019():
    import verificator_design as VD
    return VD._raspunde()


def _opreste_8019():
    import verificator_design as VD
    VD.opreste()


_SONDA_IMPLICITA, _OPRESTE_IMPLICIT = _sonda_8019, _opreste_8019


def _sterge(cale):
    try:
        os.remove(cale)
    except FileNotFoundError:
        pass


class OprirePoarta(Exception):
    """[17.5-T] Oprirea (STOP) cerută de o treaptă: nu e roșu, nici infra; scripts/poarta_rulare.py o scrie în stare[oprit] și iese cu 3."""


#: calea FIXĂ (din depozit) a probei de mediu a plasei [17.5-T, T.6]: `fișier::test` pe prima linie utilă, durata celor trei rulări pe a doua; unealta citește numele de aici, nu îl alege la rulare
PROBA_MEDIU = os.path.join("docs", "dovezi", "17_5_T", "proba_mediu.txt")


def proba_mediu_nume(wt):
    """-> (`fișier::test`, None) sau (None, motivul) când fișierul probei lipsă sau gol sau când fișierul de test numit nu mai există în arbore."""
    cale = os.path.join(wt, PROBA_MEDIU)
    try:
        linii = [ln.strip() for ln in open(cale, encoding="utf-8") if ln.strip() and not ln.startswith("#")]
    except OSError:
        return None, "fișierul probei de mediu lipsește (%s)" % PROBA_MEDIU
    if not linii or "::" not in linii[0]:
        return None, "fișierul probei de mediu nu numește un test (%s)" % PROBA_MEDIU
    nume = linii[0].split()[0]
    fis, _, test = nume.partition("::")
    sursa = os.path.join(wt, "frontend_test", "e2e", fis)
    if not os.path.exists(sursa) or ("def " + test.split("[")[0]) not in open(sursa, encoding="utf-8").read():
        return None, "testul probei de mediu nu mai există: %s" % nume
    return nume, None


def ruleaza_proba_mediu(wt, J, env, py="./venv/bin/python"):
    """Proba de mediu [17.5-T, T.6]: un singur test e2e scurt din plasa fixă, rulat cu scripts/e2e_poarta.py --doar=<fișier>::<test>. -> (ok, tip, mesaj, durata, nume):
    `tip` = «aserțiune» (raport junit cu <failure> pentru testul ei) sau «conexiune» (cod nenul fără raport junit sau ieșirea 3) sau «lipsă» (fișierul probei sau testul lipsesc)."""
    nume, motiv = proba_mediu_nume(wt)
    if nume is None:
        return False, "lipsă", motiv, 0.0, "?"
    jx = os.path.join(J, "poarta_proba_mediu.xml")
    _sterge(jx)
    rc, d = _rulare([py, "scripts/e2e_poarta.py", "--doar=" + nume, os.path.join(J, "e2e_proba_mediu_capturi")], wt, dict(env, PYTEST_ADDOPTS="--junitxml=" + jx), os.path.join(J, "poarta_proba_mediu.log"))
    if rc == 0:
        return True, "", "", d, nume
    pica = [t for t in citeste_junit(jx, wt) if t["rezultat"] == "pica"]
    if pica and rc != 3:
        mesaj = (pica[0]["mesaj"].splitlines() or [""])[0].strip()
        return False, "aserțiune", mesaj, d, nume
    try:
        ultima = [ln for ln in open(os.path.join(J, "poarta_proba_mediu.log"), errors="replace").read().splitlines() if ln.strip()][-1].strip()
    except (OSError, IndexError):
        ultima = "cod %d fără ieșire" % rc
    return False, "conexiune", ultima, d, nume


def ruleaza_trepte(wt, J, lot=None, pytest_ids=None, e2e_fisiere=None, procese="3", detalii="", verificator=True, sonda_8019=None, opreste_8019=None, dupa_treapta=None):
    """-> (durate pe treaptă, teste). `pytest_ids`/`e2e_fisiere` None = tot (nucleul / manifestul); listă = numai acelea (reluarea). Baza de test se restaurează înainte de
    pytest și înainte de plasa e2e (niciodată per test). Toate treptele rulează, și după una roșie.
    [16.7] Xml-ul unei trepte se șterge înainte de ea, iar un cod nenul fără raport junit proaspăt e o picătură de infrastructură (`<treapta>::sesiune`; [17.5-U] treapta e `infra`, nu `rosu_<cod>`).
    [17.5-U, U.1] Înaintea plasei 8019 se eliberează prin `verificator_design.elibereaza_port` (un server al uneltelor se oprește, orice alt proces se refuză cu numele lui: treapta iese `infra` cu
    motivul «8019 ocupat de pid <N> (<comandă>)», plasa nu pornește); `sonda_8019` / `opreste_8019` date, sau `_sonda_8019` / `_opreste_8019` suprascrise (citite la apel), păstrează blocul vechi.
    [17.5-T, T.6] În faza poarta_plasa, după eliberarea portului și înaintea plasei, rulează proba de mediu (`ruleaza_proba_mediu`); proba căzută = treapta `infra` cu motivul «proba de mediu <fișier::test>:
    <primul rând al mesajului>» (aceeași cale ca eliberarea refuzată a portului), plasa nu pornește. Durata probei intră în durate sub cheia `proba_mediu`.
    [17.5-T, T.5] `dupa_treapta(faza, f)` e chemată după fiecare treaptă poarta_pytest / poarta_plasa (`f` = {id, rezultat, remasurare}); întoarce True = re-măsurează numai acea treaptă, o singură dată,
    cu rândurile ei obișnuite de jurnal, iar rezultatele re-măsurării le înlocuiesc pe ale primei; o probă de mediu căzută în re-măsurarea plasei = OprirePoarta."""
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
        for remasurare in (False, True):
            with faza(lot, "poarta_pytest", detalii) as f:
                _rulare(["sh", "scripts/baza_test.sh", "restaureaza"], wt, env, os.path.join(J, "poarta_restaurare_pytest.log"))
                jx = os.path.join(J, "poarta_pytest.xml")
                _sterge(jx)
                rc, d = _rulare([py, "-m", "pytest", "-q", "-n", procese, "--dist", "loadfile", "--junitxml=" + jx] + ids, wt, env, os.path.join(J, "poarta_pytest.log"))
                r = citeste_junit(jx, wt)
                f["rezultat"] = rezultat_treapta(rc, r)
            if not remasurare and dupa_treapta and dupa_treapta("poarta_pytest", f):
                continue
            break
        trepte["pytest"] = d
        teste += [dict(t, treapta="pytest") for t in r]
        if rc != 0 and not r:   # fără raport junit proaspăt (pytest n-a ajuns să ruleze nimic (interpretare, import, interrupt): infrastructură, nu test
            teste.append({"nume": "pytest::sesiune", "treapta": "pytest", "rezultat": "pica", "infra": True, "durata": d, "mesaj": "cod %d fără raport junit" % rc})
    fis = [os.path.basename(x) for x in fisiere_manifest(wt)] if e2e_fisiere is None else e2e_fisiere
    if fis:
        import verificator_design as VD
        for remasurare in (False, True):
            with faza(lot, "poarta_plasa", detalii) as f:
                _rulare(["sh", "scripts/baza_test.sh", "restaureaza"], wt, env, os.path.join(J, "poarta_restaurare_e2e.log"))
                jx = os.path.join(J, "poarta_e2e.xml")
                _sterge(jx)
                sonda, oprire = sonda_8019 or _sonda_8019, opreste_8019 or _opreste_8019   # citite la apel, nu legate la import
                ok_port, motiv_port = VD.elibereaza_port(8019, sonda=None if sonda is _SONDA_IMPLICITA else sonda, opreste_fn=None if oprire is _OPRESTE_IMPLICIT else oprire, lot=lot)
                tip_sesiune, dp = "", 0.0
                if ok_port:
                    ok_proba, tip_sesiune, mesaj_proba, dp, nume_proba = ruleaza_proba_mediu(wt, J, env, py)
                    trepte["proba_mediu"] = dp
                    if not ok_proba and remasurare:
                        f["rezultat"] = "stop"
                        raise OprirePoarta("proba de mediu căzută în re-măsurare: %s: %s" % (nume_proba, mesaj_proba))
                    if not ok_proba and tip_sesiune == "lipsă":   # fișierul probei lipsește sau numește un test care nu mai există: faza e roșie, cu motiv (nu infra: relansarea n-ar ajuta)
                        rc, d = 1, dp
                        r = [{"nume": "plasa_e2e::proba_mediu", "rezultat": "pica", "infra": False, "durata": dp, "mesaj": mesaj_proba}]
                        motiv_sesiune = ""
                    elif not ok_proba:
                        rc, d, r, motiv_sesiune = 3, dp, [], "proba de mediu %s: %s" % (nume_proba, mesaj_proba)
                    else:
                        rc, d = _rulare([py, "scripts/e2e_poarta.py"] + ["--doar=" + x for x in fis] + [os.path.join(J, "e2e_poarta_capturi")],
                                        wt, dict(env, PYTEST_ADDOPTS="--junitxml=" + jx), os.path.join(J, "poarta_e2e.log"))
                        d = round(d + dp, 1)
                        r = citeste_junit(jx, wt)
                        motiv_sesiune = "cod %d fără raport junit" % rc
                        tip_sesiune = ""
                else:
                    rc, d, r, motiv_sesiune = 3, 0.0, [], motiv_port
                f["rezultat"] = rezultat_treapta(rc, r)
            if not remasurare and dupa_treapta and dupa_treapta("poarta_plasa", f):
                continue
            break
        trepte["plasa_e2e"] = d
        teste += [dict(t, treapta="plasa_e2e") for t in r]
        if rc != 0 and not r:   # fără raport junit proaspăt (3 = aplicația n-a pornit
            teste.append({"nume": "plasa_e2e::sesiune", "treapta": "plasa_e2e", "rezultat": "pica", "infra": True, "durata": d, "mesaj": motiv_sesiune, "tip": tip_sesiune})
    return trepte, teste
