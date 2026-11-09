# -*- coding: utf-8 -*-
"""scripts/publica_lot.py — contractul de publicare (comanda 16.1, pct.4); chemat numai de scripts/publica_lot.sh. Ordinea: începutul fazei „publicare”, ZIP-ul, verificările
(raport, poartă, jurnal, perimetru, bază, reluări, jurnalul verificării), verdictul PASS/STOP calculat din jurnal față de scripts/praguri_<lot>.txt, `PASS <sha>` în
<git-common-dir>/publica_verdicte.log. Fără PASS nu se mută `main` (scripts/githooks/reference-transaction) și nu se împinge pe main (scripts/githooks/pre-push),
iar restartul din post-commit refuză. Sfârșitul fazei „publicare” îl scrie publica_lot.sh după push.
Regula strămoșului (16.1-C1, 16.1-C2 pct.4): verdictul VERDE al rulării complete finale și rândurile din jurnal_verificare.csv sunt produse pe un commit C (ultima rulare completă din
starea lotului) și rămân valabile pentru HEAD numai dacă C e strămoș al lui HEAD și diff-ul C..HEAD atinge numai căile din `ancestor_refuzuri`. Apelabilă separat, fără publicare:
  publica_lot.py --verifica <C> <HEAD> [lot]   (lotul din LOT sau din ramura curentă; hook-urile reference-transaction și pre-push o chemă cu lotul din rândul PASS)
  publica_lot.py --proba [lot]                 (16.1-C3, pct.3) contractul la început: rândul pasului a) din jurnal_verificare.csv există, are captură, verdict „trece” și sha = commitul de bază (merge-base cu
                                               main); scrie faza „proba_contract” în jurnal. O declanșează scripts/githooks/post-commit pe ramurile lucru/* la primul commit după merge-base. Un lot fără
                                               „proba_contract” verde = STOP la publicare. (16.3, pct.0) Un lot „unelte” fără pasi.txt trece verde cu eticheta „unelte, fără oracol”; un lot de produs fără rândul a) rămâne roșu.
  publica_lot.py --verifica <C> <HEAD> [lot] [--csv <fișier>]   (16.3) pe lângă regula strămoșului: lotul „unelte” are lista permisă de fișiere (UNELTE_PERMISE; static/, core/ în afara test_*, templates/, frontend_test/ numai
                                               dacă sunt numite în scripts/praguri_<lot>.txt) și rândurile din jurnal_verificare.csv au marcaj valid (STOP „verdict în afara oracolului”; scutite: LOTURI_FARA_MARCAJ).
                                               --csv numai pentru calibrări; la publicare, „--csv” = refuz.
  publica_lot.py --controleaza <csv>           (16.3, pct.2) controlul încrucișat pe un CSV: captura există, cheia (lot, parcurgere, pas, sha, verificator) e unică, marcajul e valid (scris de jurnal_verificator.sh controleaza).
Lotul „produs” (16.3-A): faza „verificator” trebuie scrisă de lansator (marcaj HMAC; scrisă de mână sau copiată = STOP), la publicare trebuie o parcurgere haiku pe C în jurnal_verificare.csv, lista
`fisiere_permise` din scripts/praguri_<lot>.txt se aplică pe diff-ul merge-base..HEAD, iar aserțiunile cu cheia pdf: și operatorul interval_px nu se numără la „neefectuată”.
Oracolul pașilor (16.1-C3, pct.1): ~/ghid_incoming/pasi_<lot>.txt (al arhitectului) are hash-ul din rândul „pornire”, iar docs/dovezi/<lot>/pasi.json copiază literal operator + valoare ale fiecărei aserțiuni, altfel
STOP „oracol modificat”. Lotul de produs cere fișierul; lotul de unelte fără fișier nu are oracol.
Ieșire: 0 = PASS, 1 = STOP (nepublicat, cu cifra sau motivul)."""
import csv
import json
import os
import re
import subprocess
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402
import poarta_clasifica as C  # noqa: E402
import oracol_pasi as OP  # noqa: E402
import poarta_lib as L  # noqa: E402
import verifica_pas as VP  # noqa: E402

RAD = L.RAD
ACASA = os.path.expanduser("~")
#: loturile dinaintea marcajului HMAC al rândurilor (16.3, pct.1): lista fixă; orice alt lot cu un rând fără marcaj valid = STOP „verdict în afara oracolului”
LOTURI_FARA_MARCAJ = ("16.1", "16.1-C2", "16.1-C3")
#: lista permisă implicită a unui lot „unelte” (16.3, pct.0); orice alt fișier din static/, core/ (în afara test_*), templates/ sau frontend_test/ trebuie numit în scripts/praguri_<lot>.txt
UNELTE_PERMISE = ("scripts/", "frontend_test/e2e/conftest.py", "CLAUDE.md", "DEFICIENTE.md", "DECIZII.md", "PREDARE_LANT.md")
UNELTE_INTERZISE = ("static/", "core/", "templates/", "frontend_test/")
#: fișierele porții și ale contractului: nu se ating în afara loturilor marcate „unelte” în scripts/praguri_<lot>.txt
PAZITE = ("scripts/poarta_lot.sh", "scripts/publica_lot.sh", "scripts/baza_test.sh", "scripts/poarta_nucleu.txt", "conftest.py")
FRAZA_RISC = ("confinarea la fișiere deja atinse nu dovedește că fiecare modificare e legată de testul picat; "
              "poarta finală dovedește comportamentul din manifest, nu justificarea fiecărei linii")


