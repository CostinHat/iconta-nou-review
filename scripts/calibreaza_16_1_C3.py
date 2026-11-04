# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_1_C3.py — calibrarea corecției 16.1-C3 pe ambele direcții (pct.1–7). NU e o rulare a porții (nu consumă contorul rulărilor): folosește `publica_lot.py --proba`,
funcțiile pure ale scripturilor, scripturile apelate direct și iconta_test sub lacăt (baza_test.sh salveaza cu BAZA_TEST_DIR într-un director de probă, niciodată snapshotul),
niciodată poarta_lot.sh fără --baza. Depozite temporare (`git init` / clone local) cu jurnal și cheie temporare. Scrie docs/dovezi/16_1_C3/calibrare.txt: un rând pe caz,
„ATINS” (comportamentul cerut) sau „RATAT”; ieșire 1 dacă un caz e ratat. Datele sunt sintetice (se spune pe rând).
  calibreaza_16_1_C3.py <parte>...   părți: oracol, proba, incheie, clase, lacat, f017, productie, lansator (fără argument: toate, în ordinea asta)"""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
RAD = os.path.dirname(AICI)
LOT = "16.1-C3"
REZ = []
PY = os.path.join(RAD, "venv", "bin", "python")


def caz(nume, ok, detaliu=""):
    REZ.append((nume, ok, detaliu))
    print("%s  %s  %s" % ("ATINS" if ok else "RATAT", nume, str(detaliu).replace("\n", " ")[:220]))


def sh(cmd, cwd=None, env=None, inp=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, input=inp)


def g(d, *a):
    return sh(["git", *a], d)


def depozit_nou(tmp, nume):
    d = os.path.join(tmp, nume)
    sh(["git", "init", "-q", "-b", "main", d], tmp)
    g(d, "config", "user.email", "c@c")
    g(d, "config", "user.name", "c")
    return d


def commit(d, fisiere, mesaj="x", hooks=False):
    for nume, text in fisiere.items():
        os.makedirs(os.path.dirname(os.path.join(d, nume)) or d, exist_ok=True)
        open(os.path.join(d, nume), "w").write(text) if isinstance(text, str) else open(os.path.join(d, nume), "wb").write(text)
        g(d, "add", nume)
    g(d, *([] if hooks else ["-c", "core.hooksPath=/dev/null"]), "commit", "-q", "-m", mesaj)
    return g(d, "rev-parse", "HEAD").stdout.strip()


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.1 — oracolul pașilor
# ---------------------------------------------------------------------------------------------------------------------------------------------
def oracol(tmp):
    import oracol_pasi as OP
    import publica_lot as PL
    import verifica_pas as VP
    import poarta_lib as L
    import jurnal_lot as JL
    # 14 cazuri: fiecare operator pe un caz care trece și unul care pică (observatul e sintetic)
    cazuri = [("egal", "1210.00", 1210.0, "trece"), ("egal", "1210.00", 1209.99, "pica"), ("contine", "F1A", "Factura F1A 18", "trece"), ("contine", "F1A", "Factura 18", "pica"),
              ("nr_randuri", "2", [1, 2], "trece"), ("nr_randuri", "2", [1], "pica"), ("lipseste", "incasata", "neincasata", "pica"), ("lipseste", "incasata", "deschisa", "trece"),
              ("interval_px", "43-45", [43, 44.5], "trece"), ("interval_px", "43-45", [43, 47], "pica"), ("activ", "true", True, "trece"), ("activ", "true", False, "pica"),
              ("text_contine", "CHF1", "Chitanta CHF1 nr 2", "trece"), ("text_contine", "CHF1", "Chitanta F2C", "pica")]
    # „lipseste incasata” pe „neincasata”: fragmentul apare în text => pică (comparația e pe fragment, fără altă interpretare)
    for op, val, obs, asteptat in cazuri:
        v, m = VP.compara_asertiune(op, val, obs)
        caz("1 verifica_pas: operator %s, valoare %r, observat %r => %s" % (op, val, obs, asteptat), v == asteptat, "%s %s" % (v, m))
    txt = open(os.path.expanduser("~/ghid_incoming/pasi_16_2.txt"), encoding="utf-8").read()   # fișierul real al arhitectului pentru 16.2 (citit, nu modificat)
    arh, erori = OP.parseaza(txt)
    caz("1 pasi_16_2.txt (arhitect) se parsează fără erori, toți operatorii definiți", not erori and len(arh) > 0, "%d aserțiuni, erori=%s" % (len(arh), erori))
    corect = {"asertiuni": [{"id": a["id"], "operator": a["operator"], "valoare": a["valoare"], "cheie": "k." + a["id"]} for a in arh]}
    caz("1 pasi.json cu operatori și valori copiate literal = trece", OP.refuzuri(txt, corect) == [], OP.refuzuri(txt, corect)[:2])
    for nume, mod in (("valoare schimbată", lambda d: d["asertiuni"][3].update(valoare="9999")), ("operator schimbat", lambda d: d["asertiuni"][3].update(operator="contine")),
                      ("aserțiune lipsă", lambda d: d["asertiuni"].pop(3)), ("aserțiune în plus", lambda d: d["asertiuni"].append({"id": "z.9", "operator": "egal", "valoare": "1", "cheie": "x"}))):
        d = json.loads(json.dumps(corect))
        mod(d)
        r = OP.refuzuri(txt, d)
        caz("1 pasi.json: %s = refuz cu aserțiunea numită" % nume, bool(r) and ("z.9" in r[0] if "plus" in nume else arh[3]["id"] in r[0]), r[:1])
    # fișierul arhitectului modificat după pornire: rândul „pornire” scris de coadă (jurnal_lot.pornire_coada) cu hash-ul lui
    ghid = os.path.join(tmp, "ghid")
    os.makedirs(ghid)
    open(os.path.join(ghid, "pasi_PROBA_C3.txt"), "w", encoding="utf-8").write(txt)
    open(os.path.join(ghid, "praguri_PROBA_C3.txt"), "w").write("unelte\n")
    open(os.path.join(ghid, "cheie_coada.txt"), "w").write("cheie-de-proba\n")
    os.environ["LOT_JURNAL"] = os.path.join(tmp, "jurnal_oracol.log")
    JL.pornire_coada("PROBA-C3", os.path.join(ghid, "praguri_PROBA_C3.txt"), os.path.join(ghid, "cheie_coada.txt"), "comanda_PROBA_C3.txt")
    pornire = [r for r in JL._citeste(JL.cale_jurnal()) if r[0] == "PROBA-C3" and r[1] == "pornire" and r[2] == "inceput"][-1]
    caz("1 coada scrie în „pornire” hash-ul pasi_<lot>.txt al arhitectului", "pasi_sha256=%s" % L.hash_fisier(os.path.join(ghid, "pasi_PROBA_C3.txt")) in pornire[8], pornire[8][:140])
    rad = os.path.join(tmp, "rad_oracol")
    os.makedirs(os.path.join(rad, "docs", "dovezi", "PROBA_C3"))
    json.dump(corect, open(os.path.join(rad, "docs", "dovezi", "PROBA_C3", "pasi.json"), "w"))
    os.environ["GHID_INCOMING"] = ghid
    caz("1 publica_lot: fișierul nemodificat + pasi.json copiat literal = fără STOP", PL.oracol_stop("PROBA_C3", True, pornire, rad) == [], PL.oracol_stop("PROBA_C3", True, pornire, rad)[:2])
    d = json.loads(json.dumps(corect))
    d["asertiuni"][5]["valoare"] = "x"
    json.dump(d, open(os.path.join(rad, "docs", "dovezi", "PROBA_C3", "pasi.json"), "w"))
    r = PL.oracol_stop("PROBA_C3", True, pornire, rad)
    caz("1 publica_lot: o valoare schimbată în pasi.json = STOP „oracol modificat” cu aserțiunea numită", bool(r) and r[0].startswith("oracol modificat") and arh[5]["id"] in r[0], r[:1])
    json.dump(corect, open(os.path.join(rad, "docs", "dovezi", "PROBA_C3", "pasi.json"), "w"))
    open(os.path.join(ghid, "pasi_PROBA_C3.txt"), "a", encoding="utf-8").write("\nz.1 | z | ecran | egal | 1 | adăugat după pornire | proba\n")
    r = PL.oracol_stop("PROBA_C3", True, pornire, rad)
    caz("1 publica_lot: fișierul arhitectului modificat după pornire = STOP „oracol modificat” (hash diferit)", bool(r) and "hash" in r[0], r[:1])
    os.remove(os.path.join(ghid, "pasi_PROBA_C3.txt"))
    r = PL.oracol_stop("PROBA_C3", True, pornire, rad)
    caz("1 publica_lot: fișierul arhitectului dispărut după pornire = STOP", bool(r), r[:1])
    pornire_fara = list(pornire)
    pornire_fara[8] = "praguri=x"
    caz("1 lot de unelte fără fișier al arhitectului = fără oracol (fără STOP)", PL.oracol_stop("PROBA_C3", True, pornire_fara, rad) == [], "")
    caz("1 lot de produs fără fișier al arhitectului = STOP", bool(PL.oracol_stop("PROBA_C3", False, pornire_fara, rad)), PL.oracol_stop("PROBA_C3", False, pornire_fara, rad)[:1])
    del os.environ["GHID_INCOMING"]
    del os.environ["LOT_JURNAL"]


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.3 — contractul la început (--proba) și declanșatorul din post-commit
# ---------------------------------------------------------------------------------------------------------------------------------------------
def proba(tmp):
    import publica_lot as PL
    lot, lotf = "PROBA-C3", "PROBA_C3"
    d = depozit_nou(tmp, "p3")
    base = commit(d, {"a.txt": "baza\n"}, "baza")
    g(d, "checkout", "-q", "-b", "lucru/proba")
    cap = "docs/dovezi/%s/capturi/%s_P1.png" % (lotf, lotf)
    antet = "lot,commit,verificator,inceput,sfarsit,pas,actiune,verdict,captura,motiv\n"

    def randuri(sha, captura, verdict="trece"):
        return antet + "%s,%s,v,2026-11-04T10:00:00+02:00,2026-11-04T10:00:01+02:00,P1,a,%s,%s,\n" % (lot, sha, verdict, captura)
    fis = {"docs/dovezi/%s/pasi.txt" % lotf: "P1\n"}
    c1 = commit(d, dict(fis, **{cap: b"\x89PNG", "docs/dovezi/%s/jurnal_verificare.csv" % lotf: randuri(base, cap)}), "primul commit")
    caz("3 rând corect pe sha-ul bazei, cu captură = trece", PL.proba_refuzuri(d, lot) == [], PL.proba_refuzuri(d, lot))
    c2 = commit(d, {"docs/dovezi/%s/jurnal_verificare.csv" % lotf: randuri(base, "docs/dovezi/%s/capturi/lipsa.png" % lotf)}, "fără captură")
    r = PL.proba_refuzuri(d, lot)
    caz("3 rând fără captură = refuz", bool(r) and "lipsește" in r[0], r)
    commit(d, {"docs/dovezi/%s/jurnal_verificare.csv" % lotf: randuri(c1, cap)}, "alt sha (primul commit al lotului)")
    r = PL.proba_refuzuri(d, lot)
    caz("3 rând pe orice alt sha (nici baza, nici C) = refuz, cu sha-urile numite", bool(r) and "nu pe commitul de bază" in r[0], r)
    commit(d, {"docs/dovezi/%s/jurnal_verificare.csv" % lotf: randuri(base, cap, "pica")}, "verdict pică")
    r = PL.proba_refuzuri(d, lot)
    caz("3 rând pe baza cu verdict „pica” = refuz", bool(r) and "pica" in r[0], r)
    rows = [[lot, "proba_contract", "inceput", "t", "s", "-", "1", "1", ""], [lot, "proba_contract", "sfarsit", "t", "s", "verde", "1", "1", ""]]
    caz("3 lot cu faza „proba_contract” verde = fără STOP", PL.proba_stop(rows, lot) == [], "")
    caz("3 lot fără fază „proba_contract” = STOP", bool(PL.proba_stop([], lot)), PL.proba_stop([], lot))
    rows[1][5] = "rosu"
    caz("3 lot cu „proba_contract” roșie = STOP", bool(PL.proba_stop(rows, lot)), PL.proba_stop(rows, lot))
    # declanșatorul: hook-ul post-commit REAL, într-un clone cu scripts/ copiat, la primul commit al unei ramuri lucru/*; fără rând pe baza lotului => faza „rosu”; cu rând => „verde”
    for nume_caz, cu_rand in (("rând pe baza lotului", True), ("fără rând", False)):
        cl = depozit_nou(tmp, "hook_" + str(cu_rand))
        shutil.copytree(os.path.join(RAD, "scripts"), os.path.join(cl, "scripts"), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        os.symlink(os.path.join(RAD, "venv"), os.path.join(cl, "venv"))
        open(os.path.join(cl, ".gitignore"), "w").write("venv\n__pycache__/\n")
        b = commit(cl, {".gitignore": "venv\n__pycache__/\n", "x.txt": "x\n"}, "baza")
        g(cl, "checkout", "-q", "-b", "lucru/proba2")
        jur = os.path.join(tmp, "jurnal_hook_%s.log" % cu_rand)
        env = dict(os.environ, LOT=lot, LOT_JURNAL=jur)
        g(cl, "config", "core.hooksPath", "scripts/githooks")
        f2 = {"docs/dovezi/%s/pasi.txt" % lotf: "P1\n"}
        if cu_rand:
            f2.update({cap: b"\x89PNG", "docs/dovezi/%s/jurnal_verificare.csv" % lotf: randuri(b, cap)})
        for n, t in f2.items():
            os.makedirs(os.path.dirname(os.path.join(cl, n)), exist_ok=True)
            open(os.path.join(cl, n), "wb" if isinstance(t, bytes) else "w").write(t)
            g(cl, "add", n)
        r = sh(["git", "-c", "core.hooksPath=scripts/githooks", "commit", "-q", "-m", "primul commit", "--no-verify"], cl, env)
        faza = [ln.split("\t") for ln in open(jur, encoding="utf-8")] if os.path.exists(jur) else []
        sf = [x for x in faza if x[1] == "proba_contract" and x[2] == "sfarsit"]
        caz("3 post-commit (hook) la primul commit pe lucru/*: %s => faza „proba_contract” %s" % (nume_caz, "verde" if cu_rand else "rosu"),
            bool(sf) and sf[-1][5] == ("verde" if cu_rand else "rosu"), (sf[-1][5] if sf else "fără fază") + " | " + (r.stdout + r.stderr).strip()[-120:])
        if cu_rand:   # al doilea commit: hook-ul nu mai rulează contractul (numai la primul)
            n_inainte = len(faza)
            commit(cl, {"y.txt": "y\n"}, "al doilea", hooks=False)
            sh(["git", "-c", "core.hooksPath=scripts/githooks", "commit", "-q", "--allow-empty", "-m", "al doilea commit", "--no-verify"], cl, env)
            faza2 = [ln for ln in open(jur, encoding="utf-8")]
            caz("3 post-commit: la al doilea commit nu mai scrie faza „proba_contract”", len(faza2) == n_inainte, "%d -> %d rânduri" % (n_inainte, len(faza2)))


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.4 — incheie_lot.sh
# ---------------------------------------------------------------------------------------------------------------------------------------------
def incheie(tmp):
    d = os.path.join(tmp, "oprit")
    os.makedirs(d)
    env = dict(os.environ, OPRIT_DIR=d)
    r = sh(["sh", os.path.join(AICI, "incheie_lot.sh"), "PROBA-C3", "publicat", "abc123"], env=env)
    f = os.path.join(d, "OPRIT_PROBA-C3.txt")
    t = open(f, encoding="utf-8").read().strip() if os.path.exists(f) else ""
    caz("4 incheie_lot.sh PROBA-C3 publicat => OPRIT_PROBA-C3.txt cu rândul corect", bool(re.fullmatch(r"OPRIT — gata: PROBA-C3 publicat abc123 \d{4}-\d\d-\d\dT\S+", t)), t)
    r = sh(["sh", os.path.join(AICI, "incheie_lot.sh"), "PROBA-C3b", "ghicit"], env=env)
    caz("4 stare nevalidă = refuz, niciun fișier scris", r.returncode == 2 and not os.path.exists(os.path.join(d, "OPRIT_PROBA-C3b.txt")), r.stdout.strip())
    r = sh(["sh", os.path.join(AICI, "incheie_lot.sh"), "../x", "publicat"], env=env)
    caz("4 număr de lot nevalid = refuz, niciun fișier scris", r.returncode == 2 and not os.path.exists(os.path.join(d, "..", "OPRIT_x.txt")) and os.listdir(d) == ["OPRIT_PROBA-C3.txt"], r.stdout.strip())
    r = sh(["sh", os.path.join(AICI, "incheie_lot.sh"), "PROBA-C3", "nepublicat"], env=env)
    t2 = open(f, encoding="utf-8").read().strip()
    caz("4 apelat din nou, fișierul se rescrie atomic (o singură linie, starea nouă)", r.returncode == 0 and t2.count("\n") == 0 and " nepublicat " in t2, t2)


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.5 — clasele inventarului = clasele porții
# ---------------------------------------------------------------------------------------------------------------------------------------------
def clase(tmp):
    import poarta_clasifica as C
    import poarta_lib as L
    caz("5 maparea a/b/c -> restanță, d/f -> nu există în poartă, e -> invalid", C.CLASE_INVENTAR == {"a": "restanta", "b": "restanta", "c": "restanta", "d": None, "e": "invalid", "f": None}, C.CLASE_INVENTAR)
    inv = [(1, ["R901", "e2e_proba_invalid.py::test_a", "e", "-", "x", "m"]), (2, ["R902", "e2e_proba_res.py::test_b", "b", "-", "x", "m"])]
    man_p = os.path.join(tmp, "manifest_proba.txt")
    open(man_p, "w").write("# probă\nfrontend_test/e2e/e2e_proba_invalid.py\tabc\t1\tcmd\n")
    r = C.manifest_invalide(man_p, inv)
    caz("5 test invalid (clasa e) pus într-un manifest de probă = refuz cu numele fișierului", bool(r) and "e2e_proba_invalid.py" in r[0], r)
    man_ok = os.path.join(tmp, "manifest_ok.txt")
    open(man_ok, "w").write("# probă\nfrontend_test/e2e/e2e_proba_res.py\tabc\t1\tcmd\n")
    caz("5 același test invalid în afara manifestului: manifestul rămâne curat (nu refuză)", C.manifest_invalide(man_ok, inv) == [], "")
    cand = [{"nume": "e2e_proba_invalid.py::test_a", "rezultat": "trece"}]
    rez = C.clasifica(cand, cand, set(), RAD, False, inv={}, inv_e={("e2e_proba_invalid.py", "test_a"): "R901"})
    caz("5 un test cu rând „e” care rulează = invalid în clasificare", any("R901" in x for x in rez["invalid"]), rez["invalid"])
    rez = C.clasifica([], [], set(), RAD, False, inv={}, inv_e={("e2e_proba_invalid.py", "test_a"): "R901"})
    caz("5 un test cu rând „e” care NU rulează (în afara manifestului) = nu apare nicăieri", not rez["invalid"], rez["invalid"])
    rez = C.clasifica([{"nume": "e2e_proba_res.py::test_b", "rezultat": "pica"}], [{"nume": "e2e_proba_res.py::test_b", "rezultat": "pica", "asertiuni": 0}], set(), RAD, False,
                      inv={("e2e_proba_res.py", "test_b"): "R902"}, inv_e={})
    caz("5 rând „b” care pică și pe bază = restanță numerotată (nu invalid, nu regresie)", rez["restanta"] and not rez["invalid"] and not rez["regresie"], rez["restanta"])
    caz("5 manifestul din repo nu conține teste invalide după inventarul din repo (cele 8 rânduri e sunt în afara lui)", C.manifest_invalide(os.path.join(RAD, L.MANIFEST)) == [], C.manifest_invalide(os.path.join(RAD, L.MANIFEST)))
    pinv = {("e2e_x.py", "test_r"): "R1"}
    t_res = [{"nume": "e2e_x.py::test_r", "rezultat": "pica", "infra": False}]
    caz("5 treaptă cu picături numai restanțe numerotate = „verde_cu_restante”", L.rezultat_treapta(1, t_res, pinv) == "verde_cu_restante", L.rezultat_treapta(1, t_res, pinv))
    caz("5 treaptă cu o picătură nenumerotată = „rosu_1”", L.rezultat_treapta(1, t_res + [{"nume": "e2e_x.py::test_n", "rezultat": "pica", "infra": False}], pinv) == "rosu_1", "")
    caz("5 treaptă cu infrastructură = „rosu_1”", L.rezultat_treapta(1, [{"nume": "e2e_x.py::test_r", "rezultat": "pica", "infra": True}], pinv) == "rosu_1", "")
    caz("5 treaptă fără picături (cod 0) = „verde”", L.rezultat_treapta(0, [], pinv) == "verde", "")
    sf = open(os.path.join(AICI, "jurnal_lot.py"), encoding="utf-8").read()
    caz("5 rândurile vechi ale jurnalului nu se rescriu (jurnalul se scrie numai prin adăugare, mod „a”)", 'open(cale, "a"' in sf and 'open(cale, "w"' not in sf, "")


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.2 — lacătul
# ---------------------------------------------------------------------------------------------------------------------------------------------
def _salveaza(env, tmp):
    e = dict(env, BAZA_TEST_DIR=os.path.join(tmp, "dump_proba"), PYTHON=PY)
    return sh(["sh", os.path.join(AICI, "baza_test.sh"), "salveaza"], RAD, e)


def lacat(tmp):
    import lacat_test as LT
    F = LT.FISIER
    veche = open(F).read() if os.path.exists(F) else None
    holder = os.path.join(tmp, "tine_lacatul.sh")
    open(holder, "w").write('#!/bin/sh\n. "%s/lacat_test.sh"\nlacat_test_ia "%s"\necho "tinut de $$" > "$1"\nif [ -n "$2" ]; then sh "%s/baza_test.sh" salveaza > "$3" 2>&1; echo "rc=$?" >> "$3"; else sleep 12; fi\n' % (AICI, AICI, AICI))
    env = dict(os.environ, BAZA_TEST_DIR=os.path.join(tmp, "dump_proba"), PYTHON=PY)
    try:
        if os.path.exists(F):
            os.remove(F)
        # 1. două porniri simultane: prima (stub care ține lacătul) rulează; a doua (baza_test.sh salveaza) refuză cu pid-ul primei
        sem = os.path.join(tmp, "sem1")
        p1 = subprocess.Popen(["sh", holder, sem, "", ""], env=env)
        for _ in range(50):
            if os.path.exists(sem):
                break
            time.sleep(0.1)
        r = _salveaza(env, tmp)
        caz("2 două porniri simultane: a doua (baza_test.sh salveaza) refuzată cu pid-ul primei", r.returncode == 1 and ("pid %d" % p1.pid) in r.stdout and "REFUZ" in r.stdout, r.stdout.strip())
        caz("2 a doua refuzată nu a scris niciun snapshot de probă", not os.path.exists(os.path.join(tmp, "dump_proba", "iconta_test.dump")), "")
        p1.wait()
        # 2. apel imbricat: scriptul pornit de procesul care ține lacătul (LACAT_TEST_PID) trece
        sem2, log2 = os.path.join(tmp, "sem2"), os.path.join(tmp, "log2")
        p2 = subprocess.Popen(["sh", holder, sem2, "imbricat", log2], env=env)
        p2.wait()
        t = open(log2).read()
        caz("2 apel imbricat (baza_test.sh salveaza pornit de deținătorul lacătului) = trece", "rc=0" in t and "salvat" in t, t.strip()[-120:])
        # 3. pid mort = preluat
        z = subprocess.Popen(["sleep", "0.1"])
        z.wait()
        open(F, "w").write("%d %s mort\n" % (z.pid, "1"))
        r = _salveaza(env, tmp)
        caz("2 pid mort în fișier = lacăt preluat (salveaza trece)", r.returncode == 0 and "salvat" in r.stdout, "pid %d mort; %s" % (z.pid, r.stdout.strip()[-80:]))
        # 4. pid refolosit (pid viu, altă oră de start) = preluat
        open(F, "w").write("%d %s refolosit\n" % (os.getpid(), "999999999"))
        r = _salveaza(env, tmp)
        caz("2 pid refolosit (viu, ora de start diferită) = lacăt preluat (salveaza trece)", r.returncode == 0 and "salvat" in r.stdout, "pid %d viu, ora de start falsă; %s" % (os.getpid(), r.stdout.strip()[-80:]))
        # 5. pid viu cu ora de start corectă (acest proces) = refuz
        open(F, "w").write("%d %s acest-proces\n" % (os.getpid(), LT.ora_start(os.getpid())))
        r = _salveaza(env, tmp)
        caz("2 pid viu cu ora de start coincidentă = refuz cu pid-ul lui", r.returncode == 1 and ("pid %d" % os.getpid()) in r.stdout, r.stdout.strip())
        # 6. baza_test.sh stare / verifica nu cer lacăt (citire)
        caz("2 poarta_lot.sh și lanseaza_verificator.py iau lacătul (cod)", all("lacat_test" in open(os.path.join(AICI, f)).read() for f in ("poarta_lot.sh", "lanseaza_verificator.py", "baza_test.sh")), "")
    finally:
        if veche is None:
            os.path.exists(F) and os.remove(F)
        else:
            open(F, "w").write(veche)


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.6 — rândurile F017 din baza_test.sh verifica
# ---------------------------------------------------------------------------------------------------------------------------------------------
def _verifica():
    r = sh(["sh", os.path.join(AICI, "baza_test.sh"), "verifica"], RAD, dict(os.environ, PYTHON=PY))
    ok = [ln for ln in r.stdout.splitlines() if "[verifica] OK" in ln]
    pica = [ln for ln in r.stdout.splitlines() if "[verifica] PICĂ" in ln]
    return ok, pica


def f017(tmp):
    import lacat_test as LT
    LT.ia(os.getpid(), "calibreaza_16_1_C3.py f017")
    env = dict(os.environ, LACAT_TEST_PID=str(os.getpid()), PYTHON=PY)
    r = sh(["sh", os.path.join(AICI, "baza_test.sh"), "restaureaza"], RAD, env)
    caz("6 baza restaurată (baza_test.sh restaureaza)", r.returncode == 0, r.stdout.strip()[-100:])
    ok, pica = _verifica()
    rand = [x for x in ok if any(k in x for k in ("F1A nr. 18", "F1A nr. 19", "seria de chitanță CHF1", "exact o chitanță", "F5", "DANTE"))]
    caz("6 pe baza restaurată toate rândurile F017 corectate TREC (%d rânduri OK)" % len(rand), len(rand) == 9 and not pica, "OK=%d PICĂ=%s" % (len(ok), pica))
    caz("6 rândurile vechi (nr. 15 / 500 / sold 2.000) au dispărut", not any("F1A nr. 15" in x or "sold preluat 2000" in x for x in ok + pica), "")
    sch = "tenant_9049"
    r = sh(["sh", "-c", 'set -a; . ~/.iconta/test.env; set +a; export PGPASSWORD="$DB_PASSWORD"; psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d iconta_test -Atq -c "'
            "INSERT INTO %s.chitante (serie, numar, data, factura_id, client_nume, client_cui, suma, reprezentand, anulata) SELECT 'CHF1', 2, '2026-11-03', id, 'Client Test SRL', '410001005', 1210.00, 'proba C3', false "
            "FROM %s.facturi WHERE numar='F1A18'\"" % (sch, sch)], RAD, env)
    caz("6 chitanță de probă pe nr. 18 inserată (pe iconta_test, sub lacăt, nu pe snapshot)", r.returncode == 0 and "INSERT" in (r.stdout + r.stderr) or r.returncode == 0, (r.stdout + r.stderr).strip()[-160:])
    ok2, pica2 = _verifica()
    caz("6 cu chitanța de probă pe nr. 18, rândul lui PICĂ", any("F1A nr. 18" in x for x in pica2), pica2[:2])
    caz("6 cu chitanța de probă, rândul lui nr. 19 TRECE (nu e atins)", any("F1A nr. 19" in x for x in ok2), "")
    r = sh(["sh", os.path.join(AICI, "baza_test.sh"), "restaureaza"], RAD, env)
    ok3, pica3 = _verifica()
    caz("6 după restaurare rândul nr. 18 TRECE din nou", any("F1A nr. 18" in x for x in ok3) and not pica3, "PICĂ=%s" % pica3)


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.7 — căile spre producție
# ---------------------------------------------------------------------------------------------------------------------------------------------
def productie(tmp):
    import lacat_test as LT
    LT.ia(os.getpid(), "calibreaza_16_1_C3.py productie")
    env = dict(os.environ, LACAT_TEST_PID=str(os.getpid()), PYTHON=PY)
    sh(["sh", os.path.join(AICI, "baza_test.sh"), "restaureaza"], RAD, env)
    sys.path.insert(0, RAD)
    from core import migrari_registru as MR
    from core import mediu_test as MT
    main_sha = g(RAD, "rev-parse", "main").stdout.strip()
    pas_ = os.path.join(tmp, "pass_ok.log")
    open(pas_, "w").write("PASS %s 16.1-C3 t C=%s fisiere=-\n" % (main_sha, main_sha))
    gol = os.path.join(tmp, "pass_gol.log")
    open(gol, "w").write("PASS %s 16.1-C3 t C=%s fisiere=-\n" % ("0" * 40, "0" * 40))
    # a) migrări: bază de probă = iconta_test (rolul de test nu are CONNECT pe iconta_v2), sub lacăt, restaurată după; nicio scriere în producție
    MT.CALE_DB_ENV = os.path.expanduser("~/.iconta/test.env")   # „producția” a acestui proces = iconta_test (monkeypatch în proces; fișierul real nu se atinge)
    cale = "core/migrare_proba_c3.py"   # migrare sintetică, creată numai pe durata calibrării (amprentă unică, ca rândul să se scrie): nu se comite
    open(os.path.join(RAD, cale), "w", encoding="utf-8").write('# probă 16.1-C3 %s\nif __name__ == "__main__":\n    pass\n' % time.time())
    import psycopg2
    dsn = MT.dsn_productie()
    assert MT.desface_dsn(dsn)["dbname"] == "iconta_test", "baza de probă nu e iconta_test"

    def randuri():
        c = psycopg2.connect(dsn)
        try:
            cur = c.cursor()
            cur.execute("SELECT to_regclass('public.migrari_rulate') IS NOT NULL")
            if not cur.fetchone()[0]:
                return 0
            cur.execute("SELECT count(*) FROM public.migrari_rulate WHERE fisier = %s", (cale,))
            return cur.fetchone()[0]
        finally:
            c.close()
    n0 = randuri()
    MR.PASS_LOG = gol
    rc = MR.main(["marcheaza", "--productie", cale, "calibrare C3"])
    caz("7 core.migrari_registru marcheaza --productie fără PASS pentru main = refuz (cod 1), nimic scris", rc == 1 and randuri() == n0, "rc=%s rânduri %d -> %d" % (rc, n0, randuri()))
    rc = MR.main(["ruleaza", "--productie", cale])
    caz("7 core.migrari_registru ruleaza --productie fără PASS = refuz, migrarea nu rulează", rc == 1 and randuri() == n0, "rc=%s" % rc)
    MR.PASS_LOG = os.path.join(tmp, "nu_exista.log")
    caz("7 jurnal de verdicte lipsă = refuz", MR.main(["marcheaza", "--productie", cale, "calibrare C3"]) == 1, "")
    MR.PASS_LOG = pas_
    rc = MR.main(["marcheaza", "--productie", cale, "calibrare C3"])
    caz("7 core.migrari_registru marcheaza --productie cu PASS pentru main = trece, rândul scris pe baza de probă", rc == 0 and randuri() == n0 + 1, "rc=%s rânduri %d -> %d" % (rc, n0, randuri()))
    MR.PASS_LOG = None
    caz("7 verifica (citire) nu cere PASS: cod diferit de refuzul PASS", MR.refuz_fara_pass(gol) is not None and "PASS" in MR.refuz_fara_pass(gol), "")
    # b) scripturile care scriu pe producție cu --productie
    for f in ("lot13_firme2_curata_731", "lot14_3_reclaseaza_117", "stoc2_409_1_dubluri_corectie", "stoc2_619_documente_pe_jumatate", "valideaza_note_interne_pfa"):
        r = sh([PY, "-c", "import sys; sys.path.insert(0, %r); from scripts.productie_pass import cere_pass; cere_pass(%r)" % (RAD, gol)], RAD)
        caz("7 scripts/%s.py --productie: cere_pass fără PASS = refuz" % f, r.returncode != 0 and "PASS" in (r.stdout + r.stderr), (r.stderr or r.stdout).strip()[-90:])
        caz("7 scripts/%s.py cheamă cere_pass înaintea citirii DSN-ului de producție" % f, open(os.path.join(AICI, f + ".py")).read().find("cere_pass()") < open(os.path.join(AICI, f + ".py")).read().find("dsn_productie()"), "")
    r = sh([PY, "-c", "import sys; sys.path.insert(0, %r); from scripts.productie_pass import cere_pass; cere_pass(%r); print('trece')" % (RAD, pas_)], RAD)
    caz("7 cere_pass cu PASS pentru main = trece", r.returncode == 0 and "trece" in r.stdout, r.stdout.strip() + r.stderr.strip()[-80:])
    # c) restartul: publica_prod.sh într-un depozit de probă (clone), RESTART_CMD = restartul serverului de lucru 8019 (nu producția)
    cl = os.path.join(tmp, "prod")
    sh(["git", "clone", "-q", "--no-hardlinks", RAD, cl], tmp)
    g(cl, "checkout", "-q", "-B", "main", "HEAD")
    bare = os.path.join(tmp, "origin.git")
    sh(["git", "init", "-q", "--bare", bare], tmp)
    g(cl, "remote", "set-url", "origin", bare)
    g(cl, "push", "-q", "origin", "main")
    os.makedirs(os.path.join(cl, "venv", "bin"), exist_ok=True)
    open(os.path.join(cl, "venv", "bin", "python"), "w").write("#!/bin/sh\nexit 0\n")   # stub: verificarea migrărilor și statica nu ating producția
    os.chmod(os.path.join(cl, "venv", "bin", "python"), 0o755)
    head = g(cl, "rev-parse", "HEAD").stdout.strip()
    marc = os.path.join(tmp, "restart_facut")
    sc_restart = os.path.join(tmp, "restart_proba.sh")
    open(sc_restart, "w").write("#!/bin/sh\necho repornit > %s\n" % marc)
    restart = "sh " + sc_restart
    pas_head = os.path.join(tmp, "pass_head.log")
    open(pas_head, "w").write("PASS %s 16.1-C3 t C=%s fisiere=-\n" % (head, head))
    e = dict(os.environ, PUBLICA_PROD_PASS_LOG=os.path.join(tmp, "pass_lipsa.log"), PUBLICA_PROD_RESTART=restart)
    r = sh(["sh", os.path.join(AICI, "publica_prod.sh")], cl, e)
    caz("7 publica_prod.sh (restart) fără PASS pentru HEAD = refuz (cod 1), restartul NU se execută", r.returncode == 1 and not os.path.exists(marc) and "PASS" in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-100:])
    open(os.path.join(tmp, "pass_alt.log"), "w").write("PASS %s 16.1-C3 t C=%s fisiere=-\n" % ("1" * 40, "1" * 40))
    r = sh(["sh", os.path.join(AICI, "publica_prod.sh")], cl, dict(e, PUBLICA_PROD_PASS_LOG=os.path.join(tmp, "pass_alt.log")))
    caz("7 publica_prod.sh cu PASS pe ALT sha = refuz, restartul NU se execută", r.returncode == 1 and not os.path.exists(marc), "")
    r = sh(["sh", os.path.join(AICI, "publica_prod.sh")], cl, dict(e, PUBLICA_PROD_PASS_LOG=pas_head))
    caz("7 publica_prod.sh (restart) cu PASS pentru HEAD = trece pasul de restart (se execută comanda de restart a serverului de lucru)", os.path.exists(marc), r.stdout.strip()[-200:])
    # d) restart real al serverului de lucru 8019 prin publica_prod.sh, cu PASS
    if os.path.exists(marc):
        os.remove(marc)
    sc8019 = os.path.join(tmp, "restart_8019.sh")
    open(sc8019, "w").write("#!/bin/sh\ncd %s || exit 1\n./venv/bin/python scripts/verificator_design.py opreste > /dev/null 2>&1\nsh scripts/porneste_8019.sh > /dev/null 2>&1\necho repornit > %s\n" % (RAD, marc))
    wt_restart = "sh " + sc8019
    r = sh(["sh", os.path.join(AICI, "publica_prod.sh")], cl, dict(e, PUBLICA_PROD_PASS_LOG=pas_head, PUBLICA_PROD_RESTART=wt_restart))
    import urllib.request
    try:
        viu = urllib.request.urlopen("http://127.0.0.1:8019/public/config", timeout=10).status == 200
    except Exception:  # noqa: BLE001
        viu = False
    caz("7 cu PASS, restartul pornit de publica_prod.sh repornește serverul de lucru 8019 (răspunde după restart)", os.path.exists(marc) and viu, "8019 viu=%s" % viu)
    sh([PY, "scripts/verificator_design.py", "opreste"], RAD)
    os.remove(os.path.join(RAD, cale))
    sh(["sh", os.path.join(AICI, "baza_test.sh"), "restaureaza"], RAD, env)   # baza de probă înapoi la snapshot
    # e) post-commit nu mai repornește nimic
    pc = open(os.path.join(AICI, "githooks", "post-commit")).read()
    cod = "\n".join(ln for ln in pc.splitlines() if not ln.lstrip().startswith("#"))
    caz("7 post-commit nu mai conține restartul producției (nici `systemctl`, nici four-way)", "systemctl" not in cod and "four-way" not in cod and "RESTART" not in cod, "")


def lansator(tmp):
    import lacat_test as LT
    scen = os.path.join(tmp, "scenariu.txt")
    open(scen, "w").write("Scenariu sintetic: deschide /public/config și verifică beta.\n")
    pasi_t = os.path.join(tmp, "pasi_PROBA.txt")
    open(pasi_t, "w").write("PASI PROBA — sintetic\nFormat: aserțiune | pas | ecran | operator | valoare | descriere | sursa\nP1 | P1 | config | egal | false | beta | proba\n")
    pasi_j = os.path.join(tmp, "pasi.json")
    json.dump({"asertiuni": [{"id": "P1", "operator": "egal", "valoare": "false", "cheie": "beta"}]}, open(pasi_j, "w"))
    stub = os.path.join(tmp, "claude_stub.sh")
    marca = os.path.join(tmp, "stub_apelat.txt")
    open(stub, "w").write('#!/bin/sh\npwd > "%s"\necho "$@" >> "%s"\nls -a >> "%s"\nenv | grep LACAT_TEST_PID >> "%s"\ncat > "%s.prompt"\necho TRECE\n' % (marca, marca, marca, marca, marca))
    os.chmod(stub, 0o755)
    F = LT.FISIER
    veche = open(F).read() if os.path.exists(F) else None
    try:
        if os.path.exists(F):
            os.remove(F)
        e = dict(os.environ, CLAUDE_BIN=stub)
        r = sh([PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", "PROBA", "--scenariu", scen, "--pasi-txt", pasi_t, "--pasi-json", pasi_j], RAD, e)
        t = open(marca).read() if os.path.exists(marca) else ""
        caz("2 lansator: pornește subagentul cu modelul Haiku 5.5", r.returncode == 0 and "--model claude-haiku-5-5" in t, t.splitlines()[1][:160] if t else r.stdout + r.stderr)
        caz("2 lansator: directorul de lucru al agentului nu e depozit git și nu e depozitul lotului", ".git" not in t.split() and not t.splitlines()[0].startswith(RAD), t.splitlines()[0] if t else "")
        caz("2 lansator: agentul primește numai Bash pe învelișul verifica.sh (celelalte unelte interzise)", "--allowedTools Bash(" in t and "verifica.sh:*" in t and "--disallowedTools Read Edit Write" in t, "")
        caz("2 lansator: a ținut lacătul și l-a pasat copilului (LACAT_TEST_PID)", "LACAT_TEST_PID=" in t, "")
        prompt = open(marca + ".prompt").read()
        caz("2 lansator: promptul conține scenariul, pașii arhitectului și instrucțiunea fixă", "Scenariu sintetic" in prompt and "PASI PROBA" in prompt and "Rulează scenariul de mai jos" in prompt and "diff" not in prompt.lower(), "")
        # lacăt ținut de altcineva = refuz fără să pornească agentul
        os.remove(marca)
        z = subprocess.Popen(["sleep", "5"])
        open(F, "w").write("%d %s altcineva\n" % (z.pid, LT.ora_start(z.pid)))
        r = sh([PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", "PROBA", "--scenariu", scen, "--pasi-txt", pasi_t, "--pasi-json", pasi_j], RAD, e)
        caz("2 lansator: lacăt ținut de alt proces = refuz cu pid-ul lui, agentul nu pornește", r.returncode == 1 and ("pid %d" % z.pid) in r.stdout and not os.path.exists(marca), r.stdout.strip())
        z.kill()
        os.remove(F)
        dif = os.path.join(tmp, "lot.diff")
        open(dif, "w").write("diff --git a b\n")
        r = sh([PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", "PROBA", "--scenariu", scen, "--pasi-txt", pasi_t, "--pasi-json", pasi_j, "--formate", dif], RAD, e)
        caz("2 lansator: un fișier .diff dat agentului = refuz (fără acces la diff)", r.returncode == 1 and "diff" in r.stdout and not os.path.exists(marca), r.stdout.strip())
    finally:
        if veche is None:
            os.path.exists(F) and os.remove(F)
        else:
            open(F, "w").write(veche)


PARTI = {"oracol": oracol, "proba": proba, "incheie": incheie, "clase": clase, "lacat": lacat, "f017": f017, "productie": productie, "lansator": lansator}


def main(a):
    parti = a or list(PARTI)
    tmp = tempfile.mkdtemp(prefix="calibrare_16_1_C3_")
    try:
        for p in parti:
            print("\n== %s ==" % p)
            PARTI[p](tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if os.path.exists(os.path.join(RAD, "core", "migrare_proba_c3.py")):
            os.remove(os.path.join(RAD, "core", "migrare_proba_c3.py"))
    out = os.path.join(RAD, "docs", "dovezi", "16_1_C3", "calibrare.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    mod = "a" if a and os.path.exists(out) else "w"
    with open(out, mod, encoding="utf-8") as f:
        for nume, ok, det in REZ:
            f.write("%s  %s  %s\n" % ("ATINS" if ok else "RATAT", nume, str(det).replace("\n", " ")[:200]))
    print("\n%d cazuri, %d ratate -> %s" % (len(REZ), sum(not ok for _, ok, _ in REZ), os.path.relpath(out, RAD)))
    return 1 if any(not ok for _, ok, _ in REZ) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
