# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_3_a.py — calibrarea comenzii 16.3-A pe ambele direcții (pct.1–4). NU e o rulare a porții: folosește funcțiile scripturilor, `publica_lot.py --verifica`, depozite temporare (`git init`), jurnale și chei
temporare; părțile „reale” (lansator real cu Haiku 5.5, stub) rulează sub lacătul lui lanseaza_verificator.py pe 8019. Scrie docs/dovezi/16_3_A/calibrare.txt: un rând pe caz, „ATINS” sau „RATAT”; ieșire 1 dacă un caz e ratat.
Fișierele-intrare ale calibrărilor stau în docs/dovezi/16_3_A/calibrare/ (jurnale, pasi.json de probă, praguri de probă).
  calibreaza_16_3_a.py <parte>...   părți: faze (pct.1 iv–x), pdf (pct.2 ii–v), strabun (pct.3), lista (pct.4), apoi „reale” (pe 8019): haiku (pct.1 i + pct.2 i), stub (pct.1 ii, iii și parcurs_code). Fără argument: primele patru.
  CALIB_ADAUGA=1 adaugă rândurile la calibrare.txt în loc să-l rescrie."""
import csv
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
RAD = os.path.dirname(AICI)
import calibreaza_16_3 as K  # noqa: E402  (caz, sh, g, depozit_nou, commit, STUB; rezultatele merg în K.REZ)

caz, sh, g, depozit_nou, commit, PY = K.caz, K.sh, K.g, K.depozit_nou, K.commit, K.PY
LOT = "16.3-A"
LOTF = "16_3_A"
DOVEZI = os.path.join(RAD, "docs", "dovezi", LOTF)
CALIB = os.path.join(DOVEZI, "calibrare")
LOTP = "PROBA-163A"   # lotul de probă al părților pure (nu are rânduri în jurnalul comun)
LOTPF = "PROBA_163A"


class CheieTemp:
    """Cheia oracolului într-un fișier temporar (verifica_pas citește CHEIE_ORACOL la import: se reîncarcă la intrare și la ieșire)."""
    def __init__(self, tmp):
        self.tmp = tmp

    def __enter__(self):
        os.environ["CHEIE_ORACOL_FISIER"] = os.path.join(self.tmp, "cheie_oracol")
        import verifica_pas as VP
        importlib.reload(VP)
        return VP

    def __exit__(self, *a):
        os.environ.pop("CHEIE_ORACOL_FISIER", None)
        import verifica_pas as VP
        importlib.reload(VP)


def scrie(cale, text):
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    open(cale, "w", encoding="utf-8").write(text)


def rand_faza(lot, faza, ev, rez, id_, detalii="", ora="2026-11-05T06:00:00+02:00"):
    return "\t".join([lot, faza, ev, ora, "c" * 12, rez, id_, "4242", detalii]) + "\n"


def jurnal_fara_verificator(lot):
    """Toate fazele obligatorii în afară de „verificator”, ca în jurnalul unui lot terminat."""
    t = ""
    for i, f in enumerate(("pornire", "hook", "poarta_verificator", "poarta_pytest", "poarta_plasa")):
        t += rand_faza(lot, f, "inceput", "-", "id%d" % i) + rand_faza(lot, f, "sfarsit", "verde", "id%d" % i)
    return t + rand_faza(lot, "publicare", "inceput", "-", "idp")


def citeste(cale, lot):
    import jurnal_lot as JL
    return [r for r in JL._citeste(cale) if r[0] == lot and len(r) > 8]


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.1 iv–x — faza „verificator” scrisă de lansator, parcurgerea haiku pe C
# ---------------------------------------------------------------------------------------------------------------------------------------------
def faze(tmp):
    import jurnal_lot as JL
    import publica_lot as PL
    c = "c" * 40
    with CheieTemp(tmp) as VP:
        def rand(pas, verdict, i1, parc="haiku_1", verif="haiku", sha=c):
            r = {"lot": LOTP, "commit": sha, "verificator": verif, "inceput": "t", "sfarsit": "t", "pas": pas, "actiune": "x", "verdict": verdict, "captura": os.path.abspath(__file__),
                 "motiv": "", "parcurgere": parc, "verificator_independent": i1}
            r["marcaj"] = VP.marcaj_rand(r)
            return r
        # (iv) jurnal fără faza „verificator”
        fara = os.path.join(CALIB, "jurnal_fara_faza.log")
        scrie(fara, jurnal_fara_verificator(LOTP))
        r = PL.faze_stop(citeste(fara, LOTP), False)
        caz("1 (iv) jurnal_fara_faza.log pe lot «produs» = STOP (faza lipsește)", any("lipsește" in m and "verificator" in m for m in r), r)
        # (v) faza scrisă de mână, cu jurnal_verificator.sh incepe/incheie (JL.inceput / JL.sfarsit, fără marcaj)
        mana = os.path.join(CALIB, "jurnal_faza_de_mana.log")
        scrie(mana, jurnal_fara_verificator(LOTP))
        os.environ["LOT_JURNAL"] = mana
        i = JL.inceput(LOTP, "verificator", pid=os.getpid())
        JL.sfarsit(LOTP, "verificator", i, "parcurs")
        os.environ.pop("LOT_JURNAL")
        r = PL.faze_stop(citeste(mana, LOTP), False)
        caz("1 (v) jurnal_faza_de_mana.log (scris cu JL.inceput/JL.sfarsit, ca jurnal_verificator.sh) pe lot «produs» = STOP «scrisă de mână»", any("scrisă de mână" in m for m in r), r)
        # (vi) text de marcaj copiat de la alt rând (o rulare adevărată a lansatorului), lipit pe rânduri scrise de mână
        orig = os.path.join(CALIB, "jurnal_faza_lansator.log")
        scrie(orig, jurnal_fara_verificator(LOTP))
        os.environ["LOT_JURNAL"] = orig
        a = VP.scrie_faza(LOTP, "verificator", "inceput", detalii="parcurgere=haiku_1", sha=c)
        VP.scrie_faza(LOTP, "verificator", "sfarsit", "parcurs", a, "corespunde/nu corespunde/nejudecabil=5/0/2 parcurgere=haiku_1", sha=c)
        os.environ.pop("LOT_JURNAL")
        rr = citeste(orig, LOTP)
        marca_i = [x for x in rr if x[1] == "verificator" and x[2] == "inceput"][0][8]
        marca_s = [x for x in rr if x[1] == "verificator" and x[2] == "sfarsit"][0][8]
        copiata = os.path.join(CALIB, "jurnal_faza_copiata.log")
        scrie(copiata, jurnal_fara_verificator(LOTP) + rand_faza(LOTP, "verificator", "inceput", "-", "idv", marca_i, ora="2026-11-05T07:00:00+02:00")
              + rand_faza(LOTP, "verificator", "sfarsit", "parcurs", "idv", marca_s, ora="2026-11-05T07:09:00+02:00"))
        r = PL.faze_stop(citeste(copiata, LOTP), False)
        caz("1 (vi) jurnal_faza_copiata.log (textul marcajului copiat de la alt rând) pe lot «produs» = STOP", any("scrisă de mână" in m for m in r), r)
        # (vii) același jurnal (v) pe lot «unelte»
        r = PL.faze_stop(citeste(mana, LOTP), True)
        caz("1 (vii) jurnal_faza_de_mana.log pe lot «unelte» = fără STOP", r == [], r)
        r = PL.faze_stop(citeste(fara, LOTP), True)
        caz("1 (vii) jurnal_fara_faza.log pe lot «unelte» = fără STOP (faza nu se cere)", r == [], r)
        # (viii) jurnal scris de lansator + CSV cu rânduri haiku pe C, lot «produs» = PASS (faze, CSV, parcurgere haiku pe C)
        rr_csv = [rand("a.1", "trece", "corespunde"), rand("p.1", "trece", "nejudecabil din captură (pdf)")]
        pasi = {"asertiuni": [{"id": "a.1", "operator": "egal", "valoare": "1", "cheie": "json:/s|v"}, {"id": "p.1", "operator": "text_contine", "valoare": "X", "cheie": "pdf:fisier:x.pdf"}]}
        excl = PL.asertiuni_excluse(pasi)
        stop = PL.faze_stop(citeste(orig, LOTP), False) + PL.csv_stop(rr_csv, LOTP, c, excl) + PL.fara_haiku_stop(rr_csv, c)
        caz("1 (viii) jurnal_faza_lansator.log + CSV cu rânduri haiku pe C, lot «produs» = PASS (fără STOP din faze_stop + csv_stop + fara_haiku_stop)", stop == [], stop)
        # (ix) rânduri haiku numai pe alt sha decât C
        alt = [rand("a.1", "trece", "corespunde", sha="d" * 40)]
        stop = PL.fara_haiku_stop(alt, c)
        caz("1 (ix) CSV cu rânduri haiku numai pe alt sha decât C = STOP «fără verificator independent pe C»", any("fără verificator independent pe C" in m for m in stop), stop)
        stop = PL.fara_haiku_stop([rand("a.1", "trece", "corespunde", verif="code")], c)
        caz("1 (ix) CSV cu rânduri numai ale verificatorului code pe C = STOP «fără verificator independent pe C»", any("fără verificator independent pe C" in m for m in stop), stop)
        # --verifica (hook-uri) nu cere haiku pe C: depozit temporar «produs», CSV fără rânduri haiku
        d = depozit_nou(tmp, "h1")
        K.commit(d, {"a.txt": "baza\n"}, "baza")
        g(d, "checkout", "-q", "-b", "lucru/proba")
        lista = "produs\nlot: %s\nfisiere_permise (x):\n  scripts/\n  docs/dovezi/%s/\n" % (LOTP, LOTPF)
        c1 = commit(d, {"scripts/praguri_%s.txt" % LOTPF: lista, "docs/dovezi/%s/x.txt" % LOTPF: "x\n"}, "lot")
        csv_cod = os.path.join(tmp, "cod.csv")
        with open(csv_cod, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=VP.CAMPURI, lineterminator="\n", restval="")
            w.writeheader()
            w.writerow(rand("a.1", "trece", "", parc="dupa", verif="code", sha=c1))
        e = dict(os.environ, CHEIE_ORACOL_FISIER=os.path.join(tmp, "cheie_oracol"))
        r = subprocess.run([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", c1, c1, LOTP, "--csv", csv_cod], cwd=d, capture_output=True, text=True, env=e)
        caz("1 (ix) `--verifica` (hook-urile) pe lot «produs», CSV fără rând haiku pe C = PASS (verificarea haiku e numai la publicare)", r.returncode == 0, r.stdout.strip()[-200:])
        # (x) extrasul rândurilor lot=16.3 din jurnalul comun
        comun = os.path.join(os.path.dirname(JL.comun()), ".lot_jurnal.log")
        extras = os.path.join(CALIB, "jurnal_16_3_extras.log")
        linii = [ln for ln in open(comun, encoding="utf-8") if ln.split("\t")[0] == "16.3"]
        scrie(extras, "".join(linii))
        rows = citeste(extras, "16.3")
        r = PL.faze_stop(rows, True)
        caz("1 (x) extrasul rândurilor lot=16.3 din jurnalul comun (%d rânduri; 16.3 e «unelte», faza «verificator» scrisă de mână nu se cere) = fără STOP" % len(rows), r == [] and len(rows) > 0, r)
        r2 = PL.faze_stop(rows, False)
        caz("1 (x) aceleași rânduri judecate ca lot «produs» = STOP (faza lor «verificator» e scrisă de mână, fără marcaj): regula nouă ar fi prins §E din raportul 16.3", any("scrisă de mână" in m for m in r2), r2)


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.2 ii–v — pdf: și interval_px nu se numără la „neefectuată”
# ---------------------------------------------------------------------------------------------------------------------------------------------
def pdf(tmp):
    import publica_lot as PL
    c = "c" * 40
    with CheieTemp(tmp) as VP:
        def rand(pas, verdict, i1, sha=c):
            r = {"lot": LOTP, "commit": sha, "verificator": "haiku", "inceput": "t", "sfarsit": "t", "pas": pas, "actiune": "x", "verdict": verdict, "captura": os.path.abspath(__file__),
                 "motiv": "", "parcurgere": "haiku_1", "verificator_independent": i1}
            r["marcaj"] = VP.marcaj_rand(r)
            return r
        pasi_tot = {"asertiuni": [{"id": "p.1", "pas": "p", "operator": "text_contine", "valoare": "X", "cheie": "pdf:fisier:x.pdf"},
                                  {"id": "p.2", "pas": "p", "operator": "text_contine", "valoare": "Y", "cheie": "pdf:/chitanta/1"},
                                  {"id": "b.5", "pas": "b", "operator": "interval_px", "valoare": "40-44", "cheie": "dom:.b|inaltime_px"}]}
        scrie(os.path.join(CALIB, "pasi_proba_toate_pdf_interval.json"), json.dumps(pasi_tot, ensure_ascii=False, indent=1))
        pasi_dom = {"asertiuni": pasi_tot["asertiuni"] + [{"id": "a.1", "pas": "a", "operator": "egal", "valoare": "1", "cheie": "dom:#x|text"}]}
        scrie(os.path.join(CALIB, "pasi_proba_dom_si_pdf.json"), json.dumps(pasi_dom, ensure_ascii=False, indent=1))
        pdf_ = "nejudecabil din captură (pdf)"
        px = "nejudecabil: interval_px: măsurat de oracol, nu se judecă din captură"
        excl_tot, excl_dom = PL.asertiuni_excluse(pasi_tot), PL.asertiuni_excluse(pasi_dom)
        caz("2 (ii) excluse prin cheie (pdf:) și operator (interval_px), nu prin text: %s" % sorted(excl_dom), excl_tot == {"p.1", "p.2", "b.5"} and excl_dom == excl_tot, sorted(excl_dom))
        s = PL.csv_stop([rand("p.1", "trece", pdf_), rand("p.2", "trece", pdf_), rand("b.5", "trece", px)], LOTP, c, excl_tot)
        caz("2 (ii) pasi.json cu toate aserțiunile pdf: și interval_px, toate «nejudecabil» = faza nu e «neefectuată», fără STOP", s == [], s)
        s = PL.csv_stop([rand("p.1", "trece", "nejudecabil"), rand("b.5", "trece", "nejudecabil")], LOTP, c, excl_tot)
        caz("2 (ii) același caz cu textul «nejudecabil» simplu pe pdf:/interval_px (excluderea e prin cheie și operator) = fără STOP", s == [], s)
        s = PL.csv_stop([rand("a.1", "trece", "nejudecabil"), rand("p.1", "trece", pdf_), rand("p.2", "trece", pdf_), rand("b.5", "trece", px)], LOTP, c, excl_dom)
        caz("2 (iii) o aserțiune dom: «nejudecabil» + restul pdf:/interval_px = faza «neefectuată» = STOP", any("neefectuată" in m for m in s), s)
        s = PL.csv_stop([rand("a.1", "trece", "corespunde"), rand("p.1", "trece", pdf_), rand("p.2", "trece", pdf_), rand("b.5", "trece", px)], LOTP, c, excl_dom)
        caz("2 (iv) o aserțiune dom: «corespunde» + restul pdf:/interval_px = fără STOP", s == [], s)
        # (v) verdictul oracolului «pica» pe o aserțiune pdf: pe C = STOP
        v = PL.jurnal_verificare_stop([rand("a.1", "trece", "corespunde"), rand("p.1", "pica", pdf_)], ["a.1", "p.1"], c, "d" * 40, 1)
        caz("2 (v) aserțiune pdf: cu verdictul oracolului «pica» pe C = STOP (rândul p.1 numit)", any("p.1" in m and "pica" in m for m in v), v)
        v = PL.jurnal_verificare_stop([rand("a.1", "trece", "corespunde"), rand("p.1", "trece", pdf_)], ["a.1", "p.1"], c, "d" * 40, 1)
        caz("2 (v) aceeași aserțiune pdf: cu verdictul «trece» = fără STOP", v == [], v)


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.3 — fișierele produse de parcurs după C
# ---------------------------------------------------------------------------------------------------------------------------------------------
def strabun(tmp):
    import publica_lot as PL
    d = depozit_nou(tmp, "s1")
    K.commit(d, {"a.txt": "baza\n"}, "baza")
    g(d, "checkout", "-q", "-b", "lucru/proba")
    dv = "docs/dovezi/%s/" % LOTPF
    c = commit(d, {dv + "jurnal_verificare.csv": "antet\n", dv + "dupa/code/vechi.out": "ieșire veche\n"}, "C")
    PL.DEP = d

    def dupa(fisiere, mesaj="după C"):
        g(d, "reset", "-q", "--hard", c)   # fiecare caz pornește de la C
        h = commit(d, fisiere, mesaj)
        return PL.ancestor_refuzuri(c, h, LOTPF)[0]
    r = dupa({dv + "dupa/code/chitanta.pdf": b"%PDF-1.4 calibrare\n"})
    caz("3 (i) .pdf sub docs/dovezi/<lot>/dupa/code/ după C = trece", r == [], r)
    r = dupa({dv + "haiku_1/haiku/nou.out": "ieșire nouă\n"})
    caz("3 .out adăugat sub docs/dovezi/<lot>/haiku_1/haiku/ după C = trece", r == [], r)
    r = dupa({dv + "chitanta_direct.pdf": b"%PDF-1.4\n"})
    caz("3 (ii) .pdf direct în docs/dovezi/<lot>/ = refuz cu numele", any("chitanta_direct.pdf" in m for m in r), r)
    r = dupa({"docs/alt_director/chitanta.pdf": b"%PDF-1.4\n"})
    caz("3 (ii) .pdf în alt director = refuz cu numele", any("alt_director/chitanta.pdf" in m for m in r), r)
    r = dupa({dv + "dupa/code/adanc/chitanta.pdf": b"%PDF-1.4\n"})
    caz("3 (ii) .pdf mai adânc decât <parcurgere>/<verificator>/ = refuz cu numele", any("adanc/chitanta.pdf" in m for m in r), r)
    r = dupa({dv + "dupa/altul/chitanta.pdf": b"%PDF-1.4\n"})
    caz("3 (ii) .pdf sub un verificator în afara code/haiku = refuz cu numele", any("altul/chitanta.pdf" in m for m in r), r)
    r = dupa({dv + "dupa/code/vechi.out": "ieșire modificată\n"})
    caz("3 (iii) .out modificat (M) = refuz cu numele", any("vechi.out" in m and "numai se adaugă" in m for m in r), r)
    r = dupa({dv + "dupa/code/capturi/lot_dupa_a.1_aaaaaaaa.png": b"\x89PNG"})
    caz("3 (iv) .png în capturi/ după C = trece, ca până acum", r == [], r)
    r = dupa({dv + "dupa/code/script.sh": "x\n"})
    caz("3 alt fișier sub <parcurgere>/<verificator>/ (nici .pdf, nici .out, nici capturi/*.png) = refuz cu numele", any("script.sh" in m for m in r), r)
    PL.DEP = None


# ---------------------------------------------------------------------------------------------------------------------------------------------
# pct.4 — lista fișierelor permise și la lotul «produs»
# ---------------------------------------------------------------------------------------------------------------------------------------------
PRAGURI_PROBA = ("produs\nlot: %s\ncomentariu liber, cu fisiere_permise în mijloc\n"
                 "fisiere_permise (aplicata pe diff; text între paranteze ignorat):\n"
                 "  scripts/plasa_16_2.manifest (plasa fixa; creste numai cu randul fisierului nou)\n"
                 "  scripts/praguri_%s.txt\n  docs/dovezi/%s/\n  DEFICIENTE.md\n  CLAUDE.md (numai inainte de C)\n  core/casa.py\n") % (LOTP, LOTPF, LOTPF)


def lista(tmp):
    import publica_lot as PL
    scrie(os.path.join(CALIB, "praguri_proba_produs.txt"), PRAGURI_PROBA)
    intrari = PL.lista_permisa(PRAGURI_PROBA)
    caz("4 lista: liniile cu fisier sau director (cu «/» la sfârșit); textul dintre paranteze se ignoră", intrari == ["scripts/plasa_16_2.manifest", "scripts/praguri_%s.txt" % LOTPF, "docs/dovezi/%s/" % LOTPF, "DEFICIENTE.md", "CLAUDE.md", "core/casa.py"], intrari)

    def depozit(fisiere, praguri=PRAGURI_PROBA, nume="l"):
        d = depozit_nou(tmp, nume)
        K.commit(d, {"a.txt": "baza\n", "static/js/api.js": "baza\n"}, "baza")
        g(d, "checkout", "-q", "-b", "lucru/proba")
        f = dict(fisiere)
        f["scripts/praguri_%s.txt" % LOTPF] = praguri
        h = commit(d, f, "lot")
        PL.DEP = d
        return d, h
    d, h = depozit({"docs/dovezi/%s/baza.json" % LOTPF: "{}\n", "core/casa.py": "x = 1\n", "DEFICIENTE.md": "d\n", "CLAUDE.md": "c\n"}, nume="l1")
    r = PL.produs_refuzuri(h, LOTPF)
    caz("4 (i) lot «produs» cu diff numai din listă = PASS (fără refuz)", r == [], r)
    e = dict(os.environ)
    rr = subprocess.run([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", h, h, LOTP], cwd=d, capture_output=True, text=True, env=e)
    caz("4 (i) `publica_lot.py --verifica C HEAD` pe același depozit = PASS", rr.returncode == 0 and "PASS" in rr.stdout, rr.stdout.strip()[-200:])
    d, h = depozit({"docs/dovezi/%s/baza.json" % LOTPF: "{}\n", "static/js/api.js": "schimbat\n"}, nume="l2")
    r = PL.produs_refuzuri(h, LOTPF)
    caz("4 (ii) un fișier în plus (static/js/api.js) = refuz cu numele", len(r) == 1 and r[0].startswith("static/js/api.js"), r)
    rr = subprocess.run([PY, os.path.join(AICI, "publica_lot.py"), "--verifica", h, h, LOTP], cwd=d, capture_output=True, text=True)
    caz("4 (ii) `--verifica` pe același depozit = refuz (ieșire 1) cu static/js/api.js numit", rr.returncode == 1 and "static/js/api.js" in rr.stdout, rr.stdout.strip()[-200:])
    d, h = depozit({"docs/dovezi/%s/x" % LOTPF: "x\n", "docs/dovezi/%s/dupa/code/y.pdf" % LOTPF: b"%PDF"}, nume="l3")
    r = PL.produs_refuzuri(h, LOTPF)
    caz("4 (iii) fișiere dintr-un director listat (docs/dovezi/<lot>/x și în subdirector) = trece", r == [], r)
    d, h = depozit({"docs/dovezi/%s_altul/x" % LOTPF: "x\n"}, nume="l4")
    r = PL.produs_refuzuri(h, LOTPF)
    caz("4 directorul listat nu acoperă un director cu prefix comun (docs/dovezi/%s_altul/x) = refuz cu numele" % LOTPF, len(r) == 1 and "_altul/x" in r[0], r)
    d, h = depozit({"core/casa.py": "x\n"}, praguri="produs\nlot: x\n", nume="l5")
    r = PL.produs_refuzuri(h, LOTPF)
    caz("4 lot «produs» fără lista fisiere_permise în praguri = refuz (lista e cerută)", len(r) == 1 and "fisiere_permise" in r[0], r)
    # (iv) lot «unelte»: comportamentul de azi (cele două cazuri din 16.3 pct.0)
    unelte_p = "unelte\nlot: %s\nfisiere_permise:\n  core/numit.py\n" % LOTP
    d, h = depozit({"core/numit.py": "x\n", "scripts/a.py": "x\n", "DECIZII.md": "d\n"}, praguri=unelte_p, nume="u1")
    r = PL.unelte_refuzuri(h, LOTPF)
    caz("4 (iv) lot «unelte»: fișier din core/ numit în praguri + scripts/ + registre = trece", r == [], r)
    d, h = depozit({"static/js/api.js": "schimbat\n", "scripts/a.py": "x\n"}, praguri=unelte_p, nume="u2")
    r = PL.unelte_refuzuri(h, LOTPF)
    caz("4 (iv) lot «unelte»: static/js/api.js nenumit = refuz cu numele", len(r) == 1 and r[0].startswith("static/js/api.js"), r)
    PL.DEP = None
    # lotul publicat anterior (16.3, «unelte»): lista uneltelor, pe diff-ul lui 16.3
    prim = g(RAD, "log", "--reverse", "--format=%H", "--grep=Lotul 16, comanda 16.3 (unelte)").stdout.split()[0]
    baza = g(RAD, "rev-parse", prim + "^").stdout.strip()
    ultim = g(RAD, "log", "-1", "--format=%H", "--grep=Lotul 16, comanda 16.3 (unelte)").stdout.strip()
    cmd = [PY, "-c", "import sys; sys.path.insert(0, %r); import publica_lot as P; P.DEP = %r; print(P.unelte_refuzuri(%r, '16_3', %r)); print(P.produs_refuzuri(%r, '16_3_A_probe', %r, open(%r).read()))" % (
        AICI, RAD, ultim, baza, ultim, baza, os.path.join(os.path.expanduser("~"), "ghid_incoming", "praguri_16_2_A.txt"))]
    out = sh(cmd, RAD)
    unelte_16_3, produs_16_3 = out.stdout.strip().splitlines()[-2:]
    caz("4 pe lotul publicat 16.3 (praguri_16_3.txt, diff %s..%s): lista uneltelor = fără refuz" % (baza[:8], ultim[:8]), unelte_16_3 == "[]", unelte_16_3)
    scrie(os.path.join(CALIB, "praguri_proba_produs_162A.txt"), open(os.path.expanduser("~/ghid_incoming/praguri_16_2_A.txt"), encoding="utf-8").read())
    lista_ref = eval(produs_16_3)
    caz("4 praguri de probă «produs» (lista lui 16.2-A) pe diff-ul lui 16.3 = refuz cu fișierele scripts/ ale lui 16.3 numite (%d fișiere)" % len(lista_ref),
        len(lista_ref) > 0 and any(m.startswith("scripts/publica_lot.py") for m in lista_ref) and any(m.startswith("scripts/lanseaza_verificator.py") for m in lista_ref), lista_ref[:3])


# ---------------------------------------------------------------------------------------------------------------------------------------------
# părțile reale (pe 8019, sub lacăt)
# ---------------------------------------------------------------------------------------------------------------------------------------------
def lanseaza(csv_, parcurgere, jurnal, verificator="haiku", mod=None, marca=None, pasi="a", pasi_json=None, pasi_txt=None, parcurs=None, iesire=None, fara_parcurs=False):
    e = dict(os.environ, PARCURS_PASI=pasi)
    if mod:
        e.update(CLAUDE_BIN=os.path.join(os.path.dirname(marca), "claude_stub"), STUB_MOD=mod, STUB_MARCA=marca)
    cmd = [PY, os.path.join(AICI, "lanseaza_verificator.py"), "--lot", LOT, "--parcurs", parcurs or os.path.join(RAD, "docs", "dovezi", "16_3", "parcurs_proba_f017.py"),
           "--verificator", verificator, "--pasi-txt", pasi_txt or os.path.expanduser("~/ghid_incoming/pasi_16_3_proba.txt"),
           "--pasi-json", pasi_json or os.path.join(RAD, "docs", "dovezi", "16_3", "pasi.json"), "--csv", csv_, "--jurnal", jurnal, "--parcurgere", parcurgere,
           "--scenariu", os.path.expanduser("~/ghid_incoming/scenarii_pilot.txt"), "--sectiune", "F017"]
    if iesire:
        cmd += ["--iesire", iesire]
    if fara_parcurs:
        cmd += ["--fara-parcurs"]
    return sh(cmd, RAD, e)


def faze_lansator(jurnal, faza="verificator"):
    rows = citeste(jurnal, LOT)
    return [r for r in rows if r[1] == faza and r[2] == "inceput"], [r for r in rows if r[1] == faza and r[2] == "sfarsit"]


def durata(i, s):
    import datetime
    return (datetime.datetime.fromisoformat(s[3]) - datetime.datetime.fromisoformat(i[3])).total_seconds()


def haiku(tmp):
    """pct.1 (i) și pct.2 (i): lansatorul real cu Haiku 5.5 pe parcursul de probă 16.3, PARCURS_PASI=a,p (o aserțiune json și una pdf:); apoi aceeași comandă cu stub pe toate cele 7 aserțiuni."""
    import verifica_pas as VP
    csv_ = os.path.join(DOVEZI, "jurnal_verificare_calibrare.csv")
    jurnal = os.path.join(CALIB, "jurnal_lansator.log")
    ies = os.path.join(DOVEZI, "iesiri")
    os.makedirs(ies, exist_ok=True)
    sha = g(RAD, "rev-parse", "HEAD").stdout.strip()
    r = lanseaza(csv_, "calib_haiku_pdf", jurnal, pasi="a,p", iesire=os.path.join(ies, "calib_haiku_pdf_%s.out" % sha[:8]))
    inc, sf = faze_lansator(jurnal)
    ok_faza = bool(inc) and bool(sf) and sf[-1][5] == "parcurs"
    caz("1 (i) lansator real --verificator haiku, PARCURS_PASI=a,p: faza «verificator» scrisă de lansator (inceput + sfarsit «parcurs»), durata reală %ss > 0" % (durata(inc[-1], sf[-1]) if ok_faza else "-"),
        ok_faza and durata(inc[-1], sf[-1]) > 0, [x[5] for x in sf])
    caz("1 (i) marcajul fazei valid pe ambele rânduri (cheia reală a oracolului)", ok_faza and VP.faza_marcata_valida(inc[-1]) and VP.faza_marcata_valida(sf[-1]), "")
    caz("1 (i) detaliile cu numărul răspunsurilor (corespunde/nu corespunde/nejudecabil)", ok_faza and "corespunde/nu corespunde/nejudecabil=" in sf[-1][8], sf[-1][8][:100] if sf else "")
    rr = {x["pas"]: x for x in VP.randuri_csv(csv_) if x["parcurgere"] == "calib_haiku_pdf" and x["commit"] == sha}
    caz("1 (i) rândul p.1 = «nejudecabil din captură (pdf)», marcaj valid; a.1 judecat de Haiku", "p.1" in rr and rr["p.1"]["verificator_independent"] == "nejudecabil din captură (pdf)" and VP.marcaj_valid(rr["p.1"]) and
        rr.get("a.1", {}).get("verificator_independent", "").split(":")[0] in ("corespunde", "nu corespunde", "nejudecabil"), {k: v["verificator_independent"][:60] for k, v in rr.items()})
    # pct.2 (i): stub «corespunde» pe cele 6 care se dau agentului; toate cele 7 aserțiuni, toți pașii a,b,c,p,q
    marca = os.path.join(tmp, "marca.txt")
    stub_ = os.path.join(tmp, "claude_stub")
    open(stub_, "w").write(K.STUB)
    os.chmod(stub_, 0o755)
    r = lanseaza(csv_, "calib_stub_pdf", jurnal, mod="da", marca=marca, pasi="a,b,c,p,q", iesire=os.path.join(ies, "calib_stub_pdf_%s.out" % sha[:8]))
    prima = open(marca).read().splitlines()
    ids = prima[0].split("|")[2].strip().split(",") if prima else []
    caz("2 (i) pasi.json 16.3 (7 id-uri), stub «corespunde»: Haiku primește 6 (fără p.1) într-o singură instanță: %s" % ",".join(ids), len(prima) == 1 and sorted(ids) == ["a.1", "b.10", "b.9", "c.1", "q.1", "q.2"], prima)
    rr = {x["pas"]: x for x in VP.randuri_csv(csv_) if x["parcurgere"] == "calib_stub_pdf" and x["commit"] == sha}
    caz("2 (i) rândul p.1 are «nejudecabil din captură (pdf)» cu marcaj valid; celelalte 6 «corespunde»; ieșire 0, fără STOP",
        r.returncode == 0 and rr.get("p.1", {}).get("verificator_independent") == "nejudecabil din captură (pdf)" and VP.marcaj_valid(rr["p.1"]) and
        all(rr[i]["verificator_independent"].startswith("corespunde") for i in ids), r.stdout.strip()[-200:])
    inc, sf = faze_lansator(jurnal)
    caz("2 (i) faza «verificator» a rulării cu stub: detalii 6/0/1 (6 corespunde, 0 nu corespunde, 1 nejudecabil)", sf[-1][5] == "parcurs" and "=6/0/1" in sf[-1][8], sf[-1][8][:90])


def stub(tmp):
    """pct.1 (ii) și (iii); parcurs_code."""
    import verifica_pas as VP
    csv_ = os.path.join(DOVEZI, "jurnal_verificare_calibrare.csv")
    jurnal = os.path.join(CALIB, "jurnal_lansator.log")
    ies = os.path.join(DOVEZI, "iesiri")
    os.makedirs(ies, exist_ok=True)
    sha = g(RAD, "rev-parse", "HEAD").stdout.strip()
    marca = os.path.join(tmp, "marca.txt")
    stub_ = os.path.join(tmp, "claude_stub")
    open(stub_, "w").write(K.STUB)
    os.chmod(stub_, 0o755)
    r = lanseaza(csv_, "calib_stub_nu", jurnal, mod="nu_nu", marca=marca, iesire=os.path.join(ies, "calib_stub_nu_%s.out" % sha[:8]))
    inc, sf = faze_lansator(jurnal)
    caz("1 (ii) stub «nu corespunde» la ambele instanțe pe a.1: faza «parcurs», detalii 0/1/0, STOP dezacord (ieșire 1)",
        r.returncode == 1 and "STOP dezacord oracol–verificator: a.1" in r.stdout and sf[-1][5] == "parcurs" and "=0/1/0" in sf[-1][8], "%s | %s" % (sf[-1][5], sf[-1][8][:80]))
    # (iii) lansator oprit cu eroare: parcurs cu import nepermis
    rau = os.path.join(tmp, "parcurs_rau.py")
    open(rau, "w").write("import os\nimport requests\n\ndef ruleaza(pagina, ctx):\n    pass\n")
    scrie(os.path.join(CALIB, "parcurs_cu_import_nepermis.py"), open(rau).read())
    r = lanseaza(csv_, "calib_import", jurnal, parcurs=rau)
    inc, sf = faze_lansator(jurnal)
    caz("1 (iii) lansator oprit cu eroare (parcurs cu import nepermis): faza «verificator» = «intrerupt», marcaj valid", r.returncode == 1 and "requests" in r.stdout and sf[-1][5] == "intrerupt" and VP.faza_marcata_valida(sf[-1]),
        "%s | %s" % (sf[-1][5], r.stdout.strip()[-100:]))
    # parcurs_code
    r = lanseaza(csv_, "calib_code", jurnal, verificator="code", pasi="a", iesire=os.path.join(ies, "calib_code_%s.out" % sha[:8]))
    inc, sf = faze_lansator(jurnal, "parcurs_code")
    caz("1 --verificator code scrie la fel faza «parcurs_code» (marcaj valid, rezultat «parcurs»)", r.returncode == 0 and bool(sf) and sf[-1][5] == "parcurs" and VP.faza_marcata_valida(sf[-1]) and VP.faza_marcata_valida(inc[-1]), "%s" % ([x[5] for x in sf]))
    r = sh([PY, os.path.join(AICI, "publica_lot.py"), "--controleaza", csv_])
    caz("1 jurnal_verificare_calibrare.csv după rulările: controleaza trece (capturi, chei unice, marcaje)", r.returncode == 0, r.stdout.strip()[-200:])
    comun = os.path.join(os.path.dirname(__import__("jurnal_lot").comun()), ".lot_jurnal.log")
    prinse = [ln for ln in open(comun, encoding="utf-8") if ln.split("\t")[0] == LOT and ln.split("\t")[1] in ("verificator", "parcurs_code")]
    caz("1 nicio fază «verificator» / «parcurs_code» a calibrărilor în jurnalul comun (lot=16.3-A): %d rânduri" % len(prinse), not prinse, prinse[:1])


PARTI = {"faze": faze, "pdf": pdf, "strabun": strabun, "lista": lista, "haiku": haiku, "stub": stub}
PARTI_IMPLICITE = ["faze", "pdf", "strabun", "lista"]


def main(a):
    parti = a or PARTI_IMPLICITE
    tmp = tempfile.mkdtemp(prefix="calibrare_16_3a_")
    os.makedirs(CALIB, exist_ok=True)
    try:
        for p in parti:
            print("\n== %s ==" % p)
            PARTI[p](tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = os.path.join(DOVEZI, "calibrare.txt")
    mod = "a" if os.environ.get("CALIB_ADAUGA") and os.path.exists(out) else "w"
    with open(out, mod, encoding="utf-8") as f:
        for nume, ok, det in K.REZ:
            f.write("%s  %s  %s\n" % ("ATINS" if ok else "RATAT", nume, str(det).replace("\n", " ")[:200]))
    print("\n%d cazuri, %d ratate -> %s" % (len(K.REZ), sum(not ok for _, ok, _ in K.REZ), os.path.relpath(out, RAD)))
    return 1 if any(not ok for _, ok, _ in K.REZ) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