#: depozitul în care se judecă commiturile; `--verifica` din hook-uri îl ia din directorul curent al hook-ului (None = worktree-ul scriptului)
DEP = None


def git(*a):
    return subprocess.run(["git", *a], cwd=DEP or RAD, capture_output=True, text=True).stdout.strip()


def _git_brut(*a):
    return subprocess.run(["git", *a], cwd=DEP or RAD, capture_output=True, text=True)


def _fisier_la(commit, cale):
    r = _git_brut("show", "%s:%s" % (commit, cale))
    return r.stdout.splitlines() if r.returncode == 0 else None


def ancestor_refuzuri(c, head, lotf):
    """Regula strămoșului: -> (refuzuri, fișierele din diff); refuzuri goale = verdictul și rândurile produse pe C sunt valabile pentru HEAD."""
    if _git_brut("cat-file", "-e", c + "^{commit}").returncode or _git_brut("cat-file", "-e", head + "^{commit}").returncode:
        return ["C (%s) sau HEAD (%s) nu e commit" % (c[:12], head[:12])], []
    if _git_brut("merge-base", "--is-ancestor", c, head).returncode:
        return ["C (%s) nu e strămoș al lui HEAD (%s)" % (c[:12], head[:12])], []
    dovezi = "docs/dovezi/%s/" % lotf
    csv_cale = dovezi + "jurnal_verificare.csv"
    # CLAUDE.md nu e permis (16.1-C2 pct.4): regulile se schimbă înainte de C sau în lotul următor
    exacte = {csv_cale, dovezi + "registre_%s.md" % lotf, "DEFICIENTE.md", "DECIZII.md", "PREDARE_LANT.md"}
    iesire = _git_brut("diff", "--raw", "-z", "--no-renames", c, head).stdout.split("\0")
    refuzuri, fisiere = [], []
    for meta, cale in zip(iesire[0::2], iesire[1::2]):
        mod_vechi, mod_nou, _, _, stare = meta.lstrip(":").split()
        fisiere.append(cale)
        capturi = cale.startswith(dovezi) and cale.endswith(".png") and "/capturi/" in cale[len(dovezi) - 1:] and ".." not in cale.split("/")
        # 16.3-A pct.3: fișierele descărcate de parcurs (*.pdf) și ieșirile lansatorului (*.out) stau exact în docs/dovezi/<lot>/<parcurgere>/<verificator>/
        parti = cale[len(dovezi):].split("/") if cale.startswith(dovezi) else []
        produse = len(parti) == 3 and parti[1] in ("code", "haiku") and ".." not in parti and parti[2].endswith((".pdf", ".out"))
        doar_adaugat = produse and parti[2].endswith(".out")
        if cale not in exacte and not capturi and not produse:
            refuzuri.append("%s: cale în afara listei permise" % cale)
        elif stare not in ("A", "M") or (doar_adaugat and stare != "A"):
            refuzuri.append("%s: schimbare %s (%s)" % (cale, stare, "ieșirile .out numai se adaugă" if doar_adaugat else "numai adăugare sau modificare"))
        elif mod_nou != "100644" or (stare == "M" and mod_vechi != mod_nou):
            refuzuri.append("%s: mod %s -> %s (fișier obișnuit, mod neschimbat)" % (cale, mod_vechi, mod_nou))
    if csv_cale in fisiere:
        vechi, nou = _fisier_la(c, csv_cale) or [], _fisier_la(head, csv_cale) or []
        if nou[:len(vechi)] != vechi:
            refuzuri.append("%s: un rând existent la C a fost modificat sau șters" % csv_cale)
    return refuzuri, fisiere


def pornire_stop(pornire, lot, unelte):
    """Proveniența pornirii (16.1-C2 pct.2): un singur rând „pornire”; marcaj de coadă valid sau, numai într-un lot „unelte” fără alt rând „pornire”, „reconstituit”. -> motivele de STOP."""
    if not pornire:
        return ["lipsă pornire"]
    if len(pornire) > 1:
        return ["jurnalul are %d rânduri „pornire” pentru lot (se cere unul singur)" % len(pornire)]
    if "reconstituit" in pornire[0][8]:
        return [] if unelte else ["rândul „pornire” e reconstituit, dar lotul nu e „unelte” (un lot de produs pornește numai din coadă)"]
    if not JL.marca_valida(pornire[0], lot):
        return ["rândul „pornire” nu are marcajul de proveniență al cozii (un lot de produs pornește numai din coadă)"]
    return []


#: directorul arhitectului (fișierele pasi_<lot>.txt, exceptii_<lot>.txt); GHID_INCOMING îl mută numai în calibrări
def _ghid():
    return os.environ.get("GHID_INCOMING") or os.path.join(ACASA, "ghid_incoming")


