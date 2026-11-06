# -*- coding: utf-8 -*-
"""scripts/lanseaza_verificator.py — lansatorul parcursului și al verificatorului independent (16.1-C3 pct.2, rescris în 16.3 pct.1 și 3). Un parcurs pornește numai de aici (Code nu rulează Playwright pe 8019 altfel).
  lanseaza_verificator.py --lot <lot> --parcurs <fișier> --parcurgere <etichetă> --verificator code|haiku --pasi-txt <fișier> --pasi-json <fișier> [--csv <fișier>] [--utilizator <email>]
                          [--baza http://127.0.0.1:8019] [--scenariu <fișier> --sectiune F017] [--formate <fișier>...] [--iesire <fișier>] [--jurnal <fișier>]
Ia lacătul pe iconta_test și 8019 (scripts/lacat_test.py). Parcursul (docs/dovezi/<lot>/parcurs_<lot>.py, al lui Code) are punctul de intrare `ruleaza(pagina, ctx)`; importă numai playwright, biblioteca standard și
scripts/verifica_pas.py (orice alt import = refuz la lansare, cu numele modulului). Pagina e deschisă aici, pe 8019, cu sesiunea contului injectată (scripts/sesiune_test.py), cu ceasul fix al probelor (core/ceas_proba.py) și cu
variabilele de mediu ale probei (aceleași ca scripts/e2e_poarta.py::_env_test); ctx = lot, parcurgere, verificator, pasi_json, csv, sha (PARCURS_SHA, din HEAD al worktree-ului), director (unde parcursul salvează ce
descarcă prin clic). Parcursul nu compară nimic și nu scrie verdicte: după fiecare pas predă pagina vie lui verifica_pas.verifica_pagina.
Cu --verificator haiku, după parcurs, agentul Haiku 5.5 primește scenariul, pasi_<lot>.txt și un Read restrâns la directorul capturilor lui; judecă fiecare aserțiune față de coloana „descriere” și captură: corespunde / nu corespunde /
nejudecabil din captură (interval_px = nejudecabil automat). Răspunsul intră în coloana „verificator_independent” (prin oracol, cu marcaj). La „nu corespunde” pe o aserțiune cu verdictul „trece”, o a doua instanță, cu context
proaspăt, primește numai aserțiunea și captura ei (coloana „verificator_independent_2”); STOP (dezacord oracol–verificator) numai dacă și a doua spune „nu corespunde”. Dacă toate aserțiunile judecabile sunt „nejudecabil”: faza
verificatorului e „neefectuată” = STOP.
Faza în jurnal (16.3-A pct.1): lansatorul scrie el, cu marcaj HMAC (verifica_pas.scrie_faza), „verificator | inceput” înainte de parcurs și „verificator | sfarsit” după răspunsul ultimei instanțe Haiku (rezultat „parcurs” =
toate răspunsurile primite; „intrerupt” = lansatorul a ieșit cu eroare), cu numărul aserțiunilor corespunde / nu corespunde / nejudecabil în detalii; la --verificator code scrie la fel faza „parcurs_code”. --jurnal = alt fișier
decât jurnalul comun (calibrări). Aserțiunile cu cheia pdf: se scriu direct „nejudecabil din captură (pdf)”, ca interval_px: nu se dau agentului (16.3-A pct.2).
Limită declarată (CLAUDE.md): „fără acces la diff” = directorul de lucru nu e depozit și nu conține diff; agentul rulează ca utilizatorul, pe același server, deci e o izolare de proces, nu o barieră.
CLAUDE_BIN (calibrare) înlocuiește executabilul `claude`; fără el, executabilul se caută în PATH și în ~/.local/bin."""
import argparse
import ast
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import types

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
import lacat_test as LT  # noqa: E402

RAD = os.path.dirname(AICI)
MODEL = "claude-haiku-5-5"
RASPUNSURI = ("corespunde", "nu corespunde", "nejudecabil")
#: importurile permise unui parcurs, în afara bibliotecii standard
IMPORTURI_PERMISE = ("playwright", "verifica_pas")
INSTRUCTIUNE = ("Ești verificatorul independent. Pentru fiecare ASERȚIUNE de mai jos, uită-te la captura ei (fișierul indicat, citit cu Read) și spune dacă ceea ce se vede pe ecran CORESPUNDE descrierii aserțiunii. "
                "Judeci numai după descriere și captură; nu cunoști și nu ghicești vreun alt criteriu. Pentru fiecare aserțiune răspunzi cu una din trei: „corespunde”, „nu corespunde”, „nejudecabil” "
                "(captura nu arată ce cere descrierea). Nu modifici nimic. Ultimul lucru din răspuns este o listă JSON, fără alt text după ea: "
                '[{"id": "<id>", "raspuns": "corespunde|nu corespunde|nejudecabil", "motiv": "<o frază>"}, ...] — câte un element pentru fiecare aserțiune.')


