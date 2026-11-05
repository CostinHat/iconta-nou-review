# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_5.py — calibrarea comenzii 16.5 (C223, măsura „valoare” a oracolului). NU e o rulare a porții. Intrarea unică pentru pct.1 și pct.2; ieșire 1 la orice caz ratat.
  calibreaza_16_5.py pct1   cazurile (i)–(xiii) pe pagini de probă, testul pur roșu pe verifica_pas.py de la BAZA_COMMIT și verde pe cel nou, regresia părții oracol din calibreaza_16_3.py
                            (comparație pe stare + nume + număr de cazuri între regresie_inainte.txt și regresie_dupa.txt), comparatoarele probate pe perechi sintetice
  calibreaza_16_5.py pct2   lansatorul (--verificator code) pe parcursul real, apoi harta fixă a verdictelor pe jurnal_verificare_calibrare.csv (comparatorul hărții probat pe un CSV sintetic)
Refuză (ieșire 1) dacă `git show HEAD:scripts/verifica_pas.py` nu conține „valoare” sau dacă fișierele urmărite din scripts/ și core/ sunt modificate. Numără rândurile lot=16.5 din jurnalul comun
(~/iconta_nou/.lot_jurnal.log, citit direct) înainte și după fiecare parte: diferența trebuie să fie zero."""
import csv
import functools
import http.server
import os
import re
import subprocess
import sys
import tempfile
import threading

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
RAD = os.path.dirname(AICI)
LOT = "16.5"
BAZA_COMMIT = "2616e4cb"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_5")
CALIB = os.path.join(DOVEZI, "calibrare")
JURNAL_COMUN = os.path.join(os.path.expanduser("~"), "iconta_nou", ".lot_jurnal.log")
CSV_CALIB = os.path.join(CALIB, "jurnal_verificare_calibrare.csv")
#: harta fixă a pct.2: id aserțiune -> (verdict așteptat în CSV, text care trebuie să apară în motiv)
HARTA = {"inainte.1": ("trece", ""), "inainte_pica.1": ("pica", "2026-11-03"), "dupa_fill.1": ("trece", "")}
REZ = []

HTML = """<html><body>
<input id="d" value="2026-11-03">
<input id="gol">
<textarea id="t">primul rând
al doilea</textarea>
<select id="s"><option value="a">Prima</option><option value="b" selected>A doua</option></select>
<div id="dv">text în div</div>
<button id="b">Buton</button>
<input id="c" type="checkbox" checked>
<input class="p" value="unu"><input class="p" value="doi">
<span class="m"><input value="x"></span><span class="m">fără valoare</span>
</body></html>"""


def caz(nume, ok, detaliu=""):
    REZ.append((nume, ok, detaliu))
    print("%s  %s  %s" % ("ATINS" if ok else "RATAT", nume, str(detaliu).replace("\n", " ")[:220]))


def git(*a):
    return subprocess.run(["git", *a], cwd=RAD, capture_output=True, text=True).stdout


def randuri_lot_in_comun():
    return sum(1 for ln in open(JURNAL_COMUN, encoding="utf-8") if ln.split("\t")[0] == LOT)


def curat():
    """-> motivele de refuz: HEAD fără măsura „valoare” sau fișiere urmărite modificate în scripts/ și core/."""
    ref = []
    if "valoare" not in git("show", "HEAD:scripts/verifica_pas.py"):
        ref.append("HEAD:scripts/verifica_pas.py nu conține «valoare»")
    murdar = git("status", "--porcelain", "--untracked-files=no", "--", "scripts", "core").strip()
    if murdar:
        ref.append("fișiere urmărite modificate în scripts/ sau core/: " + murdar.replace("\n", "; "))
    return ref


# ---------------------------------------------------------------------------------------------------------------------------------------------
# comparatoarele (probate în ambele direcții)
# ---------------------------------------------------------------------------------------------------------------------------------------------
def linii_caz(text):
    """[(stare, nume)] din liniile de caz ale ieșirii calibreaza_16_3.py (încep cu ATINS / RATAT); detaliul (după ultimul dublu spațiu) nu se compară, iar căile /tmp și șirurile hex lungi se normalizează."""
    rez = []
    for ln in text.splitlines():
        m = re.match(r"(ATINS|RATAT)  (.*)$", ln)
        if m:
            nume = m.group(2).rsplit("  ", 1)[0] if "  " in m.group(2) else m.group(2)
            nume = re.sub(r"/tmp/\S+", "/tmp/X", nume)
            nume = re.sub(r"\b[0-9a-f]{8,}\b", "H", nume)
            rez.append((m.group(1), nume.strip()))
    return rez


def compara_regresie(inainte, dupa):
    """-> motivele diferenței: număr de cazuri, stare sau nume diferite, orice RATAT."""
    a, b = linii_caz(inainte), linii_caz(dupa)
    mot = []
    if len(a) != len(b):
        mot.append("număr de cazuri diferit: %d înainte, %d după" % (len(a), len(b)))
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            mot.append("cazul %d: %r înainte, %r după" % (i + 1, x, y))
    mot += ["RATAT %s: %s" % (nm, "înainte" if x is a else "după") for x in (a, b) for st, nm in x if st == "RATAT"]
    return mot


def compara_harta(randuri, sha):
    """-> motivele abaterii rândurilor CSV (dicționare) față de HARTA: exact o aserțiune pe id, numai cu commit = sha, verdict și motiv ca în hartă."""
    mot = [("rând pe alt sha: %s (%s)" % (r.get("pas"), (r.get("commit") or "")[:8])) for r in randuri if r.get("commit") != sha]
    pe = [r for r in randuri if r.get("commit") == sha]
    if len(pe) != len(HARTA):
        mot.append("%d rânduri pe %s în loc de %d" % (len(pe), sha[:8], len(HARTA)))
    for id_, (verdict, in_motiv) in HARTA.items():
        gasite = [r for r in pe if r.get("pas") == id_]
        if len(gasite) != 1:
            mot.append("%s: %d rânduri în loc de 1" % (id_, len(gasite)))
        elif gasite[0].get("verdict") != verdict:
            mot.append("%s: verdict %r în loc de %r" % (id_, gasite[0].get("verdict"), verdict))
        elif in_motiv and in_motiv not in (gasite[0].get("motiv") or ""):
            mot.append("%s: motivul %r nu conține %r" % (id_, gasite[0].get("motiv"), in_motiv))
    mot += ["id în plus: %s" % r.get("pas") for r in pe if r.get("pas") not in HARTA]
    return mot


def comparatoare():
    c1 = "ATINS  caz unu  detaliu x\nRATAT_nu  nu  e caz\nATINS  caz doi  \n"
    caz("comparator regresie: pereche identică (detalii diferite) = fără diferență", compara_regresie(c1, c1.replace("detaliu x", "alt detaliu")) == [], "")
    caz("comparator regresie: un caz lipsă = diferență", bool(compara_regresie(c1, "ATINS  caz unu  d\n")), "")
    caz("comparator regresie: un caz în plus = diferență", bool(compara_regresie(c1, c1 + "ATINS  caz trei  \n")), "")
    caz("comparator regresie: un RATAT = diferență", bool(compara_regresie(c1, c1.replace("ATINS  caz doi", "RATAT  caz doi"))), "")
    caz("comparator regresie: nume schimbat = diferență", bool(compara_regresie(c1, c1.replace("caz doi", "caz două"))), "")
    sha = "a" * 40
    bun = [{"pas": "inainte.1", "commit": sha, "verdict": "trece", "motiv": ""}, {"pas": "inainte_pica.1", "commit": sha, "verdict": "pica", "motiv": "găsit '2026-11-03', așteptat '2026-11-04'"},
           {"pas": "dupa_fill.1", "commit": sha, "verdict": "trece", "motiv": ""}]
    caz("comparator hartă: verdictele corecte = ieșire 0", compara_harta(bun, sha) == [], compara_harta(bun, sha))
    rau = [dict(r) for r in bun]
    rau[0]["verdict"] = "pica"
    m = compara_harta(rau, sha)
    caz("comparator hartă: inainte.1 «pică» = ieșire 1 cu pasul numit", bool(m) and "inainte.1" in m[0], m)
    rau = [dict(r) for r in bun]
    rau[1]["verdict"] = "trece"
    caz("comparator hartă: inainte_pica.1 «trece» = ieșire 1", bool(compara_harta(rau, sha)), "")
    caz("comparator hartă: rând pe alt sha sau lipsă = ieșire 1", bool(compara_harta(bun + [{"pas": "x", "commit": "b" * 40}], sha)) and bool(compara_harta(bun[:2], sha)), "")


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.1
# ---------------------------------------------------------------------------------------------------------------------------------------------
def cazuri_pagina():
    import verifica_pas as VP
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 800, "height": 400})
        pg.set_content(HTML)
        ob = lambda cheie: VP.observa_pagina(pg, cheie, CALIB)[1]   # noqa: E731

        def ver(nume, cheie, op, val, asteptat, in_motiv=""):
            o = ob(cheie)
            v, m = VP.compara_asertiune(op, val, o)
            caz("%s: %s %s %r pe %r => %s" % (nume, cheie, op, val, o, asteptat), v == asteptat and in_motiv in m, "%s %s" % (v, m))
        ver("(i) input cu valoare", "dom:#d|valoare", "egal", "2026-11-03", "trece")
        ver("(ii) aceeași valoare, altă dată", "dom:#d|valoare", "egal", "2026-11-04", "pica", "2026-11-03")
        ver("(iii) input gol, șirul gol", "dom:#gol|valoare", "egal", "", "trece")
        caz("(iii) măsura «text» pe același input rămâne goală", ob("dom:#d|text") == "", repr(ob("dom:#d|text")))
        ver("(iv) textarea", "dom:#t|valoare", "egal", "primul rând\nal doilea", "trece")
        ver("(v) select cu a doua opțiune aleasă", "dom:#s|valoare", "egal", "b", "trece")
        ver("(v) select: nu valoarea primei opțiuni", "dom:#s|valoare", "egal", "a", "pica")
        ver("(vi) div", "dom:#dv|valoare", "egal", "text în div", "pica", "elementul nu are valoare")
        ver("(vii) două input-uri, separate prin virgulă", "dom:.p|valoare", "contine", "unu,doi", "trece")
        ver("(x) selector inexistent", "dom:#nu-exista|valoare", "egal", "", "pica", "niciun element pentru selector")
        ver("(x) selector inexistent, operator «lipseste»", "dom:#nu-exista|valoare", "lipseste", "x", "pica", "niciun element pentru selector")
        ver("(xi) două elemente, unul fără valoare", "dom:.m, .m input|valoare", "contine", "x", "pica", "elementul nu are valoare")
        ver("(xii) buton", "dom:#b|valoare", "egal", "", "pica", "elementul nu are valoare")
        ver("(xiii) checkbox", "dom:#c|valoare", "egal", "on", "pica", "elementul nu are valoare")
        try:
            VP.observa_pagina(pg, "dom:#d|culoare", CALIB)
            caz("(viii) măsură necunoscută = refuz", False, "")
        except ValueError as e:
            caz("(viii) măsură necunoscută rămâne refuzată, cu «valoare» în mesaj", "culoare" in str(e) and "valoare" in str(e), str(e)[:160])
        b.close()
    # (ix) calea veche: selectorul «#x|valoare» e invalid -> excepție de selector (pe un server local de probă, nu pe 8019)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=CALIB))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    baza = "http://127.0.0.1:%d" % srv.server_address[1]
    try:
        try:
            VP.observa("dom:#x|valoare", {}, baza, "/")
            caz("(ix) calea veche cu «|valoare» ridică excepție", False, "a întors o valoare")
        except Exception as e:   # noqa: BLE001 — se cere excepția de selector, nu cea de conexiune
            mesaj = str(e)
            caz("(ix) calea veche cu «|valoare» ridică excepție de selector (%s)" % type(e).__name__, type(e).__name__ == "Error" and any(x in mesaj.lower() for x in ("selector", "valid")) and "ERR_CONNECTION" not in mesaj, mesaj.splitlines()[0][:160])
    finally:
        srv.shutdown()


def test_pur():
    """Testul pur, în subproces pytest, cu LOT_JURNAL propriu: roșu pe verifica_pas.py de la BAZA_COMMIT (o copie a scripts/ cu acel fișier), verde pe cel nou."""
    env = dict(os.environ, LOT_JURNAL=os.path.join(CALIB, "jurnal_pytest.log"))
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "core/test_oracol_valoare_16_5.py"]
    with tempfile.TemporaryDirectory(prefix="calib_16_5_") as tmp:
        os.makedirs(os.path.join(tmp, "core"))
        subprocess.run(["cp", "-r", os.path.join(RAD, "scripts"), os.path.join(tmp, "scripts")], check=True)
        subprocess.run(["cp", os.path.join(RAD, "core", "test_oracol_valoare_16_5.py"), os.path.join(tmp, "core")], check=True)
        open(os.path.join(tmp, "scripts", "verifica_pas.py"), "w", encoding="utf-8").write(git("show", "%s:scripts/verifica_pas.py" % BAZA_COMMIT))
        rosu = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, env=env)
    caz("testul pur pe verifica_pas.py de la %s = roșu" % BAZA_COMMIT, rosu.returncode != 0, rosu.stdout.strip().splitlines()[-1] if rosu.stdout.strip() else rosu.stderr[-120:])
    verde = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True, env=env)
    caz("testul pur pe verifica_pas.py nou = verde", verde.returncode == 0, verde.stdout.strip().splitlines()[-1] if verde.stdout.strip() else verde.stderr[-120:])


def regresie():
    """calibreaza_16_3.py oracol pe HEAD -> regresie_dupa.txt (regresie_inainte.txt s-a scris pe BAZA_COMMIT, înainte de modificări); calibrare.txt al lui 16.3 se readuce."""
    inainte = os.path.join(CALIB, "regresie_inainte.txt")
    dupa = os.path.join(CALIB, "regresie_dupa.txt")
    p = subprocess.run([sys.executable, os.path.join(AICI, "calibreaza_16_3.py"), "oracol"], cwd=RAD, capture_output=True, text=True)
    open(dupa, "w", encoding="utf-8").write(p.stdout)
    subprocess.run(["git", "checkout", "--", "docs/dovezi/16_3/calibrare.txt"], cwd=RAD, check=True)
    if not os.path.exists(inainte):
        caz("regresie: regresie_inainte.txt există", False, inainte)
        return
    txt_i = open(inainte, encoding="utf-8").read()
    li, ld = linii_caz(txt_i), linii_caz(p.stdout)
    mot = compara_regresie(txt_i, p.stdout)
    caz("regresie oracol: înainte %d ATINS / %d RATAT, după %d ATINS / %d RATAT; fără diferență de stare, nume sau număr" % (
        sum(s == "ATINS" for s, _ in li), sum(s == "RATAT" for s, _ in li), sum(s == "ATINS" for s, _ in ld), sum(s == "RATAT" for s, _ in ld)), not mot and bool(ld), mot[:3])


def pct1():
    comparatoare()
    cazuri_pagina()
    test_pur()
    regresie()


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.2
# ---------------------------------------------------------------------------------------------------------------------------------------------
def pct2():
    import verifica_pas as VP
    sha = git("rev-parse", "HEAD").strip()
    cmd = [sys.executable, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", LOT, "--verificator", "code", "--parcurs", os.path.join(CALIB, "parcurs_16_5.py"),
           "--pasi-txt", os.path.join(CALIB, "pasi_16_5.txt"), "--pasi-json", os.path.join(CALIB, "pasi_16_5.json"), "--parcurgere", "valoare", "--csv", CSV_CALIB,
           "--jurnal", os.path.join(CALIB, "jurnal_lansator.log"), "--iesire", os.path.join(CALIB, "parcurs.out")]
    p = subprocess.run(cmd, cwd=RAD, capture_output=True, text=True)
    print(p.stdout[-1500:], p.stderr[-500:])
    caz("lansatorul a ieșit cu 0", p.returncode == 0, p.returncode)
    randuri = VP.randuri_csv(CSV_CALIB) if os.path.exists(CSV_CALIB) else []
    mot = compara_harta(randuri, sha)
    caz("harta verdictelor pe %s: inainte.1 trece, inainte_pica.1 pică (cu «2026-11-03» în motiv), dupa_fill.1 trece" % sha[:8], not mot, mot)
    for r in randuri:
        if r.get("commit") == sha:
            caz("rând CSV %s: verdict %s, captura %s" % (r["pas"], r["verdict"], r["captura"]), bool(r.get("marcaj")) and os.path.exists(os.path.join(RAD, r["captura"])), r.get("motiv"))
    comparatoare_harta_doar()


def comparatoare_harta_doar():
    """Comparatorul hărții probat și aici (nu doar la pct.1), ca pct.2 să se poată rula singur."""
    sha = "a" * 40
    bun = [{"pas": k, "commit": sha, "verdict": v[0], "motiv": v[1]} for k, v in HARTA.items()]
    caz("comparator hartă (pct.2): verdicte corecte = 0, un verdict greșit = 1", compara_harta(bun, sha) == [] and bool(compara_harta([dict(bun[0], verdict="pica")] + bun[1:], sha)), "")


PARTI = {"pct1": pct1, "pct2": pct2}


def main(a):
    if not a or any(x not in PARTI for x in a):
        print(__doc__)
        return 2
    ref = curat()
    if ref:
        print("REFUZ: " + "; ".join(ref))
        return 1
    os.makedirs(CALIB, exist_ok=True)
    ratate = 0
    for p in a:
        del REZ[:]
        inainte = randuri_lot_in_comun()
        print("\n== %s ==" % p)
        PARTI[p]()
        dupa = randuri_lot_in_comun()
        caz("jurnalul comun, rânduri lot=%s înainte / după partea «%s»: %d / %d (diferența zero)" % (LOT, p, inainte, dupa), inainte == dupa, "")
        out = os.path.join(CALIB, "calibrare_%s.txt" % p)
        with open(out, "w", encoding="utf-8") as f:
            for nume, ok, det in REZ:
                f.write("%s  %s  %s\n" % ("ATINS" if ok else "RATAT", nume, str(det).replace("\n", " ")[:200]))
        ratate += sum(not ok for _, ok, _ in REZ)
        print("\n%d cazuri, %d ratate -> %s" % (len(REZ), sum(not ok for _, ok, _ in REZ), os.path.relpath(out, RAD)))
    return 1 if ratate else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