def oracol_stop(lotf, unelte, pornire, rad=None):
    """Oracolul pașilor (16.1-C3, pct.1). `pornire` = rândul „pornire” (început). -> motivele de STOP „oracol modificat” (sau lipsa fișierului la un lot de produs)."""
    arh = os.path.join(_ghid(), "pasi_%s.txt" % lotf)
    h_jurnal = re.search(r"\bpasi_sha256=([0-9a-f]{64})\b", pornire[8] if len(pornire) > 8 else "")
    if not os.path.exists(arh):
        if h_jurnal:
            return ["oracol modificat: fișierul arhitectului pasi_%s.txt a dispărut după pornire" % lotf]
        return [] if unelte else ["lipsește pasi_%s.txt al arhitectului (un lot de produs are oracol)" % lotf]
    if not h_jurnal:
        return ["oracol modificat: pasi_%s.txt există, dar rândul „pornire” nu are hash-ul lui (fișierul a apărut sau s-a schimbat după pornire)" % lotf]
    if L.hash_fisier(arh) != h_jurnal.group(1):
        return ["oracol modificat: hash-ul curent al pasi_%s.txt diferă de cel din rândul „pornire”" % lotf]
    if not unelte:   # 16.3: în pasi_<lot>.txt al unui lot de produs, „descriere” nu conține verdicte (le-ar sufla verificatorului independent)
        for x in OP.parseaza(open(arh, encoding="utf-8").read())[0]:
            gasite = [c for c in ("trece", "pică", "pica", "corespunde") if re.search(r"\b%s\b" % c, x["descriere"], re.I)]
            if gasite:
                return ["oracol modificat: descrierea aserțiunii %s conține cuvintele de verdict %s (nu sunt permise într-un lot de produs)" % (x["id"], ", ".join(gasite))]
    cale = os.path.join(rad or RAD, "docs", "dovezi", lotf, "pasi.json")
    if not os.path.exists(cale):
        return ["oracol modificat: lipsește docs/dovezi/%s/pasi.json" % lotf]
    return ["oracol modificat: " + m for m in OP.refuzuri(open(arh, encoding="utf-8").read(), json.load(open(cale, encoding="utf-8")))]


def proba_stop(rows, lot):
    """Faza „proba_contract” (16.1-C3, pct.3): ultimul ei sfârșit trebuie „verde”. -> motivele de STOP."""
    sf = [r for r in rows if r[0] == lot and r[1] == "proba_contract" and r[2] == "sfarsit"]
    if not sf:
        return ["faza „proba_contract” lipsește (contractul se probează la primul commit al lotului, de scripts/githooks/post-commit)"]
    return [] if sf[-1][5] == "verde" else ["faza „proba_contract” nu e verde (%s)" % sf[-1][5]]


def lot_unelte(rad, lotf):
    """Lotul e marcat „unelte” (prima linie din scripts/praguri_<lot>.txt, în arborele de lucru `rad`)."""
    try:
        return open(os.path.join(rad, "scripts", "praguri_%s.txt" % lotf), encoding="utf-8").readline().strip().lower() == "unelte"
    except OSError:
        return False


def proba_fara_oracol(rad, lot):
    """Lot „unelte” fără docs/dovezi/<lot>/pasi.txt: nu are pasul a), deci nici rând de probat (16.3, pct.0)."""
    lotf = L.lot_fisier(lot)
    return lot_unelte(rad, lotf) and not os.path.exists(os.path.join(rad, "docs", "dovezi", lotf, "pasi.txt"))


def proba_refuzuri(rad, lot, main="main"):
    """Rândul pasului a) (primul pas din docs/dovezi/<lot>/pasi.txt) din jurnal_verificare.csv: există, captura există, verdict „trece”, sha = commitul de bază (merge-base cu main). -> refuzurile.
    Un lot „unelte” fără pasi.txt nu are ce proba (16.3, pct.0): fără refuz; un lot de produs fără rândul a) rămâne refuzat."""
    lotf = L.lot_fisier(lot)
    if proba_fara_oracol(rad, lot):
        return []
    d = os.path.join(rad, "docs", "dovezi", lotf)
    g = lambda *a: subprocess.run(["git", *a], cwd=rad, capture_output=True, text=True).stdout.strip()   # noqa: E731
    baza = g("merge-base", "HEAD", main)
    if not baza:
        return ["nu există merge-base cu %s" % main]
    try:
        pasi = [ln.strip() for ln in open(os.path.join(d, "pasi.txt"), encoding="utf-8") if ln.strip()]
        rr = list(csv.DictReader(open(os.path.join(d, "jurnal_verificare.csv"), encoding="utf-8")))
    except OSError as e:
        return ["lipsește %s" % os.path.relpath(e.filename, rad)]
    if not pasi:
        return ["pasi.txt e gol: nu există pasul a)"]
    pas = pasi[0]
    ale = [r for r in rr if r["pas"] == pas]
    if not ale:
        return ["nu există rândul pasului a) (%s) în jurnal_verificare.csv" % pas]
    pe_baza = [r for r in ale if r["commit"] == baza]
    if not pe_baza:
        return ["rândul pasului a) (%s) e pe %s, nu pe commitul de bază %s (se produce înainte de primul commit, pe baza lotului)" % (
            pas, ", ".join(sorted({r["commit"][:12] for r in ale})), baza[:12])]
    exista = lambda r: os.path.exists(r["captura"] if os.path.isabs(r["captura"]) else os.path.join(rad, r["captura"]))   # noqa: E731
    if any(r["verdict"] == "trece" and exista(r) for r in pe_baza):
        return []
    return ["rândul pasului a) (%s) pe baza %s: %s" % (pas, baza[:12], "; ".join("verdict „%s”" % r["verdict"] if r["verdict"] != "trece" else "captura %s lipsește" % r["captura"] for r in pe_baza))]