def caut_claude():
    """Executabilul `claude`: CLAUDE_BIN, apoi PATH, apoi ~/.local/bin; None dacă nu există (se raportează, nu se ocolește)."""
    if os.environ.get("CLAUDE_BIN"):
        return os.environ["CLAUDE_BIN"]
    return shutil.which("claude") or next((c for c in (os.path.expanduser("~/.local/bin/claude"),) if os.access(c, os.X_OK)), None)


def refuzuri_fisiere(cai):
    """Fișierele date agentului: niciun diff și nimic din .git. -> motivele de refuz."""
    ref = []
    for c in cai:
        if not os.path.isfile(c):
            ref.append("%s: nu există" % c)
        elif c.lower().endswith((".diff", ".patch")) or "/.git/" in os.path.abspath(c) + "/":
            ref.append("%s: diff sau cale din .git — agentul nu are acces la diff" % c)
    return ref


def importuri_parcurs(cale):
    """Modulele (rădăcina numelui) importate de un parcurs, cu numele celor nepermise. -> (toate, nepermise)."""
    arbore = ast.parse(open(cale, encoding="utf-8").read(), cale)
    module = []
    for n in ast.walk(arbore):
        if isinstance(n, ast.Import):
            module += [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom):
            module.append(("." * n.level) + (n.module or ""))
    nepermise = []
    for m in module:
        radacina = m.split(".")[0]
        if m.startswith("."):
            nepermise.append(m)
        elif m in ("scripts.verifica_pas", "verifica_pas") or radacina in IMPORTURI_PERMISE or radacina in sys.stdlib_module_names:
            continue
        else:
            nepermise.append(m)
    return module, nepermise


def sectiune(text, cod):
    """Rândurile scenariului de la antetul cu codul EXACT `cod` până la următorul antet (literă + 2–3 cifre + „ · ”: F017, X05); cod negăsit = text gol."""
    rez, in_ = [], False
    for ln in text.splitlines():
        m = re.match(r"([A-Z]\d{2,3}) · ", ln)
        if m:
            in_ = m.group(1) == cod
        if in_:
            rez.append(ln)
    return "\n".join(rez)


def text_scenariu(cale, cod):
    """-> (textul scenariului, motivul refuzului sau None): fără cod fișierul întreg, cu cod numai secțiunea lui; singura sursă a regulii."""
    if not cod:
        return (open(cale, encoding="utf-8").read() if cale else ""), None
    if not cale:
        return "", "--sectiune cere --scenariu"
    text = open(cale, encoding="utf-8").read()
    sec = sectiune(text, cod)
    if sec:
        return sec, None
    coduri = [m.group(1) for m in (re.match(r"([A-Z]\d{2,3}) · ", ln) for ln in text.splitlines()) if m]
    return "", "secțiunea %s nu e în %s (coduri găsite: %s)" % (cod, cale, ", ".join(coduri))


def mediul_probei(baza_temp):
    """Variabilele de mediu ale probei: aceleași ca scripts/e2e_poarta.py::_env_test (stand-in-urile ANAF/SPV/BNR/AI/WhatsApp, cutia de email, directoarele probei) și ceasul fix al probelor (core/ceas_proba.py)."""
    os.environ["E2E_TEMP"] = baza_temp   # e2e_poarta.TEMP se citește la import: același director ca al serverului pornit de porneste_8019.sh
    import e2e_poarta
    env = e2e_poarta._env_test()
    nume = ("ICONTA_EMAIL_CUTIE", "ICONTA_AI_SIMULAT", "ICONTA_ANAF_SIMULAT", "ICONTA_WHATSAPP_SIMULAT", "ICONTA_BON_DIR", "ICONTA_FISIERE_DIR")
    mediu = {k: env[k] for k in nume if k in env}
    sys.path.insert(0, RAD)
    from core import ceas_proba
    mediu["CEAS_FIX"] = ceas_proba.MOMENT_REF.isoformat()
    return mediu, ceas_proba


