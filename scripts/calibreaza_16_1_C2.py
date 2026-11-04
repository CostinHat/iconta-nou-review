# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_1_C2.py — calibrarea corecției 16.1-C2 pe ambele direcții (pct.0–4). Rulează pe un depozit TEMPORAR (git clone local al commitului curent și
depozite `git init` de probă), cu jurnal și cheie temporare; nu atinge depozitul lotului, configurația lui comună (core.hooksPath se scrie numai în configurația clonei) și nu
atinge ~/iconta_nou. Scrie docs/dovezi/16_1_C2/calibrare.txt: un rând pe caz, „ATINS” (comportamentul cerut) sau „RATAT”; ieșire 1 dacă un caz e ratat.
Datele sunt sintetice (se spune pe rând); codul judecat e cel din scripts/ și scripts/githooks/."""
import csv
import os
import shutil
import subprocess
import sys
import tempfile

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
RAD = os.path.dirname(AICI)
LOT = "16.1-C2"
REZ = []


def caz(nume, ok, detaliu=""):
    REZ.append((nume, ok, detaliu))
    print("%s  %s  %s" % ("ATINS" if ok else "RATAT", nume, detaliu))


def sh(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def g(d, *a):
    return sh(["git", *a], d)


def commit(d, nume, text, mesaj="x"):
    os.makedirs(os.path.dirname(os.path.join(d, nume)) or d, exist_ok=True)
    open(os.path.join(d, nume), "w").write(text)
    g(d, "add", nume)
    g(d, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", mesaj)
    return g(d, "rev-parse", "HEAD").stdout.strip()


def depozit_nou(tmp, nume):
    d = os.path.join(tmp, nume)
    sh(["git", "init", "-q", "-b", "main", d], tmp)
    g(d, "config", "user.email", "c@c")
    g(d, "config", "user.name", "c")
    return d


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.0 — hook-urile (reference-transaction, pre-push) pe un clone local, cu depozit la distanță temporar
# ---------------------------------------------------------------------------------------------------------------------------------------------
def hook_uri(tmp):
    cl = os.path.join(tmp, "clona")
    sh(["git", "clone", "-q", "--no-hardlinks", RAD, cl], tmp)
    for k, v in (("user.email", "c@c"), ("user.name", "c")):
        g(cl, "config", k, v)
    base = g(cl, "rev-parse", "origin/main").stdout.strip()
    g(cl, "update-ref", "refs/heads/main", base)
    g(cl, "checkout", "-q", "-b", "lot", base)
    c = commit(cl, "scripts/probă_c2.txt", "C\n", "C")
    dov = "docs/dovezi/16_1_C2/"
    head_csv = commit(cl, dov + "jurnal_verificare.csv", "lot,commit\n16.1-C2,%s\n" % c, "CSV")
    g(cl, "checkout", "-q", "-b", "lot_claude", c)
    head_claude = commit(cl, "CLAUDE.md", "schimbat după C\n", "CLAUDE.md după C")
    g(cl, "checkout", "-q", "-b", "lot_cap", c)
    head_cap = commit(cl, dov + "capturi/nota.txt", "nu e png\n", "fișier non-png în capturi")
    g(cl, "checkout", "-q", "-b", "lot_alt", c)
    head_alt = commit(cl, dov + "jurnal_verificare.csv", "lot,commit\n", "alt HEAD")
    g(cl, "checkout", "-q", "lot")
    g(cl, "config", "core.hooksPath", os.path.join(RAD, "scripts", "githooks"))   # numai în configurația clonei
    comun = os.path.join(cl, ".git")
    jv, jp = os.path.join(comun, "poarta_verdicte.log"), os.path.join(comun, "publica_verdicte.log")

    def scrie(verde_pe=None, pass_pe=None, c_in_pass=None):
        open(jv, "w").write(("VERDE %s lot x manifest=m completa lot=%s\n" % (verde_pe, LOT)) if verde_pe else "")
        open(jp, "w").write(("PASS %s %s 2026-11-04T22:00:00+02:00 C=%s fisiere=x\n" % (pass_pe, LOT, c_in_pass or c)) if pass_pe else "")

    def main_la(sha):
        g(cl, "-c", "core.hooksPath=/dev/null", "update-ref", "refs/heads/main", sha)

    def mutare(head):
        main_la(base)
        return g(cl, "update-ref", "refs/heads/main", head)

    def impinge(head):
        bare = tempfile.mkdtemp(dir=tmp)
        sh(["git", "init", "-q", "--bare", bare], tmp)
        return g(cl, "push", bare, "%s:refs/heads/main" % head)
    msg = lambda r: (r.stderr.strip().splitlines() or ["-"])[-1][:100]   # noqa: E731
    scrie(c, head_csv)
    r = mutare(head_csv)
    caz("0 PASS pe HEAD (care numește C) + VERDE pe C, HEAD = C + rând CSV: reference-transaction lasă main să se mute", r.returncode == 0, msg(r))
    r = impinge(head_csv)
    caz("0 același caz: pre-push lasă push-ul pe main să treacă", r.returncode == 0, msg(r))
    scrie(c, None)
    r = mutare(head_csv)
    caz("0 VERDE pe C fără PASS pe HEAD: reference-transaction refuză", r.returncode != 0 and "PASS" in r.stderr, msg(r))
    r = impinge(head_csv)
    caz("0 VERDE pe C fără PASS pe HEAD: pre-push refuză", r.returncode != 0 and "REFUZAT" in r.stderr, msg(r))
    scrie(c, head_alt)
    r = mutare(head_csv)
    caz("0 PASS pe alt HEAD (VERDE pe C): reference-transaction refuză", r.returncode != 0 and "PASS" in r.stderr, msg(r))
    r = impinge(head_csv)
    caz("0 PASS pe alt HEAD (VERDE pe C): pre-push refuză", r.returncode != 0 and "REFUZAT" in r.stderr, msg(r))
    scrie(c, head_claude)
    r = mutare(head_claude)
    caz("4(d) HEAD care diferă de C prin CLAUDE.md, cu PASS și VERDE pe C: reference-transaction refuză", r.returncode != 0 and "CLAUDE.md" in r.stderr, msg(r))
    r = impinge(head_claude)
    caz("4(d) același caz: pre-push refuză", r.returncode != 0 and "REFUZAT" in r.stderr, msg(r))
    scrie(c, head_cap)
    r = mutare(head_cap)
    caz("4(f) fișier non-.png sub docs/dovezi/<lot>/capturi/ în diff-ul C..HEAD: reference-transaction refuză", r.returncode != 0 and "capturi/nota.txt" in r.stderr, msg(r))
    scrie(head_csv, head_csv)
    r = mutare(head_csv)
    caz("0 VERDE exact pe HEAD + PASS pe HEAD (fără C diferit) rămâne acceptat", r.returncode == 0, msg(r))
    # C inexistent / necurat: PASS care numește un C fără VERDE
    scrie("0" * 40, head_csv)
    r = mutare(head_csv)
    caz("0 PASS pe HEAD care numește un C fără VERDE în jurnalul porții: refuză", r.returncode != 0, msg(r))


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.1 — manifestul poate crește numai cu fișiere de test noi
# ---------------------------------------------------------------------------------------------------------------------------------------------
def manifest(tmp):
    import poarta_lib as L
    d = depozit_nou(tmp, "man")
    antet = "# manifest de probă\n"
    rand = lambda f, h="a" * 64, n=3: "%s\t%s\t%d\tpython -m pytest -q %s\n" % (f, h, n, f)   # noqa: E731
    commit(d, "frontend_test/e2e/e2e_vechi.py", "def test_a():\n    assert 1\n")
    commit(d, "frontend_test/e2e/e2e_pe_main.py", "def test_b():\n    assert 1\n")
    baza = commit(d, L.MANIFEST, antet + rand("frontend_test/e2e/e2e_vechi.py"), "baza")
    g(d, "checkout", "-q", "-b", "lot")
    f_nou = "frontend_test/e2e/e2e_pilot_f001.py"
    commit(d, f_nou, "def test_n():\n    assert 1\n")
    cal = os.path.join(d, L.MANIFEST)
    man = antet + rand("frontend_test/e2e/e2e_vechi.py")
    open(cal, "w").write(man + rand(f_nou, "b" * 64, 2))
    r = L.manifest_refuzuri(d, baza)
    caz("1 rând adăugat pentru un fișier de test nou (în diff, absent pe main) = trece", r == [], str(r))
    open(cal, "w").write(man + rand("frontend_test/e2e/e2e_pe_main.py", "c" * 64, 1))
    r = L.manifest_refuzuri(d, baza)
    caz("1 rând adăugat pentru un fișier existent pe main = refuz cu numele lui", len(r) == 1 and "e2e_pe_main.py" in r[0] and "existent pe main" in r[0], str(r))
    open(cal, "w").write(antet + rand("frontend_test/e2e/e2e_vechi.py", "a" * 64, 4))
    r = L.manifest_refuzuri(d, baza)
    caz("1 rând modificat (numărul de teste al unui fișier existent) = refuz cu numele lui", len(r) == 1 and "e2e_vechi.py" in r[0] and "modificat" in r[0], str(r))
    open(cal, "w").write(antet + rand("frontend_test/e2e/e2e_vechi.py", "d" * 64, 3))
    r = L.manifest_refuzuri(d, baza)
    caz("1 rând modificat (hash-ul) = refuz cu numele lui", len(r) == 1 and "e2e_vechi.py" in r[0], str(r))
    open(cal, "w").write(antet)
    r = L.manifest_refuzuri(d, baza)
    caz("1 rând lipsă = refuz cu numele lui", len(r) == 1 and "e2e_vechi.py" in r[0] and "lipsă" in r[0], str(r))
    open(cal, "w").write(man + rand("frontend_test/e2e/e2e_fantoma.py", "e" * 64, 1))
    r = L.manifest_refuzuri(d, baza)
    caz("1 rând adăugat pentru un fișier care nu e în diff-ul lotului = refuz cu numele lui", len(r) == 1 and "e2e_fantoma.py" in r[0] and "diff" in r[0], str(r))


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.2 — pornirea cu proveniență; pct.3 — jurnalul verificării și rundele
# ---------------------------------------------------------------------------------------------------------------------------------------------
def pornire(tmp):
    import jurnal_lot as JL
    import publica_lot as PL
    jur = os.path.join(tmp, "j.log")
    cheie = os.path.join(tmp, "cheie.txt")
    open(cheie, "w").write("cheie-de-proba-sintetica\n")
    env = dict(os.environ, LOT_JURNAL=jur, CHEIE_COADA=cheie)
    os.environ["LOT_JURNAL"], os.environ["CHEIE_COADA"] = jur, cheie
    pr = os.path.join(tmp, "praguri.txt")
    open(pr, "w").write("produs\n")
    jd = depozit_nou(tmp, "jp")   # depozit de probă: `pornire-coada` fixează lotul curent în configurația comună a depozitului în care rulează
    commit(jd, "a.txt", "a\n")
    rc = sh([sys.executable, os.path.join(AICI, "jurnal_lot.py"), "pornire-coada", "99.9", pr, cheie, "comanda_x.txt"], jd, env).returncode
    rows = [r for r in JL._citeste(jur) if r[1] == "pornire" and r[2] == "inceput"]
    caz("2 coada scrie rândul „pornire” cu marcaj (coada=1 marca=<hash>), ora reală și hash-ul pragurilor", rc == 0 and len(rows) == 1 and "coada=1 marca=" in rows[0][8] and "praguri_sha256=" in rows[0][8], rows[0][8][:70] if rows else "-")
    caz("2 marcajul se recalculează din cheie + lot + ora rândului = valid", bool(rows) and JL.marca_valida(rows[0], "99.9"))
    fals = list(rows[0])
    fals[8] = fals[8].replace("marca=", "marca=0")[:-1]
    caz("2 rând cu marcaj falsificat = nevalid", not JL.marca_valida(fals, "99.9"))
    fals2 = list(rows[0])
    fals2[3] = "2026-01-01T00:00:00+02:00"
    caz("2 rând cu ora schimbată după scriere = nevalid", not JL.marca_valida(fals2, "99.9"))
    os.environ["CHEIE_COADA"] = os.path.join(tmp, "alta_cheie.txt")
    open(os.environ["CHEIE_COADA"], "w").write("alta\n")
    caz("2 aceeași linie cu altă cheie = nevalid (marcajul nu se poate pune fără cheia cozii)", not JL.marca_valida(rows[0], "99.9"))
    os.environ["CHEIE_COADA"] = cheie
    recon = ["99.9", "pornire", "inceput", "x", "s", "-", "i", "1", "praguri=p praguri_sha256=h reconstituit ora_reala=x"]
    nemarcat = ["99.9", "pornire", "inceput", "x", "s", "-", "i", "1", "praguri=p praguri_sha256=h"]
    caz("2 lot de produs cu rând de pornire cu marcaj valid, unul singur = acceptat", PL.pornire_stop([rows[0]], "99.9", False) == [])
    caz("2 lot de produs fără rând „pornire” = STOP „lipsă pornire”", PL.pornire_stop([], "99.9", False) == ["lipsă pornire"])
    caz("2 lot de produs cu pornire fără marcaj (comandă lipită direct în prompt) = STOP", len(PL.pornire_stop([nemarcat], "99.9", False)) == 1)
    caz("2 lot de produs cu pornire reconstituită = STOP", "nu e „unelte”" in " ".join(PL.pornire_stop([recon], "99.9", False)))
    caz("2 lot „unelte” cu o singură pornire reconstituită = acceptat", PL.pornire_stop([recon], "99.9", True) == [])
    caz("2 lot „unelte” cu pornire reconstituită și alt rând „pornire” = STOP", len(PL.pornire_stop([recon, rows[0]], "99.9", True)) == 1)
    caz("2 doi rânduri „pornire” valide într-un lot de produs = STOP (unul singur)", len(PL.pornire_stop([rows[0], rows[0]], "99.9", False)) == 1)
    os.environ.pop("LOT_JURNAL")
    os.environ.pop("CHEIE_COADA")


def csv_si_runde(tmp):
    import publica_lot as PL
    cap = os.path.join(tmp, "cap.png")
    open(cap, "wb").write(b"x")
    C, ALT, BAZA = "c" * 40, "a" * 40, "b" * 40

    def r(sha, pas="P1", verdict="trece", ver="scripts/verifica_pas.py v1", captura=None):
        return dict(lot=LOT, commit=sha, verificator=ver, inceput="", sfarsit="", pas=pas, actiune="x", verdict=verdict, captura=captura or cap, motiv="")
    caz("3(e) rând pe alt sha decât C, cu verdict „pica”, ignorat; rândul pe C „trece” = trece", PL.jurnal_verificare_stop([r(ALT, verdict="pica"), r(C)], ["P1"], C, BAZA, 0) == [])
    s = PL.jurnal_verificare_stop([r(ALT, verdict="trece")], ["P1"], C, BAZA, 0)
    caz("3 pas fără rând pe C (rândul e pe alt sha) = STOP „nu are rând pe C”", len(s) == 1 and "nu are rând pe C" in s[0], str(s))
    s = PL.jurnal_verificare_stop([r(C, verdict="pica")], ["P1"], C, BAZA, 0)
    caz("3 rând pe C cu verdict „pica” = STOP", any("pica" in x for x in s), str(s))
    s = PL.jurnal_verificare_stop([r(C, captura=os.path.join(tmp, "lipsa.png"))], ["P1"], C, BAZA, 0)
    caz("3 rând pe C cu captură lipsă = STOP", any("captura lipsește" in x for x in s), str(s))
    haiku = lambda sha, pas="P1": r(sha, pas, ver="Haiku 4.5")   # noqa: E731
    s = PL.jurnal_verificare_stop([r(C), haiku(BAZA), haiku(C)], ["P1"], C, BAZA, 1)
    caz("3 runde: parcurgerea „înainte” pe commitul de bază nu e rundă (o rundă pe C, maxim 1) = trece", s == [], str(s))
    s = PL.jurnal_verificare_stop([r(C), haiku(ALT), haiku(C)], ["P1"], C, BAZA, 1)
    caz("3 runde: două sha distincte cu Haiku pe pașii „după” (maxim 1) = STOP", len(s) == 1 and "rundele" in s[0], str(s))
    s = PL.jurnal_verificare_stop([r(C), haiku(C)], ["P1"], C, BAZA, 0)
    caz("3 runde: cheie lipsă (maxim 0) și un rând Haiku = STOP (lot fără verificator)", len(s) == 1 and "rundele" in s[0], str(s))
    # citirea cheii din praguri pe un fișier real
    pr = os.path.join(RAD, "scripts", "praguri_16_1_C2.txt")
    import re
    mx = [int(m.group(1)) for ln in open(pr, encoding="utf-8") for m in [re.search(r"runde_verificator_max:\s*(\d+)", ln)] if m]
    caz("3 scripts/praguri_16_1_C2.txt declară runde_verificator_max: 0", mx == [0], str(mx))
    # CSV real al lotului: structura
    cv = os.path.join(RAD, "docs", "dovezi", "16_1_C2", "jurnal_verificare.csv")
    if os.path.exists(cv):
        rr = list(csv.DictReader(open(cv, encoding="utf-8")))
        caz("3 jurnal_verificare.csv al lotului are rândul P1", any(x["pas"] == "P1" for x in rr), "%d rânduri" % len(rr))


def strabun(tmp):
    """pct.4 direct pe funcția `ancestor_refuzuri` (aceeași funcție ca în hook-uri), pe un depozit de probă."""
    import publica_lot as PL
    d = depozit_nou(tmp, "str")
    c = commit(d, "a.txt", "a\n")
    dov = "docs/dovezi/16_1_C2/"
    PL.DEP = d
    try:
        h1 = commit(d, "CLAUDE.md", "x\n")
        ref, _ = PL.ancestor_refuzuri(c, h1, "16_1_C2")
        caz("4 CLAUDE.md nu mai e în lista căilor permise după C", len(ref) == 1 and "CLAUDE.md" in ref[0], str(ref))
        g(d, "reset", "-q", "--hard", c)
        h2 = commit(d, dov + "capturi/p.png", "png\n")
        ref, _ = PL.ancestor_refuzuri(c, h2, "16_1_C2")
        caz("4 captură .png sub capturi/ = permisă", ref == [], str(ref))
        g(d, "reset", "-q", "--hard", c)
        h3 = commit(d, dov + "capturi/p.txt", "txt\n")
        ref, _ = PL.ancestor_refuzuri(c, h3, "16_1_C2")
        caz("4(f) fișier non-.png sub capturi/ = refuz cu numele lui", len(ref) == 1 and "p.txt" in ref[0], str(ref))
        g(d, "reset", "-q", "--hard", c)
        h4 = commit(d, dov + "jurnal_verificare.csv", "a\nb\n")
        ref, _ = PL.ancestor_refuzuri(c, h4, "16_1_C2")
        caz("4 jurnal_verificare.csv adăugat = permis", ref == [], str(ref))
    finally:
        PL.DEP = None


def main():
    tmp = tempfile.mkdtemp(prefix="calibrare_16_1_C2_")
    try:
        hook_uri(tmp)
        manifest(tmp)
        pornire(tmp)
        csv_si_runde(tmp)
        strabun(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    iesire = os.path.join(RAD, "docs", "dovezi", "16_1_C2", "calibrare.txt")
    os.makedirs(os.path.dirname(iesire), exist_ok=True)
    open(iesire, "w", encoding="utf-8").write("\n".join("%s  %s  %s" % ("ATINS" if ok else "RATAT", n, d) for n, ok, d in REZ) + "\n")
    return 0 if all(ok for _, ok, _ in REZ) else 1


if __name__ == "__main__":
    sys.exit(main())