def main_proba(lot=None):
    """`--proba [lot]`: rulează contractul la început și scrie faza „proba_contract” (verde sau rosu). Ieșire 0 = verde."""
    lot = lot or JL.lot_curent()
    ref = proba_refuzuri(RAD, lot)
    fara = proba_fara_oracol(RAD, lot)
    id_ = JL.inceput(lot, "proba_contract", "baza=%s" % git("merge-base", "HEAD", "main")[:12], pid=os.getpid())
    JL.sfarsit(lot, "proba_contract", id_, "rosu" if ref else "verde", "; ".join(ref) or ("unelte, fără oracol" if fara else ""))
    for m in ref:
        print("[publica_lot --proba] REFUZ: " + m)
    if not ref:
        print("[publica_lot --proba] verde: " + ("unelte, fără oracol" if fara else "rândul pasului a) e pe commitul de bază, cu captură"))
    return 1 if ref else 0


def _raspuns(x):
    return (x or "").split(":")[0].strip().lower()


def asertiuni_excluse(pasi_json):
    """Id-urile aserțiunilor pe care verificatorul independent nu le judecă din captură: cheia pdf: sau operatorul interval_px (16.3-A pct.2). `pasi_json` = conținutul lui pasi.json (dict) sau None."""
    return {x["id"] for x in (pasi_json or {}).get("asertiuni", []) if str(x.get("cheie", "")).startswith("pdf:") or x.get("operator") == "interval_px"}


def pasi_json_la(commit, lotf):
    """docs/dovezi/<lot>/pasi.json de la `commit` (None dacă nu există)."""
    t = _fisier_la(commit, "docs/dovezi/%s/pasi.json" % lotf)
    return json.loads("\n".join(t)) if t else None


def csv_stop(rr, lot, c=None, excluse=frozenset()):
    """Rândurile jurnalului (16.3): marcajul HMAC al oracolului valid pe fiecare rând (STOP „verdict în afara oracolului”; scutite loturile din LOTURI_FARA_MARCAJ), cheia unică, iar pe rândurile lui C ale verificatorului
    independent: dezacordul oracol–verificator (verdict „trece”, ambele instanțe „nu corespunde”) și faza „neefectuată” (toate aserțiunile judecabile „nejudecabil”) sau fără răspuns. -> motivele de STOP."""
    if lot in LOTURI_FARA_MARCAJ:
        return []
    stop, vazute = [], set()
    for r in rr:
        if not VP.marcaj_valid(r):
            stop.append("verdict în afara oracolului: rândul %s (sha %s, parcurgerea %s) nu are marcaj valid" % (r.get("pas"), (r.get("commit") or "")[:8], r.get("parcurgere") or "-"))
        k = VP.cheia_unica(r)
        if k in vazute:
            stop.append("cheia %s repetată (captura %s)" % (k, r.get("captura")))
        vazute.add(k)
    grupe = {}
    for r in rr:
        if c and r.get("commit") == c and "haiku" in (r.get("verificator") or "").lower():
            grupe.setdefault(r.get("parcurgere") or "", []).append(r)
    for parc, rands in grupe.items():
        for r in rands:
            r1, r2 = _raspuns(r.get("verificator_independent")), _raspuns(r.get("verificator_independent_2"))
            if not r1 or r1 == "fara_raspuns":
                stop.append("verificatorul independent n-a răspuns pe aserțiunea %s (parcurgerea %s)" % (r["pas"], parc))
            if r["verdict"] == "trece" and r1 == "nu corespunde" and r2 == "nu corespunde":
                stop.append("dezacord oracol–verificator: aserțiunea %s (oracolul: trece; ambele instanțe Haiku: nu corespunde)" % r["pas"])
        # aserțiunile excluse (pdf:, interval_px) nu se numără: cheie și operator, nu textul răspunsului; dacă toate sunt excluse, faza nu e „neefectuată”
        judecabile = [r for r in rands if r.get("pas") not in excluse]
        if judecabile and all(_raspuns(r.get("verificator_independent")) == "nejudecabil" for r in judecabile):
            stop.append("faza verificatorului independent este „neefectuată” (parcurgerea %s: toate aserțiunile sunt nejudecabile)" % parc)
    return stop


def unelte_refuzuri(head, lotf, main="main"):
    """Lotul „unelte” are o listă permisă de fișiere, fixă aici (16.3, pct.0): diff-ul față de merge-base atinge numai căile din UNELTE_PERMISE, docs/dovezi/<lot>/, testele core/test_*.py și ce e numit în
    scripts/praguri_<lot>.txt; un fișier din static/, core/ (altul decât test_*), templates/ sau frontend_test/ nenumit = refuz cu numele lui. -> motivele de refuz."""
    baza = git("merge-base", head, main)
    diff = git("diff", "--name-only", "--no-renames", baza, head).splitlines() if baza else []
    text = "\n".join(_fisier_la(head, "scripts/praguri_%s.txt" % lotf) or [])
    numite = {ln.split()[0] for ln in text.splitlines()[1:] if ln.strip() and "/" in ln.split()[0]}
    ref = []
    for f in diff:
        permis = f.startswith(UNELTE_PERMISE) or f.startswith("docs/dovezi/%s/" % lotf) or (f.startswith("core/test_") and "/" not in f[5:])
        if not permis and f.startswith(UNELTE_INTERZISE) and f not in numite:
            ref.append("%s: lotul „unelte” nu are voie să atingă acest fișier (static/, core/, templates/, frontend_test/ numai dacă e numit în scripts/praguri_%s.txt)" % (f, lotf))
    return ref