def ruleaza_parcurs(a, ctx, mediu, ceas):
    """Deschide pagina pe 8019 cu sesiunea injectată și ceasul fix, încarcă parcursul și îl rulează."""
    import sesiune_test
    from playwright.sync_api import sync_playwright
    script_sesiune = sesiune_test.sesiune(a.utilizator)
    spec = importlib.util.spec_from_file_location("parcurs_lot", a.parcurs)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    os.makedirs(ctx.director, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            c = b.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
            c.clock.set_fixed_time(ceas.MOMENT_REF)
            c.add_init_script(script_sesiune)
            pagina = c.new_page()
            pagina.goto(a.baza + "/", wait_until="load", timeout=30000)
            modul.ruleaza(pagina, ctx)
        finally:
            b.close()


def _claude(cmd, prompt, cwd):
    return subprocess.run(cmd, input=prompt, cwd=cwd, capture_output=True, text=True)


def _comanda(binar, director_capturi):
    """Agentul are o singură unealtă, Read, și numai pe directorul capturilor lui (restul e refuzat, fără întrebări)."""
    return [binar, "-p", "--model", MODEL, "--tools", "Read", "--allowedTools", "Read(//%s/**)" % director_capturi.strip("/"), "--permission-mode", "dontAsk", "--no-session-persistence"]


def parseaza_raspuns(text):
    """Lista JSON de la sfârșitul răspunsului: {id: (raspuns, motiv)}; ce nu se poate citi lipsește (-> „fara_raspuns”)."""
    m = list(re.finditer(r"\[\s*\{.*?\}\s*\]", text, re.S))
    if not m:
        return {}
    try:
        lista = json.loads(m[-1].group(0))
    except ValueError:
        return {}
    return {str(x.get("id")): (str(x.get("raspuns", "")).strip().lower(), str(x.get("motiv", ""))) for x in lista if isinstance(x, dict)}


def linie_asertiune(a, cap):
    return "ASERȚIUNEA %s | ecran: %s | descriere: %s | captura: %s" % (a["id"], a.get("ecran", ""), a.get("descriere", ""), cap)


def judeca(binar, asertiuni, dir_capturi, scenariu, pasi_txt, lucru):
    """Prima instanță, pe toate aserțiunile judecabile. -> {id: (raspuns, motiv)}."""
    prompt = INSTRUCTIUNE + "\n\n== SCENARIUL ==\n%s\n\n== PAȘII (fișierul arhitectului) ==\n%s\n\n== ASERȚIUNILE DE JUDECAT ==\n%s\n" % (
        scenariu, pasi_txt, "\n".join(linie_asertiune(a, a["_cap"]) for a in asertiuni))
    r = _claude(_comanda(binar, dir_capturi), prompt, lucru)
    return parseaza_raspuns(r.stdout), r


def judeca_a_doua(binar, a, dir_capturi, lucru):
    """A doua instanță: context proaspăt, numai aserțiunea și captura ei."""
    prompt = INSTRUCTIUNE + "\n\n== ASERȚIUNEA DE JUDECAT ==\n%s\n" % linie_asertiune(a, a["_cap"])
    r = _claude(_comanda(binar, dir_capturi), prompt, lucru)
    return parseaza_raspuns(r.stdout).get(a["id"], ("fara_raspuns", (r.stdout + r.stderr)[-200:])), r


def descrieri(pasi_txt_text):
    import oracol_pasi as OP
    return {x["id"]: x for x in OP.parseaza(pasi_txt_text)[0]}


def verificator_independent(a, ctx, csv_, binar, iesire):
    """Haiku peste rândurile parcurgerii. -> (cod de ieșire, rânduri de raport)."""
    import verifica_pas as VP
    rapoarte = []
    randuri = [r for r in VP.randuri_csv(csv_) if (r["lot"], r.get("parcurgere"), r["commit"], r["verificator"]) == (ctx.lot, ctx.parcurgere, ctx.sha, ctx.verificator)]
    if not randuri:
        return 1, ["verificatorul independent: parcursul n-a scris niciun rând (parcurgere %s, sha %s)" % (ctx.parcurgere, ctx.sha[:8])], None
    txt = open(a.pasi_txt, encoding="utf-8").read()
    desc = descrieri(txt)
    chei = {x["id"]: x.get("cheie", "") for x in json.load(open(a.pasi_json, encoding="utf-8"))["asertiuni"]}
    dir_cap = os.path.abspath(os.path.join(ctx.director, "capturi"))
    scenariu = text_scenariu(a.scenariu, a.sectiune)[0]
    lucru = tempfile.mkdtemp(prefix="verificator_")
    try:
        de_judecat, rez1, rez2 = [], {}, {}
        for r in randuri:
            d = dict(desc.get(r["pas"], {"id": r["pas"]}))
            cap = r["captura"] if os.path.isabs(r["captura"]) else os.path.join(RAD, r["captura"])
            d["_cap"] = os.path.abspath(cap)
            if d.get("operator") == "interval_px":
                rez1[r["pas"]] = ("nejudecabil", "interval_px: măsurat de oracol, nu se judecă din captură")
            elif chei.get(r["pas"], "").startswith("pdf:"):
                rez1[r["pas"]] = ("nejudecabil din captură (pdf)", "")
            elif r["verdict"] == "neexecutat" or not os.path.exists(cap):
                rez1[r["pas"]] = ("nejudecabil", "pasul nu s-a executat sau captura lipsește")
            else:
                de_judecat.append(d)
        if de_judecat:
            r1, proc = judeca(binar, de_judecat, dir_cap, scenariu, txt, lucru)
            rapoarte.append("[haiku, instanța 1] cod %s\n%s" % (proc.returncode, (proc.stdout + proc.stderr).strip()[-8000:]))
            for d in de_judecat:
                rez1[d["id"]] = r1.get(d["id"], ("fara_raspuns", "agentul n-a răspuns pe această aserțiune"))
        stare = {r["pas"]: r for r in randuri}
        for d in de_judecat:
            if rez1[d["id"]][0] == "nu corespunde" and stare[d["id"]]["verdict"] == "trece":
                rez2[d["id"]], proc2 = judeca_a_doua(binar, d, dir_cap, lucru)
                rapoarte.append("[haiku, instanța 2 pe %s] %s" % (d["id"], rez2[d["id"]]))
        for r in randuri:
            i = r["pas"]
            VP.completeaza_independent(csv_, ctx.lot, ctx.parcurgere, ctx.sha, ctx.verificator, i, "%s: %s" % rez1[i] if rez1[i][1] else rez1[i][0],
                                       ("%s: %s" % rez2[i] if rez2[i][1] else rez2[i][0]) if i in rez2 else None)
        judecate = [rez1[d["id"]][0] for d in de_judecat]
        dezacorduri = [i for i in rez2 if rez2[i][0] == "nu corespunde"]
        # numai aserțiunile care se dau agentului contează pentru „neefectuată”; interval_px și pdf: sunt excluse prin operator și cheie (nu prin textul răspunsului)
        exclus = lambda i: desc.get(i, {}).get("operator") == "interval_px" or chei.get(i, "").startswith("pdf:")   # noqa: E731
        de_dat = [r["pas"] for r in randuri if not exclus(r["pas"])]
        final = [rez2[i][0] if i in rez2 else rez1[i][0] for i in rez1]
        contor = (final.count("corespunde"), final.count("nu corespunde"), sum(1 for x in final if x.startswith("nejudecabil")), final.count("fara_raspuns"))
        cod = 0
        if dezacorduri:
            rapoarte.append("STOP dezacord oracol–verificator: %s" % ", ".join(dezacorduri))
            cod = 1
        if de_dat and (not judecate or all(x == "nejudecabil" for x in judecate)):
            rapoarte.append("STOP verificatorul independent: neefectuată (toate aserțiunile judecabile sunt „nejudecabil”)")
            cod = 1
        rapoarte.append("răspunsuri: " + "; ".join("%s=%s" % (i, rez1[i][0]) for i in rez1) + " | nejudecabile: %d din %d" % (sum(1 for x in rez1.values() if x[0] == "nejudecabil"), len(rez1)))
        return cod, rapoarte, contor
    finally:
        shutil.rmtree(lucru, ignore_errors=True)


def _la_sigterm(semnal, cadru):
    raise SystemExit(128 + semnal)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lot", required=True)
    ap.add_argument("--parcurs", required=True)
    ap.add_argument("--parcurgere", required=True)
    ap.add_argument("--verificator", required=True, choices=("code", "haiku"))
    ap.add_argument("--pasi-txt", required=True)
    ap.add_argument("--pasi-json", required=True)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--utilizator", default="dovada.71507@sesiuneab.test")
    ap.add_argument("--baza", default="http://127.0.0.1:8019")
    ap.add_argument("--scenariu", default=None)
    ap.add_argument("--sectiune", default=None)
    ap.add_argument("--formate", nargs="*", default=[])
    ap.add_argument("--iesire", default=None)
    ap.add_argument("--jurnal", default=None, help="jurnalul de faze al calibrărilor (implicit jurnalul comun)")
    ap.add_argument("--fara-parcurs", action="store_true", help="numai verificatorul independent, peste rândurile deja scrise (reluare)")
    a = ap.parse_args(argv)
    if a.jurnal:
        os.environ["LOT_JURNAL"] = os.path.abspath(a.jurnal)
    import verifica_pas as VP
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    faza = "verificator" if a.verificator == "haiku" else "parcurs_code"
    # 16.4 pct.2 (C221): SIGTERM devine ieșire normală, ca `finally` să scrie sfârșitul „intrerupt” marcat (fără handler procesul moare fără sfârșit)
    signal.signal(signal.SIGTERM, _la_sigterm)
    id_ = VP.scrie_faza(a.lot, faza, "inceput", detalii="parcurgere=%s" % a.parcurgere, sha=sha)
    rezultat, detalii = "intrerupt", "lansatorul a ieșit cu eroare"
    try:
        cod, complet, contor = _lanseaza(a, sha, VP)
        if complet:
            rezultat, detalii = "parcurs", "corespunde/nu corespunde/nejudecabil=%d/%d/%d parcurgere=%s" % (contor[:3] + (a.parcurgere,))
        return cod
    finally:
        VP.scrie_faza(a.lot, faza, "sfarsit", rezultat, id_, detalii, sha=sha)


def _lanseaza(a, sha, VP):
    """-> (cod de ieșire, faza e completă: parcursul n-a căzut și, la haiku, toate răspunsurile au venit, contorul corespunde / nu corespunde / nejudecabil)."""
    cai = [a.parcurs, a.pasi_txt, a.pasi_json] + ([a.scenariu] if a.scenariu else []) + a.formate
    ref = refuzuri_fisiere(cai)
    if ref:
        print("[lanseaza_verificator] REFUZ: " + "; ".join(ref))
        return 1, False, (0, 0, 0, 0)
    _, motiv = text_scenariu(a.scenariu, a.sectiune)
    if motiv:
        print("[lanseaza_verificator] REFUZ: " + motiv)
        return 1, False, (0, 0, 0, 0)
    _, nepermise = importuri_parcurs(a.parcurs)
    if nepermise:
        print("[lanseaza_verificator] REFUZ: parcursul importă module nepermise: %s (permise: playwright, biblioteca standard, verifica_pas)" % ", ".join(sorted(set(nepermise))))
        return 1, False, (0, 0, 0, 0)
    lotf = VP.JL.L.lot_fisier(a.lot)
    csv_ = os.path.abspath(a.csv or os.path.join(RAD, "docs", "dovezi", lotf, "jurnal_verificare.csv"))
    binar = None
    if a.verificator == "haiku":
        binar = caut_claude()
        if not binar:
            print("[lanseaza_verificator] claude: command not found (nici în PATH, nici în ~/.local/bin) — se raportează")
            return 127, False, (0, 0, 0, 0)
    if LT.ia(os.getpid(), "lanseaza_verificator.py"):   # refuz cu pid-ul care ține lacătul (mesajul îl tipărește lacat_test)
        return 1, False, (0, 0, 0, 0)
    os.environ["LACAT_TEST_PID"] = str(os.getpid())
    os.environ["PARCURS_SHA"] = sha          # citit de verifica_pas.sha_curent(): nimeni altcineva nu-l dă
    os.environ["ICONTA_RAD"] = RAD
    mediu, ceas = mediul_probei("/tmp/verificator_design")
    os.environ.update(mediu)
    ctx = types.SimpleNamespace(lot=a.lot, parcurgere=a.parcurgere, verificator=a.verificator, pasi_json=os.path.abspath(a.pasi_json), csv=csv_, sha=sha,
                                director=VP.director_parcurgere(csv_, a.parcurgere, a.verificator))
    cod, iesire, complet, contor = 0, [], True, (0, 0, 0, 0)
    if not a.fara_parcurs:
        try:
            ruleaza_parcurs(a, ctx, mediu, ceas)
        except Exception as e:   # noqa: BLE001 — parcursul a căzut: se raportează, rândurile deja scrise rămân  # invariant-intern-ok: lansator
            iesire.append("parcursul a căzut: %s: %s" % (type(e).__name__, e))
            cod, complet = 1, False
    if a.verificator == "haiku":
        c2, rap, contor = verificator_independent(a, ctx, csv_, binar, a.iesire)
        cod = cod or c2
        iesire += rap
        if contor is None or contor[3]:   # niciun rând de judecat sau o aserțiune fără răspuns: nu toate răspunsurile au venit
            complet = False
    text = "\n".join(iesire)
    if a.iesire:
        open(a.iesire, "w", encoding="utf-8").write(text + "\n")
    print(text)
    return cod, complet, contor


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
