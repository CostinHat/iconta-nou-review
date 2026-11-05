# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_3.py — calibrarea comenzii 16.3 pe ambele direcții (pct.0–5). NU e o rulare a porții: folosește funcțiile pure ale scripturilor, `publica_lot.py --verifica/--controleaza`, depozite temporare
(`git init`), jurnal și cheie temporare, un browser Playwright pe pagini locale (fără 8019) și, la părțile „reale”, iconta_test sub lacătul lui lanseaza_verificator.py. Scrie docs/dovezi/16_3/calibrare.txt: un rând pe caz,
„ATINS” (comportamentul cerut) sau „RATAT”; ieșire 1 dacă un caz e ratat. Datele sunt sintetice (se spune pe rând).
  calibreaza_16_3.py <parte>...   părți: unelte, oracol, controleaza, lansator (fără iconta_test și 8019), apoi „reale” (sub lacăt, pe 8019): stub, citire (fără argument: primele patru).
  CALIB_ADAUGA=1 adaugă rândurile la docs/dovezi/16_3/calibrare.txt în loc să-l rescrie."""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
RAD = os.path.dirname(AICI)
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


def commit(d, fisiere, mesaj="x"):
    for nume, text in fisiere.items():
        os.makedirs(os.path.dirname(os.path.join(d, nume)) or d, exist_ok=True)
        open(os.path.join(d, nume), "wb" if isinstance(text, bytes) else "w").write(text)
        g(d, "add", nume)
    g(d, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", mesaj)
    return g(d, "rev-parse", "HEAD").stdout.strip()


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.0 — contractul pe lot de unelte; lista permisă
# ---------------------------------------------------------------------------------------------------------------------------------------------
def unelte(tmp):
    import publica_lot as PL
    import jurnal_lot as JL
    lot = "PROBA-163"
    lotf = "PROBA_163"
    jur = os.path.join(tmp, "jurnal_unelte.log")
    os.environ["LOT_JURNAL"] = jur
    # lot „unelte” de probă fără pasi.txt: faza „proba_contract” verde, eticheta „unelte, fără oracol”
    d = depozit_nou(tmp, "u1")
    commit(d, {"a.txt": "baza\n"}, "baza")
    g(d, "checkout", "-q", "-b", "lucru/proba")
    commit(d, {"scripts/praguri_%s.txt" % lotf: "unelte\nlot: %s\n" % lot}, "primul commit")
    caz("0 lot „unelte” fără pasi.txt: proba_refuzuri = fără refuz", PL.proba_refuzuri(d, lot) == [], PL.proba_refuzuri(d, lot))
    PL.RAD, PL.DEP = d, d
    rc = PL.main_proba(lot)
    sf = [r for r in JL._citeste(jur) if r[0] == lot and r[1] == "proba_contract" and r[2] == "sfarsit"]
    caz("0 lot „unelte” fără pasi.txt: --proba iese 0, faza „proba_contract | verde | unelte, fără oracol”", rc == 0 and bool(sf) and sf[-1][5] == "verde" and "unelte, fără oracol" in sf[-1][8],
        "rc=%s, %s" % (rc, sf[-1][5:9] if sf else "fără fază"))
    caz("0 proba_stop pe jurnalul acestui lot = fără STOP", PL.proba_stop([r for r in JL._citeste(jur) if len(r) > 8], lot) == [], "")
    # lot de produs (praguri fără „unelte”) fără rând a): roșu, ca până acum
    d2 = depozit_nou(tmp, "u2")
    commit(d2, {"a.txt": "baza\n"}, "baza")
    g(d2, "checkout", "-q", "-b", "lucru/proba")
    commit(d2, {"scripts/praguri_%s.txt" % lotf: "lot: %s\nruns\n" % lot, "docs/dovezi/%s/pasi.txt" % lotf: "P1\n"}, "primul commit")
    r = PL.proba_refuzuri(d2, lot)
    caz("0 lot de produs (fără „unelte”) cu pasi.txt și fără rândul a) = refuz", bool(r), r)
    d3 = depozit_nou(tmp, "u3")
    commit(d3, {"a.txt": "baza\n"}, "baza")
    g(d3, "checkout", "-q", "-b", "lucru/proba")
    commit(d3, {"scripts/praguri_%s.txt" % lotf: "lot: %s\n" % lot}, "primul commit")
    r = PL.proba_refuzuri(d3, lot)
    caz("0 lot de produs fără pasi.txt și fără rând a) = refuz (nu e scutit)", bool(r), r)
    PL.RAD, PL.DEP = RAD, None
    del os.environ["LOT_JURNAL"]
    # lista permisă: fișier din static/ în diff
    d4 = depozit_nou(tmp, "u4")
    commit(d4, {"a.txt": "baza\n"}, "baza")
    g(d4, "checkout", "-q", "-b", "lucru/proba")
    c1 = commit(d4, {"scripts/praguri_%s.txt" % lotf: "unelte\nlot: %s\n" % lot, "scripts/x.py": "x=1\n", "core/test_x.py": "def test_x(): pass\n", "docs/dovezi/%s/a.txt" % lotf: "a\n"}, "permise")
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c1, c1, lot], d4)
    caz("0 lot „unelte” cu scripts/, core/test_*.py și docs/dovezi/<lot>/ în diff = trece", r.returncode == 0, r.stdout.strip()[-200:])
    c2 = commit(d4, {"static/js/x.js": "var a;\n"}, "static")
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c2, c2, lot], d4)
    caz("0 lot „unelte” cu static/js/x.js în diff = STOP cu fișierul numit", r.returncode == 1 and "static/js/x.js" in r.stdout, r.stdout.strip()[-200:])
    for f in ("core/x.py", "templates/x.html", "frontend_test/e2e/e2e_x.py"):
        c3 = commit(d4, {f: "x\n"}, f)
        r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c3, c3, lot], d4)
        caz("0 lot „unelte” cu %s în diff = STOP cu fișierul numit" % f, r.returncode == 1 and f in r.stdout, r.stdout.strip()[-160:])
    c4 = commit(d4, {"scripts/praguri_%s.txt" % lotf: "unelte\nlot: %s\nstatic/js/x.js\ncore/x.py\ntemplates/x.html\nfrontend_test/e2e/e2e_x.py\n" % lot}, "numite în praguri")
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c4, c4, lot], d4)
    caz("0 aceleași fișiere numite în scripts/praguri_<lot>.txt = trece", r.returncode == 0, r.stdout.strip()[-200:])
    # un lot de produs nu are lista permisă a uneltelor (praguri fără „unelte”)
    d5 = depozit_nou(tmp, "u5")
    commit(d5, {"a.txt": "baza\n"}, "baza")
    g(d5, "checkout", "-q", "-b", "lucru/proba")
    c5 = commit(d5, {"scripts/praguri_%s.txt" % lotf: "lot: %s\nmax x 5\n" % lot, "static/js/x.js": "var a;\n"}, "produs")
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c5, c5, lot], d5)
    caz("0 lot de produs cu static/js/x.js în diff = trece (lista permisă e numai a uneltelor)", r.returncode == 0, r.stdout.strip()[-200:])


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.1 — oracolul prin parcurs: măsurile DOM, marcajul, importurile parcursului
# ---------------------------------------------------------------------------------------------------------------------------------------------
HTML = """<html><body style="margin:0"><div id="rand" style="display:flex;gap:8px;width:600px">
<button class="b" style="width:100px;height:40px">Adaugă</button><button class="b" style="width:120px;height:40px" disabled>Completează:</button><button class="b" aria-disabled="true" style="width:100px;height:44px">Gata</button></div>
<ul><li class="l">  unu   doi </li><li class="l">trei</li></ul><p id="lat" style="width:50px;overflow:hidden;white-space:nowrap">un text foarte lung care iese din casetă</p>
<button id="ok">Fine</button></body></html>"""


class PaginaFalsa:
    """Pagina sintetică a calibrării marcajului: evaluate întoarce valori date, screenshot scrie un fișier."""
    def __init__(self, valori):
        self.valori = valori

    def evaluate(self, js, arg=None):
        return self.valori.get(arg if not isinstance(arg, list) else tuple(arg))

    def screenshot(self, path):
        open(path, "wb").write(b"\x89PNG")

    def wait_for_timeout(self, ms):
        pass


def oracol(tmp):
    os.environ["CHEIE_ORACOL_FISIER"] = os.path.join(tmp, "cheie_oracol")
    import importlib
    import verifica_pas as VP
    importlib.reload(VP)
    import publica_lot as PL
    from playwright.sync_api import sync_playwright
    # măsurile DOM, pe o pagină locală: fiecare măsură, valoare care trece și una care pică (prin compara_asertiune)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 800, "height": 400})
        pg.set_content(HTML)
        ob = lambda cheie: VP.observa_pagina(pg, cheie, tmp)[1]   # noqa: E731
        cazuri = [
            ("text", "dom:.l|text", "egal", "unu doi,trei", "trece"), ("text", "dom:.l|text", "egal", "unu  doi,trei", "pica"),
            ("numar", "dom:.b|numar", "nr_randuri", "3", "trece"), ("numar", "dom:.b|numar", "nr_randuri", "2", "pica"),
            ("activ (primul activ)", "dom:.b:nth-child(1)|activ", "activ", "true", "trece"), ("activ (disabled)", "dom:.b:nth-child(2)|activ", "activ", "false", "trece"),
            ("activ (aria-disabled)", "dom:.b:nth-child(3)|activ", "activ", "false", "trece"), ("activ (disabled cerut true)", "dom:.b:nth-child(2)|activ", "activ", "true", "pica"),
            ("inaltime_px", "dom:.b|inaltime_px", "interval_px", "40-44", "trece"), ("inaltime_px", "dom:.b|inaltime_px", "interval_px", "40-41", "pica"),
            ("distanta_px", "dom:.b|distanta_px", "interval_px", "8-8", "trece"), ("distanta_px", "dom:.b|distanta_px", "interval_px", "10-12", "pica"),
            ("diferenta_latime_px", "dom:.b|diferenta_latime_px", "interval_px", "20-20", "trece"), ("diferenta_latime_px", "dom:.b|diferenta_latime_px", "interval_px", "0-5", "pica"),
            ("depasire", "dom:#lat|depasire", "egal", "1", "trece"), ("depasire", "dom:#ok|depasire", "egal", "1", "pica"),
            ("text pe un singur element", "dom:#ok|text", "contine", "Fine", "trece"), ("text pe un singur element", "dom:#ok|text", "contine", "Gata", "pica"),
        ]
        for nume, cheie, op, val, asteptat in cazuri:
            v, m = VP.compara_asertiune(op, val, ob(cheie))
            caz("1 măsura %s: %s %s %r pe %r => %s" % (nume, cheie, op, val, ob(cheie), asteptat), v == asteptat, "%s %s" % (v, m))
        try:
            VP.observa_pagina(pg, "dom:.b|culoare", tmp)
            caz("1 măsură necunoscută = refuz", False, "")
        except ValueError as e:
            caz("1 măsură necunoscută = refuz cu numele ei", "culoare" in str(e) or "dom:" in str(e), str(e)[:120])
        b.close()
    # json: din contextul paginii și pdf:fisier: (aceeași funcție de extragere ca pdf:<url>)
    pf = PaginaFalsa({"/x": {"a": {"b": [10, {"c": "558.46"}]}}})
    caz("1 json:<url>|<cale> cu cuib și index de listă", VP.citeste_cheia({"a": {"b": [10, {"c": "558.46"}]}}, "a.b.1.c") == (True, "558.46") and VP.citeste_cheia({"a": 1}, "a.z")[0] is False, "")
    from pypdf import PdfWriter  # noqa: F401  (pypdf e în venv; PDF-ul de probă se scrie cu reportlab dacă există, altfel se sare)
    try:
        from reportlab.pdfgen import canvas
        pdf = os.path.join(tmp, "dir_parc", "x.pdf")
        os.makedirs(os.path.dirname(pdf))
        c = canvas.Canvas(pdf)
        c.drawString(72, 720, "Chitanta CHF1 de la DANTE INTERNATIONAL SA")
        c.save()
        v, obs = VP.observa_pagina(pf, "pdf:fisier:x.pdf", os.path.dirname(pdf))
        caz("1 pdf:fisier: extrage textul PDF-ului descărcat", v and "DANTE INTERNATIONAL" in obs, obs[:60])
        try:
            VP.observa_pagina(pf, "pdf:fisier:../x.pdf", os.path.dirname(pdf))
            caz("1 pdf:fisier: în afara directorului parcurgerii = refuz", False, "")
        except ValueError as e:
            caz("1 pdf:fisier: în afara directorului parcurgerii = refuz", "în afara" in str(e), str(e)[:100])
    except ImportError:
        caz("1 pdf:fisier: (reportlab lipsește, PDF-ul se probează în rularea reală, p.1)", True, "sărit")
    # verifica_pagina cu pagină sintetică: rândurile, marcajul, cheia unică, nicio excepție pe „pica”
    pasi = os.path.join(tmp, "pasi.json")
    json.dump({"asertiuni": [{"id": "a.1", "pas": "a", "operator": "egal", "valoare": "558.46", "cheie": "json:/s|sold"},
                             {"id": "b.9", "pas": "b", "operator": "activ", "valoare": "false", "cheie": "dom:#ok|activ"}]}, open(pasi, "w"))
    pag = PaginaFalsa({"/s": {"sold": "558.46"}, ("#ok", "activ"): True})
    pag.evaluate = lambda js, arg=None: {"/s": {"sold": "558.46"}}.get(arg, True) if not isinstance(arg, list) else True   # noqa: E731
    os.environ["PARCURS_SHA"] = "a" * 40
    csv_ = os.path.join(tmp, "dovezi", "jurnal_cal.csv")
    rez, v = VP.verifica_pagina(pag, "PROBA-163", "a", "calib_x", "code", pasi, csv_)
    caz("1 verifica_pagina: pasul a (a.1 = 558.46) => trece, un rând, captura sub <parcurgere>/<verificator>/capturi/<lot>_<parcurgere>_<pas>_<sha8>.png",
        v == "trece" and rez == [("a.1", "trece", "")] and os.path.exists(os.path.join(tmp, "dovezi", "calib_x", "code", "capturi", "PROBA_163_calib_x_a.1_aaaaaaaa.png")), rez)
    rez, v = VP.verifica_pagina(pag, "PROBA-163", "b", "calib_x", "code", pasi, csv_)
    caz("1 verifica_pagina: pasul b (Adaugă activ, așteptat false) => pica, fără excepție; parcursul continuă", v == "pica" and rez[0][1] == "pica", rez)
    rez, v = VP.verifica_pagina(pag, "PROBA-163", "a", "calib_x", "code", pasi, csv_)
    caz("1 verifica_pagina: aceeași cheie (lot, parcurgere, pas, sha, verificator) a doua oară = neexecutat cu captura numită, nimic suprascris",
        v == "neexecutat" and "PROBA_163_calib_x_a.1_aaaaaaaa.png" in rez[0][2] and len(VP.randuri_csv(csv_)) == 2, rez)
    rr = VP.randuri_csv(csv_)
    caz("1 rândurile scrise de oracol au marcaj valid", all(VP.marcaj_valid(r) for r in rr), [r["marcaj"][:8] for r in rr])
    rr[0]["verdict"] = "pica"
    caz("1 un rând modificat de mână (verdict schimbat) are marcaj nevalid", not VP.marcaj_valid(rr[0]), "")
    fara = dict(rr[1], marcaj="")
    caz("1 un rând fără marcaj e nevalid", not VP.marcaj_valid(fara), "")
    csv_m = os.path.join(tmp, "dovezi", "jurnal_mana.csv")
    shutil.copy(csv_, csv_m)
    with open(csv_m, "a", encoding="utf-8", newline="") as f:
        csv.DictWriter(f, fieldnames=VP.CAMPURI, lineterminator="\n", restval="").writerow(
            {"lot": "PROBA-163", "commit": "b" * 40, "verificator": "code", "inceput": "t", "sfarsit": "t", "pas": "z.9", "actiune": "scris de mână", "verdict": "trece", "captura": os.path.relpath(csv_, RAD), "parcurgere": "calib_x"})
    # --verifica --csv: rândul scris de mână = refuz cu rândul numit (depozit temporar cu un singur commit)
    d = depozit_nou(tmp, "v1")
    commit(d, {"a.txt": "baza\n"}, "baza")
    g(d, "checkout", "-q", "-b", "lucru/proba")
    c1 = commit(d, {"b.txt": "b\n"}, "lot")
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c1, c1, "PROBA-163", "--csv", csv_m], d)
    caz("1 --verifica --csv: un rând scris de mână (fără marcaj) = refuz, rândul numit", r.returncode == 1 and "z.9" in r.stdout and "verdict în afara oracolului" in r.stdout, r.stdout.strip()[-220:])
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c1, c1, "PROBA-163", "--csv", csv_], d)
    caz("1 --verifica --csv: rândurile cu marcaj valid (scrise de oracol) = trece", r.returncode == 0, r.stdout.strip()[-200:])
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c1, c1, "16.1-C3", "--csv", csv_m], d)
    caz("1 --verifica --csv: lotul scutit (16.1-C3) cu rând fără marcaj = trece", r.returncode == 0, r.stdout.strip()[-200:])
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--csv", csv_], d)
    caz("1 „--csv” la publicare (fără --verifica) = refuz", r.returncode == 1 and "calibr" in r.stdout, r.stdout.strip()[-160:])
    # completarea coloanelor verificatorului independent re-marchează rândul; o editare de mână a coloanei o invalidează
    VP.completeaza_independent(csv_, "PROBA-163", "calib_x", "a" * 40, "code", "a.1", "corespunde")
    rr = VP.randuri_csv(csv_)
    caz("1 completeaza_independent: coloana se scrie, rândul rămâne cu marcaj valid", rr[0]["verificator_independent"] == "corespunde" and all(VP.marcaj_valid(r) for r in rr), "")
    # importurile parcursului
    import lanseaza_verificator as LV
    bun = os.path.join(tmp, "parcurs_bun.py")
    open(bun, "w").write("import os, re\nimport json\nfrom playwright.sync_api import Page\nimport verifica_pas as VP\n\ndef ruleaza(pagina, ctx):\n    pass\n")
    rau = os.path.join(tmp, "parcurs_rau.py")
    open(rau, "w").write("import os\nimport requests\nfrom core import auth_api\n\ndef ruleaza(pagina, ctx):\n    pass\n")
    caz("1 parcurs cu playwright, biblioteca standard și verifica_pas = importuri permise", LV.importuri_parcurs(bun)[1] == [], LV.importuri_parcurs(bun))
    nep = LV.importuri_parcurs(rau)[1]
    caz("1 parcurs cu alte importuri = refuz la lansare, cu numele modulului", nep == ["requests", "core"], nep)
    r = sh([PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", "PROBA-163", "--parcurs", rau, "--parcurgere", "x", "--verificator", "code", "--pasi-txt", bun, "--pasi-json", pasi, "--csv", csv_], RAD)
    caz("1 lansatorul refuză parcursul cu import nepermis (numele modulului în ieșire), fără să ia lacătul", r.returncode == 1 and "requests" in r.stdout and "core" in r.stdout, r.stdout.strip()[-200:])
    del os.environ["PARCURS_SHA"]
    del os.environ["CHEIE_ORACOL_FISIER"]


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.2 — controleaza: cheie + captură + marcaj, nu mtime
# ---------------------------------------------------------------------------------------------------------------------------------------------
def controleaza(tmp):
    os.environ["CHEIE_ORACOL_FISIER"] = os.path.join(tmp, "cheie_oracol2")
    import importlib
    import verifica_pas as VP
    importlib.reload(VP)
    pasi = os.path.join(tmp, "pasi2.json")
    json.dump({"asertiuni": [{"id": "a.1", "pas": "a", "operator": "egal", "valoare": "1", "cheie": "json:/s|v"}]}, open(pasi, "w"))
    pag = PaginaFalsa({})
    pag.evaluate = lambda js, arg=None: {"v": "1"}   # noqa: E731
    csv_ = os.path.join(tmp, "dov2", "jurnal.csv")
    for sha in ("1" * 40, "2" * 40):
        os.environ["PARCURS_SHA"] = sha
        VP.verifica_pagina(pag, "PROBA-163", "a", "calib_sha", "code", pasi, csv_)
    rr = VP.randuri_csv(csv_)
    caps = {r["captura"] for r in rr}
    caz("2 același pas pe două sha-uri: două rânduri, două capturi distincte", len(rr) == 2 and len(caps) == 2 and all(os.path.exists(c) for c in caps), sorted(os.path.basename(c) for c in caps))
    # mtime-ul capturii nu mai contează: îl mutăm cu o zi în urmă
    for c in caps:
        os.utime(c, (1, 1))
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--controleaza", csv_])
    caz("2 controleaza trece pe două rânduri ale aceluiași pas, deși mtime-ul capturilor e în afara intervalului", r.returncode == 0, r.stdout.strip())
    sh_ = sh(["sh", os.path.join(AICI, "jurnal_verificator.sh"), "controleaza", csv_], RAD)
    caz("2 jurnal_verificator.sh controleaza (calea scriptului) = trece", sh_.returncode == 0, sh_.stdout.strip())
    # aceeași cheie de două ori în fișier => refuz cu numele capturii
    dup = os.path.join(tmp, "dov2", "jurnal_dup.csv")
    shutil.copy(csv_, dup)
    linii = open(csv_, encoding="utf-8").read().splitlines()
    open(dup, "a", encoding="utf-8").write(linii[1] + "\n")
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--controleaza", dup])
    caz("2 aceeași cheie de două ori în CSV = refuz cu numele capturii", r.returncode == 1 and "repetată" in r.stdout and os.path.basename(rr[0]["captura"]) in r.stdout, r.stdout.strip()[-200:])
    # captura ștearsă => refuz cu rândul
    os.remove(rr[0]["captura"])
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--controleaza", csv_])
    caz("2 captura lipsă => refuz cu rândul numit", r.returncode == 1 and "a.1" in r.stdout and "lipsește" in r.stdout, r.stdout.strip()[-200:])
    # verifica_pas refuză aceeași cheie pe același sha
    rez, v = VP.verifica_pagina(pag, "PROBA-163", "a", "calib_sha", "code", pasi, csv_)
    caz("2 verifica_pagina pe aceeași cheie = nu suprascrie (neexecutat)", v == "neexecutat", rez)
    # subcomanda `pas` scoasă
    r = sh(["sh", os.path.join(AICI, "jurnal_verificator.sh"), "pas", "x"], RAD)
    caz("2 jurnal_verificator.sh pas = ieșirea „folosire: …” cu exit 2", r.returncode == 2 and r.stdout.startswith("folosire: jurnal_verificator.sh incepe|incheie|controleaza"), repr(r.stdout))
    # lotul scutit: rândurile vechi (16.1-C3) se judecă numai după existența capturii
    r = sh(["sh", os.path.join(AICI, "jurnal_verificator.sh"), "controleaza", os.path.join(RAD, "docs", "dovezi", "16_1_C3", "jurnal_verificare.csv")], RAD)
    caz("2 controleaza pe docs/dovezi/16_1_C3/jurnal_verificare.csv (rânduri scutite, fără marcaj) = trece", r.returncode == 0, r.stdout.strip())
    del os.environ["PARCURS_SHA"]
    del os.environ["CHEIE_ORACOL_FISIER"]


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.3 — verificatorul independent: regulile publicării pe rânduri sintetice; lansatorul cu stub
# ---------------------------------------------------------------------------------------------------------------------------------------------
STUB = r'''#!/usr/bin/env python3
import os, re, sys, json
prompt = sys.stdin.read()
mod = os.environ.get("STUB_MOD", "da")
ids = re.findall(r"ASERȚIUNEA (\S+) \|", prompt)
unica = len(ids) == 1 and "ASERȚIUNILE DE JUDECAT" not in prompt
open(os.environ["STUB_MARCA"], "a").write("%s | %s | %s\n" % (" ".join(sys.argv[1:]), "a doua" if unica else "prima", ",".join(ids)))
def raspuns(i):
    if mod == "nejudecabil":
        return "nejudecabil"
    if mod == "nu_nu" and i == "a.1":
        return "nu corespunde"
    if mod == "nu_da" and i == "a.1":
        return "corespunde" if unica else "nu corespunde"
    return "corespunde"
print(json.dumps([{"id": i, "raspuns": raspuns(i), "motiv": "stub"} for i in ids], ensure_ascii=False))
'''


def lansator(tmp):
    os.environ["CHEIE_ORACOL_FISIER"] = os.path.join(tmp, "cheie_oracol3")
    import importlib
    import verifica_pas as VP
    importlib.reload(VP)
    import publica_lot as PL
    sha = "c" * 40
    antet = VP.CAMPURI

    def rand(pas, verdict, i1, i2="", sha_=sha, parc="dupa"):
        r = {"lot": "PROBA-163", "commit": sha_, "verificator": "haiku", "inceput": "t", "sfarsit": "t", "pas": pas, "actiune": "x", "verdict": verdict, "captura": os.path.abspath(__file__), "motiv": "",
             "parcurgere": parc, "verificator_independent": i1, "verificator_independent_2": i2}
        r["marcaj"] = VP.marcaj_rand(r)
        return r
    stop = lambda rr: PL.csv_stop(rr, "PROBA-163", sha)   # noqa: E731
    caz("3 dezacord: oracol trece, ambele instanțe „nu corespunde” => STOP cu aserțiunea numită",
        any("dezacord oracol–verificator" in m and "a.1" in m for m in stop([rand("a.1", "trece", "nu corespunde", "nu corespunde"), rand("b.9", "pica", "corespunde")])), stop([rand("a.1", "trece", "nu corespunde", "nu corespunde"), rand("b.9", "pica", "corespunde")]))
    caz("3 prima „nu corespunde”, a doua „corespunde” => fără STOP", stop([rand("a.1", "trece", "nu corespunde", "corespunde"), rand("b.9", "pica", "corespunde")]) == [], stop([rand("a.1", "trece", "nu corespunde", "corespunde")]))
    caz("3 toate „corespunde” => fără STOP", stop([rand("a.1", "trece", "corespunde"), rand("b.9", "pica", "corespunde")]) == [], "")
    caz("3 toate „nejudecabil” => STOP „neefectuată”", any("neefectuată" in m for m in stop([rand("a.1", "trece", "nejudecabil"), rand("b.9", "trece", "nejudecabil")])), stop([rand("a.1", "trece", "nejudecabil")]))
    caz("3 o aserțiune „nejudecabil”, restul „corespunde” => fără STOP (numărul nejudecabilelor e măsurătoare)", stop([rand("a.1", "trece", "nejudecabil"), rand("b.9", "trece", "corespunde")]) == [], "")
    caz("3 fără răspuns al verificatorului pe o aserțiune => STOP", any("n-a răspuns" in m for m in stop([rand("a.1", "trece", "")])), "")
    caz("3 a doua instanță nu e rundă nouă: două rânduri cu a doua instanță, același sha și parcurgere = o rundă (runde_verificator_max 1 => fără STOP)",
        PL.jurnal_verificare_stop([dict(rand("a.1", "trece", "nu corespunde", "corespunde"), verificator="haiku"), dict(rand("b.9", "trece", "corespunde"), verificator="haiku")], [], sha, "d" * 40, 1) == [], "")
    caz("3 runde = sha și parcurgere: aceeași sha pe două parcurgeri Haiku = 2 runde (> max 1 => STOP)",
        any("rundele" in m for m in PL.jurnal_verificare_stop([rand("a.1", "trece", "corespunde", parc="haiku_1"), rand("a.1", "trece", "corespunde", parc="haiku_2")], [], sha, "d" * 40, 1)), "")
    caz("3 rând fără marcaj în jurnal => STOP „verdict în afara oracolului”", any("verdict în afara oracolului" in m for m in stop([dict(rand("a.1", "trece", "corespunde"), marcaj="")])), "")
    # regula descrierii: lot de produs cu «trece» în descriere = STOP; lot de unelte = trece
    import jurnal_lot as JL
    ghid = os.path.join(tmp, "ghid")
    os.makedirs(ghid)
    txt = "Antet\nFormat: x\na.1 | a | ecran | egal | 1 | soldul afisat; asteptat: trece | sursa\n"
    open(os.path.join(ghid, "pasi_PROBA_163.txt"), "w", encoding="utf-8").write(txt)
    os.environ["GHID_INCOMING"] = ghid
    pornire = ["PROBA-163", "pornire", "inceput", "t", "s", "-", "i", "p", "pasi_sha256=%s" % PL.L.hash_fisier(os.path.join(ghid, "pasi_PROBA_163.txt"))]
    rad = os.path.join(tmp, "rad3")
    os.makedirs(os.path.join(rad, "docs", "dovezi", "PROBA_163"))
    json.dump({"asertiuni": [{"id": "a.1", "operator": "egal", "valoare": "1", "cheie": "json:/s|v"}]}, open(os.path.join(rad, "docs", "dovezi", "PROBA_163", "pasi.json"), "w"))
    r = PL.oracol_stop("PROBA_163", False, pornire, rad)
    caz("3 lot de produs: «trece» în coloana descriere = STOP", bool(r) and "trece" in r[0], r[:1])
    r = PL.oracol_stop("PROBA_163", True, pornire, rad)
    caz("3 lot de unelte: «trece» în descriere (fișier de probă) = fără STOP", r == [], r)
    open(os.path.join(ghid, "pasi_PROBA_163.txt"), "w", encoding="utf-8").write(txt.replace("; asteptat: trece", ""))
    pornire[8] = "pasi_sha256=%s" % PL.L.hash_fisier(os.path.join(ghid, "pasi_PROBA_163.txt"))
    caz("3 lot de produs: descriere fără cuvinte de verdict = fără STOP", PL.oracol_stop("PROBA_163", False, pornire, rad) == [], PL.oracol_stop("PROBA_163", False, pornire, rad))
    del os.environ["GHID_INCOMING"]
    del os.environ["CHEIE_ORACOL_FISIER"]
    del antet


def _lanseaza(csv_, parcurgere, mod, marca, extra=(), fara_parcurs=False):
    e = dict(os.environ, CLAUDE_BIN=os.path.join(os.path.dirname(marca), "claude_stub"), STUB_MOD=mod, STUB_MARCA=marca, PARCURS_PASI="a")
    cmd = [PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", "16.3", "--parcurs", os.path.join(RAD, "docs", "dovezi", "16_3", "parcurs_proba_f017.py"), "--verificator", "haiku",
           "--pasi-txt", os.path.expanduser("~/ghid_incoming/pasi_16_3_proba.txt"), "--pasi-json", os.path.join(RAD, "docs", "dovezi", "16_3", "pasi.json"), "--csv", csv_, "--parcurgere", parcurgere,
           "--scenariu", os.path.expanduser("~/ghid_incoming/scenarii_pilot.txt"), "--sectiune", "F017"] + list(extra) + (["--fara-parcurs"] if fara_parcurs else [])
    return sh(cmd, RAD, e)


def stub(tmp):
    """CLAUDE_BIN înlocuit de un stub (pct.3): „nu corespunde” pe a.1 la ambele instanțe = STOP cu a.1 numită; „nu” la prima și „corespunde” la a doua = trece; „corespunde” pe toate = trece; „nejudecabil” pe toate =
    STOP „neefectuată”. Parcursul real rulează numai pasul a (PARCURS_PASI=a); rândurile sunt în jurnal_verificare_calibrare.csv, etichetele calib_stub_nu și calib_stub_da."""
    import verifica_pas as VP
    csv_ = os.path.join(RAD, "docs", "dovezi", "16_3", "jurnal_verificare_calibrare.csv")
    marca = os.path.join(tmp, "marca.txt")
    stub_ = os.path.join(tmp, "claude_stub")
    open(stub_, "w").write(STUB)
    os.chmod(stub_, 0o755)
    r = _lanseaza(csv_, "calib_stub_nu", "nu_nu", marca)
    caz("3 stub „nu corespunde” pe a.1 la ambele instanțe => STOP dezacord, a.1 numită, ieșire 1", r.returncode == 1 and "STOP dezacord oracol–verificator: a.1" in r.stdout, r.stdout.strip()[-260:])
    m = open(marca).read().splitlines()
    caz("3 stub: s-au pornit două instanțe (prima pe a.1, a doua numai pe a.1) cu modelul Haiku 5.5 și Read restrâns", len(m) == 2 and "prima" in m[0] and "a doua" in m[1] and "--model claude-haiku-5-5" in m[0] and "--tools Read" in m[0], m)
    rr = [x for x in VP.randuri_csv(csv_) if x["parcurgere"] == "calib_stub_nu"]
    caz("3 stub: ambele răspunsuri stau pe același rând (verificator_independent și verificator_independent_2), marcaj valid", len(rr) == 1 and rr[0]["verificator_independent"].startswith("nu corespunde") and rr[0]["verificator_independent_2"].startswith("nu corespunde") and VP.marcaj_valid(rr[0]), rr[0]["verificator_independent"] if rr else "")
    os.remove(marca)
    r = _lanseaza(csv_, "calib_stub_nu", "nu_da", marca, fara_parcurs=True)
    rr = [x for x in VP.randuri_csv(csv_) if x["parcurgere"] == "calib_stub_nu"]
    caz("3 stub „nu corespunde” la prima și „corespunde” la a doua => trece (ieșire 0), a doua instanță pe același rând", r.returncode == 0 and "STOP" not in r.stdout and rr[0]["verificator_independent"].startswith("nu corespunde") and rr[0]["verificator_independent_2"].startswith("corespunde"), r.stdout.strip()[-200:])
    os.remove(marca)
    r = _lanseaza(csv_, "calib_stub_nu", "nejudecabil", marca, fara_parcurs=True)
    caz("3 stub „nejudecabil” pe toate => STOP „neefectuată”, ieșire 1", r.returncode == 1 and "neefectuată" in r.stdout, r.stdout.strip()[-200:])
    os.remove(marca)
    r = _lanseaza(csv_, "calib_stub_da", "da", marca)
    rr = [x for x in VP.randuri_csv(csv_) if x["parcurgere"] == "calib_stub_da"]
    caz("3 stub „corespunde” pe toate => trece (ieșire 0), o singură instanță", r.returncode == 0 and len(open(marca).read().splitlines()) == 1 and rr[0]["verificator_independent"].startswith("corespunde") and not rr[0]["verificator_independent_2"], r.stdout.strip()[-200:])
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--controleaza", csv_])
    caz("3 jurnal_verificare_calibrare.csv după rulările cu stub: controleaza trece (capturi, chei unice, marcaje)", r.returncode == 0, r.stdout.strip()[-200:])
    r = sh([PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", "16.3", "--parcurs", os.path.join(RAD, "docs", "dovezi", "16_3", "parcurs_proba_f017.py"), "--verificator", "haiku", "--pasi-txt", os.path.expanduser("~/ghid_incoming/pasi_16_3_proba.txt"),
               "--pasi-json", os.path.join(RAD, "docs", "dovezi", "16_3", "pasi.json"), "--csv", csv_, "--parcurgere", "calib_fara_claude"], RAD, dict(os.environ, CLAUDE_BIN="", PATH="/usr/bin:/bin", HOME=tmp))
    caz("3 fără executabil `claude` (nici în PATH, nici în ~/.local/bin): „command not found” raportat, ieșire 127, fără stub", r.returncode == 127 and "command not found" in r.stdout, r.stdout.strip()[-160:])


def citire(tmp):
    """Read restrâns la directorul capturilor (pct.3): cu Claude real (Haiku 5.5), Read în director reușește, Read în afara lui e refuzat."""
    import lanseaza_verificator as LV
    binar = LV.caut_claude()
    dcap = os.path.join(tmp, "capturi_probe")
    os.makedirs(dcap)
    open(os.path.join(dcap, "cod.txt"), "w").write("CODUL-DIN-DIRECTOR-7431\n")
    afara = os.path.join(tmp, "afara.txt")
    open(afara, "w").write("CODUL-DIN-AFARA-9182\n")
    cmd = LV._comanda(binar, dcap)
    lucru = os.path.join(tmp, "lucru_agent")   # ca în lansator: directorul de lucru al agentului e altul decât al capturilor și decât al fișierului din afară
    os.makedirs(lucru)
    r1 = sh(cmd, lucru, inp="Citește cu Read fișierul %s și răspunde cu textul lui, nimic altceva." % os.path.join(dcap, "cod.txt"))
    caz("3 Read în directorul capturilor = permis (agentul citește fișierul)", "CODUL-DIN-DIRECTOR-7431" in r1.stdout, r1.stdout.strip()[-160:])
    r2 = sh(cmd, lucru, inp="Citește cu Read fișierul %s și răspunde cu textul lui; dacă nu poți, spune «REFUZAT» și motivul." % afara)
    caz("3 Read în afara directorului capturilor = refuz (conținutul nu apare în răspuns)", "CODUL-DIN-AFARA-9182" not in r2.stdout, r2.stdout.strip()[-200:])
    r3 = sh(cmd, lucru, inp="Rulează cu Bash comanda `echo BASH-RULAT` și răspunde cu ieșirea ei; dacă nu poți, spune «REFUZAT».")
    caz("3 alte unelte (Bash) nu sunt disponibile agentului", "BASH-RULAT" not in r3.stdout.replace("`echo BASH-RULAT`", ""), r3.stdout.strip()[-160:])


PARTI = {"unelte": unelte, "oracol": oracol, "controleaza": controleaza, "lansator": lansator, "stub": stub, "citire": citire}
PARTI_IMPLICITE = ["unelte", "oracol", "controleaza", "lansator"]


def main(a):
    parti = a or PARTI_IMPLICITE
    tmp = tempfile.mkdtemp(prefix="calibrare_16_3_")
    try:
        for p in parti:
            print("\n== %s ==" % p)
            PARTI[p](tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = os.path.join(RAD, "docs", "dovezi", "16_3", "calibrare.txt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    mod = "a" if os.environ.get("CALIB_ADAUGA") and os.path.exists(out) else "w"
    with open(out, mod, encoding="utf-8") as f:
        for nume, ok, det in REZ:
            f.write("%s  %s  %s\n" % ("ATINS" if ok else "RATAT", nume, str(det).replace("\n", " ")[:200]))
    print("\n%d cazuri, %d ratate -> %s" % (len(REZ), sum(not ok for _, ok, _ in REZ), os.path.relpath(out, RAD)))
    return 1 if any(not ok for _, ok, _ in REZ) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