def lista_permisa(text):
    """Intrările listei `fisiere_permise` din scripts/praguri_<lot>.txt (16.3-A pct.4): liniile de după rândul care începe cu „fisiere_permise”; textul dintre paranteze se ignoră; o intrare cu „/” la sfârșit e un director.
    -> lista intrărilor, sau None dacă fișierul nu are lista."""
    in_lista, intrari = False, []
    for ln in text.splitlines():
        if ln.startswith("fisiere_permise"):
            in_lista = True
        elif in_lista and ln.strip():
            if not ln[0].isspace():
                break
            intrare = re.sub(r"\(.*?\)", "", ln).strip().split()
            if intrare:
                intrari.append(intrare[0])
    return intrari if in_lista else None


def produs_refuzuri(head, lotf, main="main", text=None):
    """Lotul „produs”: diff-ul merge-base..HEAD atinge numai fișierele din lista `fisiere_permise` a pragurilor lotului (fișier exact sau director cu „/” la sfârșit); orice altceva = refuz cu numele. „CLAUDE.md (numai
    inainte de C)” e permis aici (în diff-ul până la HEAD); după C îl refuză regula strămoșului. `text` = alt conținut al pragurilor (numai calibrări). -> motivele de refuz."""
    if text is None:
        linii = _fisier_la(head, "scripts/praguri_%s.txt" % lotf)
        if linii is None:
            return []
        text = "\n".join(linii)
    lista = lista_permisa(text)
    if lista is None:
        return ["scripts/praguri_%s.txt nu are lista fisiere_permise (un lot «produs» o cere)" % lotf]
    baza = git("merge-base", head, main)
    diff = git("diff", "--name-only", "--no-renames", baza, head).splitlines() if baza else []
    return ["%s: fișier în afara listei fisiere_permise din scripts/praguri_%s.txt" % (f, lotf) for f in diff if not any(f == i or (i.endswith("/") and f.startswith(i)) for i in lista)]


def faze_stop(rows, unelte):
    """Fazele obligatorii din jurnal (rândurile lotului): început și sfârșit neîntrerupt; „publicare” numai cu început. Faza „verificator” (16.3-A pct.1): la un lot „unelte” nu se cere; la un lot «produs» începutul și
    sfârșitul ultimei rulări trebuie să poarte marcajul scris de lansator (scrisă de mână sau copiată = STOP). -> motivele de STOP."""
    stop = []
    for faza in JL.FAZE_OBLIGATORII:
        ev = [r for r in rows if r[1] == faza]
        if faza == "publicare":
            if not any(r[2] == "inceput" for r in ev):
                stop.append("faza „publicare” nu are început")
            continue
        if faza == "verificator" and unelte:
            continue
        sf = {r[6]: r for r in ev if r[2] == "sfarsit"}
        ultimul = [r for r in ev if r[2] == "inceput"][-1:]
        if not ultimul:
            stop.append("faza „%s” lipsește din jurnal" % faza)
        elif ultimul[0][6] not in sf or sf[ultimul[0][6]][5] == "intrerupt":
            stop.append("faza „%s” e fără sfârșit sau întreruptă" % faza)
        elif faza == "verificator" and not (VP.faza_marcata_valida(ultimul[0]) and VP.faza_marcata_valida(sf[ultimul[0][6]])):
            stop.append("faza verificator scrisă de mână (fără marcajul lansatorului; copiată sau editată = nevalid): o scrie numai scripts/lanseaza_verificator.py")
    return stop


def fara_haiku_stop(rr, c):
    """Lotul «produs», la publicare (nu la `--verifica`): jurnalul trebuie să aibă rânduri ale unei parcurgeri cu verificator=haiku pe C (16.3-A pct.1b). -> motivele de STOP."""
    if any(r.get("commit") == c and "haiku" in (r.get("verificator") or "").lower() for r in rr):
        return []
    return ["fără verificator independent pe C: jurnal_verificare.csv nu are nicio parcurgere cu verificator=haiku pe %s" % c[:12]]


def jurnal_verificare_stop(rr, pasi, c, baza, mx, rad=None):
    """Jurnalul verificării pe pas (16.1-C2 pct.3): rândurile pe alt sha decât C sunt ignorate; rândurile pe C trebuie „trece” cu captură existentă, iar fiecare pas are rând pe C;
    rundele verificatorului independent (sha distincte, ≠ baza, cu verificator=Haiku, pe pașii „după”) nu depășesc `mx`. -> motivele de STOP."""
    stop = []
    pe_c = [r for r in rr if r["commit"] == c]
    for r in pe_c:
        if r["verdict"] != "trece":
            stop.append("rândul %s din jurnal_verificare.csv (pe C): %s" % (r["pas"], r["verdict"]))
        if not os.path.exists(r["captura"] if os.path.isabs(r["captura"]) else os.path.join(rad or RAD, r["captura"])):
            stop.append("rândul %s: captura lipsește" % r["pas"])
    stop += ["pasul „%s” nu are rând pe C în jurnal_verificare.csv" % p for p in pasi if p not in {r["pas"] for r in pe_c}]
    # runda = (sha, parcurgere) distinct cu rânduri Haiku pe pașii „după”; a doua instanță Haiku stă pe același rând și nu e rundă nouă (16.3, pct.3)
    runde = {(r["commit"], r.get("parcurgere") or "") for r in rr if "haiku" in r["verificator"].lower() and r["commit"] != baza and (not pasi or r["pas"] in pasi)}
    if len(runde) > mx:
        stop.append("rundele verificatorului: %d > runde_verificator_max %d (cheie lipsă = 0)" % (len(runde), mx))
    return stop


def verifica(lot, sha, comun, sirul_zip):
    """-> listă de motive de STOP (goală = PASS)."""
    lotf = L.lot_fisier(lot)
    stop = []
    # praguri: fișierul există, hash-ul = cel din jurnal la „pornire”
    praguri = os.path.join(RAD, "scripts", "praguri_%s.txt" % lotf)
    rows = [r for r in JL._citeste(JL.cale_jurnal()) if r[0] == lot and len(r) > 8]
    pornire = [r for r in rows if r[1] == "pornire" and r[2] == "inceput"]
    if not pornire:
        return ["lipsă pornire"]
    if not os.path.exists(praguri) or "lipsa_praguri" in [r[5] for r in rows if r[1] == "pornire" and r[2] == "sfarsit"]:
        return ["lipsă praguri"]
    if "praguri_sha256=%s" % L.hash_fisier(praguri) not in pornire[-1][8]:
        stop.append("pragurile s-au modificat după pornire (hash diferit de cel din jurnal)")
    unelte = open(praguri, encoding="utf-8").readline().strip().lower() == "unelte"
    stop += pornire_stop(pornire, lot, unelte)
    stop += oracol_stop(lotf, unelte, pornire[-1])
    stop += proba_stop(rows, lot)
    # poarta: VERDE pe HEAD, rulare completă finală, zero regresii, lot neoprit
    f_stare = os.path.join(comun, "lot_stare_%s.json" % lotf)
    stare = json.load(open(f_stare)) if os.path.exists(f_stare) else {}
    if not stare or stare.get("oprit") or not stare["complete"] or not stare["complete"][-1]["curat"]:
        stop.append("starea lotului nu arată o rulare completă curată (oprit=%s)" % stare.get("oprit"))
    c = stare["complete"][-1]["sha"] if stare and stare["complete"] else sha
    refuzuri, fisiere_c = ancestor_refuzuri(c, sha, lotf)
    stop += ["regula strămoșului: " + m for m in refuzuri]
    # raportul
    raport = os.path.join(ACASA, "lot_%s_raport.md" % lotf)
    if not os.path.exists(raport) or not os.path.getsize(raport):
        stop.append("lipsește raportul %s" % raport)
    else:
        text = open(raport, encoding="utf-8").read()
        if c not in text:
            stop.append("raportul nu conține sha-ul lui C (%s)" % c)
        if c != sha and (sha in text or sha[:8] in text):
            stop.append("raportul conține sha-ul lui HEAD (%s); numește numai C" % sha[:8])
    jv = os.path.join(comun, "poarta_verdicte.log")
    if not any(ln.startswith("VERDE %s " % c) and " completa " in ln for ln in open(jv, encoding="utf-8")) if os.path.exists(jv) else True:
        stop.append("lipsește verdictul VERDE al rulării complete finale pe %s" % c[:8])
    try:
        clase = json.load(open(os.path.join(comun, "lot_picate_%s.json" % lotf)))["clase"]
        for k in C.CURAT:
            if clase.get(k):
                stop.append("clasificarea porții are %d × %s" % (len(clase[k]), k))
    except OSError:
        stop.append("lipsește clasificarea porții")
    # faze obligatorii în jurnal
    stop += faze_stop(rows, unelte)
    # perimetrul uneltelor
    cb = os.path.join(RAD, "docs", "dovezi", L.lot_fisier(L.lot_baza(lot)), "baza.json")
    baza = git("merge-base", sha, "main")
    diff = git("diff", "--name-only", baza, sha).splitlines()
    if not unelte:
        atinse = [f for f in PAZITE if f in diff]
        if atinse:
            stop.append("lotul nu e marcat „unelte”, dar atinge: " + ", ".join(atinse))
    else:
        stop += unelte_refuzuri(sha, lotf)
    if not unelte:
        stop += produs_refuzuri(sha, lotf)
    # manifestul (16.1-C2 pct.1): poate crește numai cu rânduri pentru fișiere de test noi (prezente în diff, absente pe main); orice altă diferență = refuz cu numele
    if os.path.exists(cb):
        ab = json.load(open(cb, encoding="utf-8"))["antet"]
        if ab["manifest_sha256"] != L.hash_fisier(os.path.join(RAD, L.MANIFEST)):
            stop += ["manifestul: " + m for m in L.manifest_refuzuri(DEP or RAD, ab["commit_baza"], modificabile=L.plasa_modificabile(DEP or RAD, lotf, sha))]
    # baza
    if not os.path.exists(cb):
        stop.append("lipsește baza.json")
    else:
        an = json.load(open(cb, encoding="utf-8"))["antet"]
        if an["commit_baza"] != baza:
            stop.append("baza.json e pentru %s, nu pentru %s" % (an["commit_baza"][:8], baza[:8]))
    # reluări
    if stare.get("reluari") and "diff-ul reluărilor" not in (open(raport, encoding="utf-8").read() if os.path.exists(raport) else ""):
        stop.append("a existat reluare, dar raportul nu are secțiunea „diff-ul reluărilor”")
    if stare.get("reluari") and FRAZA_RISC not in open(raport, encoding="utf-8").read():
        stop.append("raportul nu are fraza de risc rezidual a reluărilor")
    # jurnalul verificării pe pas (16.1-C2 pct.3): rândurile pe alt sha decât C rămân în fișier și sunt ignorate; numai rândurile pe C trebuie „trece”, iar fiecare pas are rând pe C
    cv = os.path.join(RAD, "docs", "dovezi", lotf, "jurnal_verificare.csv")
    if os.path.exists(cv):
        pasi_f = os.path.join(RAD, "docs", "dovezi", lotf, "pasi.txt")
        pasi = [ln.strip() for ln in open(pasi_f, encoding="utf-8") if ln.strip()] if os.path.exists(pasi_f) else []
        rr = list(csv.DictReader(open(cv, encoding="utf-8")))
        mx = 0
        for ln in open(praguri, encoding="utf-8"):
            m = re.search(r"runde_verificator_max:\s*(\d+)", ln)
            if m:
                mx = int(m.group(1))
        stop += jurnal_verificare_stop(rr, pasi, c, baza, mx)
        stop += csv_stop(rr, lot, c, asertiuni_excluse(pasi_json_la(c, lotf)))
        if not unelte:
            stop += fara_haiku_stop(rr, c)
    elif not unelte:
        stop.append("lipsește jurnal_verificare.csv")
    # backup-ul uneltelor
    if unelte and not os.path.exists(os.path.join(ACASA, "backup_%s" % lotf, "CLAUDE.md")):
        stop.append("lipsește backup-ul ~/backup_%s/ (scripts/ și CLAUDE.md)" % lotf)
    # ZIP-ul
    if not os.path.exists(sirul_zip):
        stop.append("lipsește ZIP-ul %s" % sirul_zip)
    else:
        z = zipfile.ZipFile(sirul_zip)
        if z.read("sha.txt").decode().strip() != sha:
            stop.append("ZIP-ul nu conține sha-ul publicat")
        if sorted(z.read("fisiere_diff.txt").decode().split()) != sorted(diff):
            stop.append("lista fișierelor din ZIP diferă de diff-ul față de main")
    # praguri numerice: `max <faza> <secunde>`; în lotul de unelte nu sunt
    depasiri, intrerupte = depasiri_praguri(JL.durate(lot), open(praguri, encoding="utf-8").read().splitlines())
    stop += depasiri
    if os.path.exists(raport) and "Rulări „intrerupt” pe fază" not in open(raport, encoding="utf-8").read():
        stop.append("raportul nu dă numărul rulărilor „intrerupt” pe fază (%s)" % (", ".join("%s=%d" % kv for kv in sorted(intrerupte.items())) or "niciuna"))
    return stop


def depasiri_praguri(durate, linii_praguri):
    """-> (STOP-uri, {faza: număr de rulări „intrerupt”}). Comparația `max <faza> <secunde>` ignoră rulările cu rezultatul „intrerupt” (x[4]) [16.7]: o rulare
    întreruptă nu e o rulare terminată peste prag; numărul lor pe fază intră în raport."""
    stop, intrerupte = [], {}
    for x in durate:
        if x[4] == "intrerupt":
            intrerupte[x[0]] = intrerupte.get(x[0], 0) + 1
    for ln in linii_praguri:
        m = re.match(r"max\s+(\S+)\s+(\d+)", ln)
        if m:
            d = [x[5] for x in durate if x[0] == m.group(1) and x[5] != "" and x[4] != "intrerupt"]
            if d and max(d) > int(m.group(2)):
                stop.append("pragul „%s” depășit: %ss > %ss" % (m.group(1), max(d), m.group(2)))
    return stop, intrerupte


def lucru_si_timp(lot):
    """17.5-A: fazele timpului de lucru (`jurnal_lot.py lucru`) și raportul de timp ~/lot_<lot>_timp.md, înaintea ZIP-ului. Nu oprește niciodată publicarea: orice eroare se tipărește (și intră în raportul lotului),
    iar derivarea scrie rândurile într-o singură scriere, deci nu lasă rânduri pe jumătate. -> lista mesajelor (erorile încep cu «EROARE»)."""
    mesaje = []
    try:
        mesaje.append("lucru %s: %d rânduri noi" % (lot, JL.lucru(lot)))
    except Exception as e:  # noqa: BLE001
        mesaje.append("EROARE lucru %s: %s: %s" % (lot, type(e).__name__, e))
    try:
        import raport_timp_lot as RT
        text, fisier = RT.scrie(lot)
        mesaje.append("raport de timp: %s" % (fisier or "lotul nu are rânduri în jurnal"))
    except Exception as e:  # noqa: BLE001
        mesaje.append("EROARE raport de timp %s: %s: %s" % (lot, type(e).__name__, e))
    for m in mesaje:
        print("[publica_lot] " + m)
    return mesaje


def zip_lot(lot, sha, cale):
    baza = git("merge-base", sha, "main")
    diff = git("diff", "--name-only", baza, sha).splitlines()
    lotf = L.lot_fisier(lot)
    with zipfile.ZipFile(cale, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("sha.txt", sha + "\n")
        z.writestr("fisiere_diff.txt", "\n".join(diff) + "\n")
        for f in diff:
            if os.path.exists(os.path.join(RAD, f)):
                z.write(os.path.join(RAD, f), "fisiere/" + f)
        for extra in (os.path.join(ACASA, "lot_%s_raport.md" % lotf), os.path.join(ACASA, "lot_%s_timp.md" % lotf)):
            if os.path.exists(extra):
                z.write(extra, os.path.basename(extra))
        z.writestr("jurnal_lot.txt", "\n".join("%-20s %-10s %s -> %s  %ss" % (f, r, b, s, sec) for f, i, b, s, r, sec in JL.durate(lot)) + "\n")


def main_verifica(c, head, lot=None, csv_cale=None):
    """`--verifica <C> <HEAD> [lot] [--csv fișier]`: regula strămoșului, lista permisă a lotului „unelte” și marcajul rândurilor din jurnalul verificării; fără publicare, fără scrieri; judecă depozitul din
    directorul curent (hook-urile git o chemă de aici). `--csv` (numai calibrări) ia alt jurnal decât al lotului."""
    global DEP
    DEP = os.getcwd()
    lot = lot or JL.lot_curent()
    lotf = L.lot_fisier(lot)
    head = git("rev-parse", head)
    c = git("rev-parse", c)
    refuzuri, fisiere = ancestor_refuzuri(c, head, lotf)
    praguri = _fisier_la(head, "scripts/praguri_%s.txt" % lotf) or [""]
    if praguri[0].strip().lower() == "unelte":
        refuzuri += unelte_refuzuri(head, lotf)
    else:
        refuzuri += produs_refuzuri(head, lotf)
    cv = csv_cale or os.path.join(DEP, "docs", "dovezi", lotf, "jurnal_verificare.csv")
    if os.path.exists(cv):
        refuzuri += csv_stop(list(csv.DictReader(open(cv, encoding="utf-8"))), lot, c, asertiuni_excluse(pasi_json_la(head, lotf)))
    for m in refuzuri:
        print("[publica_lot --verifica] REFUZ: " + m)
    if refuzuri:
        return 1
    print("[publica_lot --verifica] PASS C=%s HEAD=%s fisiere=%s" % (c, head, ",".join(fisiere) or "-"))
    return 0


def controleaza_csv(cale):
    """`--controleaza <csv>`: controlul încrucișat (captura există, cheia unică, marcajul valid; loturile scutite numai după existența capturii). Ieșire 1 + rândul numit la prima abatere."""
    rr = list(csv.DictReader(open(cale, encoding="utf-8")))
    ref = []
    for r in rr:
        ref += VP.refuzuri_rand(r, RAD, exceptat=r.get("lot") in LOTURI_FARA_MARCAJ)
    vazute = set()
    for r in rr:
        if r.get("parcurgere"):
            k = VP.cheia_unica(r)
            if k in vazute:
                ref.append("cheia %s repetată (captura %s)" % (k, r.get("captura")))
            vazute.add(k)
    for m in ref:
        print("REFUZ: " + m)
    return 1 if ref else 0


def main():
    if "--csv" in sys.argv and "--verifica" not in sys.argv:
        print("[publica_lot] REFUZ: „--csv” e numai pentru calibrări (--verifica); la publicare se folosește jurnalul lotului")
        return 1
    if len(sys.argv) == 3 and sys.argv[1] == "--controleaza":
        return controleaza_csv(sys.argv[2])
    if len(sys.argv) in (2, 3) and sys.argv[1] == "--proba":
        return main_proba(sys.argv[2] if len(sys.argv) == 3 else None)
    if len(sys.argv) >= 4 and sys.argv[1] == "--verifica":
        a = sys.argv[2:]
        cv = None
        if "--csv" in a:
            i = a.index("--csv")
            cv = a[i + 1] if i + 1 < len(a) else None
            a = a[:i] + a[i + 2:]
        return main_verifica(a[0], a[1], a[2] if len(a) > 2 else None, cv)
    lot = JL.lot_curent()
    lotf = L.lot_fisier(lot)
    sha = git("rev-parse", "HEAD")
    comun = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    sirul_zip = os.path.join(ACASA, "lot_%s.zip" % lotf)
    lucru_si_timp(lot)
    zip_lot(lot, sha, sirul_zip)
    stop = verifica(lot, sha, comun, sirul_zip)
    f_stare = os.path.join(comun, "lot_stare_%s.json" % lotf)
    stare = json.load(open(f_stare)) if os.path.exists(f_stare) else {}
    c = stare["complete"][-1]["sha"] if stare.get("complete") else sha
    if stop:
        for m in stop:
            print("[publica_lot] STOP: " + m)
        print("OPRIT — gata: %s nepublicat, %s" % (lot, stop[0]))
        return 1
    with open(os.path.join(comun, "publica_verdicte.log"), "a", encoding="utf-8") as f:
        f.write("PASS %s %s %s C=%s fisiere=%s\n" % (sha, lot, JL._acum(), c, ",".join(ancestor_refuzuri(c, sha, lotf)[1]) or "-"))
    print("[publica_lot] PASS %s (lot %s); ZIP %s" % (sha, lot, sirul_zip))
    return 0


if __name__ == "__main__":
    sys.exit(main())
