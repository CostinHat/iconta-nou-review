# -*- coding: utf-8 -*-
"""scripts/verificator_design.py — uneltele VERIFICATORULUI DE DESIGN pe criteriul „migrat” (comanda 15.1-E1, R5 / R6 / R7).

Verificatorul independent (un subagent, promptul fix din `scripts/verificator_design_prompt.txt`) nu rulează niciodată pe producție:
rulează pe serverul de lucru, portul 8019, pe baza de TEST, cu copia firmelor de test (`scripts/dovada_firme_test.py --cloneaza`).
Unealta asta pornește / oprește serverul și măsoară un ecran: PIESELE (clase DS, înălțimi, rânduri), nu pixelii; criteriul rândurilor a–h
e scris o singură dată, în `RANDURI` de mai jos (promptul îl repetă cuvânt cu cuvânt, `core/test_verificator_design_prompt.py` le păzește
identice). Un singur rând PICĂ = ecranul e nemigrat.

  python scripts/verificator_design.py porneste            serverul de lucru pe 8019, din commitul curent (arbore curat), pe baza de TEST
  python scripts/verificator_design.py opreste
  python scripts/verificator_design.py prompt <director> <ecran>...   promptul fix, cu lista de ecrane și directorul capturilor
  python scripts/verificator_design.py lista               ecranele din registru (core/catalog_ecrane.json)
  python scripts/verificator_design.py ecran "<nume>" <LATxINALT> <director> [<director_png>]
                                                           deschide ecranul ca un contabil, scrie `<director>/<slug>_<LAT>x<INALT>.png` și `.json`
                                                           (măsurătorile și verdictul mecanic pe rândurile a–h) și le tipărește
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
import unicodedata

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

PORT = 8019
TEMP = "/tmp/verificator_design"
STARE = os.path.join(TEMP, "stare.json")
STARE_COPIE = os.path.expanduser("~/.cache/iconta_dovada")
REGISTRU = os.path.join(RAD, "core", "catalog_ecrane.json")
MASURI = os.path.join(RAD, "scripts", "verificator_design_masuri.js")

#: Criteriul „migrat” (comanda 15.1-E1 pct.2, R7), cuvânt cu cuvânt. Cheia = litera rândului.
RANDURI = {
    "a": "bara de sus: 56 px, fără traseu, firma sau cabinetul în lucru cu CUI, numele ferestrei, căutarea; traseu înseamnă două sau mai multe "
         "ecrane vizitate înșiruite — un singur „›” urmat de numele ferestrei curente NU e traseu; la Panou Admin, unde nu e nicio firmă sau "
         "cabinet în lucru, contextul e „Panou Admin”, fără CUI; „✕” (închidere) de 40 × 40, exact unul, ultimul element din bară, în dreapta sus, "
         "pe FIECARE fereastră de lucru și pe cele mici; „←” nu se judecă: apare numai unde există un pas înapoi real (fereastră deschisă din alta "
         "sau cu pas intern), altfel fereastra are numai „✕”",
    "b": "fereastra de lucru pe tot ecranul la 1920 × 1080 și 1366 × 768, un singur loc de derulare (tabelul lung), bara de jos fixă 72 px "
         "cu un singur buton principal L (cu data-actiune-principala); bara nu are „Renunță”, în afara ferestrelor din PASTREAZA_RENUNTA (fără „←” activ "
         "în starea formularului sau cu „Renunță” cu efect propriu; revenirea e „←” din antet, „✕” închide); „Închide” și „Renunță” nu sunt "
         "acțiune principală, oricum ar fi colorate; butonul principal inactiv cu motiv cât timp acțiunea nu e posibilă; acțiunea principală a ferestrei "
         "apare o singură dată pe ecran: niciun buton vizibil din conținut (în afara tabelelor, template și details) nu are același text ca butonul "
         "principal din bara de jos; excepție (stare sau meniu "
         "de butoane, pe nume, lista din raport): bara fără buton principal și fără „Renunță”",
    "c": "orice listă de înregistrări e tabelul DS: cap ≥ 40 px, rând ≥ 44 px (cu rândul care se rupe, înălțimea crește), zebra, starea doar în coloana „Stare”, cel mult 2 acțiuni XS pe "
         "rând, subsol 44 px (rândul de totaluri fix, bara-fixa, nu e o listă de înregistrări); nicio celulă cu dată sau sumă tăiată",
    "d": "orice avertisment sau explicație secundară e card-rezumat de 44 px cu detaliile pliate; orice semnal e un rând de 36 px (cel mult două rânduri, textul întreg, fără „…”) cu „ce e de "
         "făcut” pliat; niciun paragraf explicativ mai lung de un rând nepliat; un card-rezumat gri (neutru, informativ) e valid; cardurile de eroare "
         "rămân la vedere și nu se numără, din celelalte cel mult 2 la vedere (restul sub „Semnale (n)”); un semnal sau card al cărui text spune "
         "„deschide X” sau „mergi la X” are butonul care deschide X",
    "e": "nicio acțiune în casete de text sau în mijlocul conținutului; acțiune = buton, navigare = link",
    "f": "titlurile de secțiune fără majuscule (numele proprii — firme, cabinete — nu sunt titluri); titlurile de grup 14 px majuscule gri; textele din catalog, cu diacritice, pluralul după număr, "
         "același mesaj o singură dată pe ecran",
    "g": "date, sume, perioade, firma prin funcția unică (un cod de cont analitic, ca 4428.01, nu e o sumă)",
    "h": "cota TVA ca grup cu cotele la data documentului plus categoriile fără TVA; nicio listă derulantă sub 7 variante; nimic „— alege —” sau opțiune goală",
}


#: [17.3] Ferestrele care păstrează „Renunță” în bara de jos, pe titlul din `.fir-acum`: aceleași ca `static/js/cadru.js::PASTREAZA_RENUNTA` și ca rândurile «fără ←» / «efect propriu: da»
#: din docs/dovezi/17_3/inapoi.txt. Intersecția cu EXCEPTII_B e goală; dacă nu, EXCEPTII_B are prioritate.
PASTREAZA_RENUNTA = ["Încasări/plăți", "Invitații cabinete", "Notificări", "Pachete lunare"]


#: Ecranele fără acțiune principală (stare sau meniu de butoane), pe nume — comanda 15.1-E5 pct.1; lista intră în raport. Aceleași ferestre ca
#: `static/js/cadru.js::FARA_ACTIUNE_PRINCIPALA`.
EXCEPTII_B = {"Sinteza zilei": "stare", "Capacitate": "stare", "Supervizor": "stare", "Declarații lucrate": "stare",
              "Firme": "meniu", "Facturi F1": "meniu", "Operațiuni speciale F1": "meniu", "Activitate": "meniu", "Setări cont": "meniu",
              "Migrare cabinet": "meniu", "Ghiduri": "meniu", "Panou Admin — Anunțuri": "meniu"}


# ── serverul de lucru ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _raspunde():
    import urllib.request
    try:
        return urllib.request.urlopen("http://127.0.0.1:%d/" % PORT, timeout=3).status == 200
    except Exception:  # noqa: BLE001
        return False


def porneste():
    if _raspunde():
        print("[verificator design] portul %d răspunde deja" % PORT)
        return 0
    if not os.path.exists(os.path.join(STARE_COPIE, "stare.json")):
        print("[verificator design] copia firmelor de test nu există: rulează întâi scripts/dovada_firme_test.py --cloneaza", file=sys.stderr)
        return 2
    os.environ["E2E_TEMP"] = TEMP           # înaintea importului: `e2e_poarta.TEMP` se citește la import
    import e2e_poarta
    from dovada_firme_test import tinta_de_test
    env = e2e_poarta._env_test()
    tinta_de_test(env)                      # refuză dacă mediul nu e dovedit de test
    git = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    arb = e2e_poarta._exporta(False)        # indexul = ce se comite (arborele de lucru murdar nu se verifică)
    py = os.path.join(RAD, "venv", "bin", "python")
    r = subprocess.run([py, "scripts/publica_static.py", "--din-arbore"], cwd=arb, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print("[verificator design] publicarea staticului a eșuat: " + (r.stdout + r.stderr)[-400:], file=sys.stderr)
        return 3
    for k in ("ICONTA_AI_SIMULAT", "ICONTA_ANAF_SIMULAT", "ICONTA_BON_DIR"):
        os.makedirs(env[k], exist_ok=True)
    log = open(os.path.join(TEMP, "uvicorn.log"), "w")
    app = subprocess.Popen([py, "-m", "uvicorn", "main:app", "--port", str(PORT)], cwd=arb, env=env, stdout=log, stderr=subprocess.STDOUT,
                           start_new_session=True)
    for _ in range(120):
        if _raspunde():
            break
        time.sleep(2)
    else:
        print("[verificator design] aplicația n-a răspuns pe %d (vezi %s/uvicorn.log)" % (PORT, TEMP), file=sys.stderr)
        return 3
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    json.dump({"pid": app.pid, "sha": sha, "arbore_murdar": bool(git)}, open(STARE, "w"))
    print("[verificator design] serverul de lucru pe %d, commit %s%s" % (PORT, sha[:8], " (arbore murdar: se verifică indexul)" if git else ""))
    return 0


def opreste():
    if os.path.exists(STARE):
        pid = json.load(open(STARE))["pid"]
        for sem, asteapta in ((signal.SIGTERM, 20), (signal.SIGKILL, 10)):
            try:
                os.killpg(pid, sem)
            except ProcessLookupError:
                break
            for _ in range(asteapta):
                time.sleep(1)
                try:
                    os.kill(pid, 0)
                except ProcessLookupError:
                    break
    import shutil
    shutil.rmtree(TEMP, ignore_errors=True)
    print("[verificator design] oprit; portul %d %s" % (PORT, "răspunde încă!" if _raspunde() else "liber"))
    return 0


# ── ecranele ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def slug(nume):
    s = unicodedata.normalize("NFKD", nume).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def registru():
    return json.load(open(REGISTRU, encoding="utf-8"))


def _sesiune(utilizator):
    stare = json.load(open(os.path.join(STARE_COPIE, "stare.json"), encoding="utf-8"))
    email = stare["utilizatori"]["superadmin"] if utilizator == "superadmin" else stare["utilizator"]["email"]
    parola = open(os.path.join(STARE_COPIE, "parola"), encoding="utf-8").read().strip()
    import pasi
    return pasi.autentifica("http://127.0.0.1:%d" % PORT, email, parola), stare["firme"]


def ecran(nume, rez, director, interventie=None, masuri_alt=None, director_png=None):
    """Deschide ecranul `nume` din registru la rezoluția `LATxINALT`; scrie captura și măsurătorile. [16.7] `interventie` = JS rulat după pași,
    înaintea măsurării; `masuri_alt` = a doua cale .js evaluată pe aceeași pagină (rezultat în cheia `masuri_alt`); `director_png` = directorul capturilor."""
    from playwright.sync_api import sync_playwright
    intrari = [e for e in registru() if e["nume"] == nume]
    if not intrari:
        print("[verificator design] ecran necunoscut: %r (vezi `lista`)" % nume, file=sys.stderr)
        return 2
    e = intrari[0]
    lat, inalt = (int(x) for x in rez.split("x"))
    os.makedirs(director, exist_ok=True)
    if director_png:
        os.makedirs(director_png, exist_ok=True)
    os.environ["PROBA_BAZA"] = "http://127.0.0.1:%d" % PORT
    os.environ["E2E_CAPTURI"] = director
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    init, firme = _sesiune(e.get("utilizator", "cabinet"))
    schema = next((k for k, v in firme.items() if v["nume"].startswith(e["firma"] + " ")), None) if e.get("firma") else None
    if e.get("firma") and not schema:
        print("[verificator design] firma %r nu e în copie" % e["firma"], file=sys.stderr)
        return 2
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": lat, "height": inalt})
        ctx.add_init_script(init)
        pg = ctx.new_page()
        erori = []
        pg.on("pageerror", lambda x: erori.append(str(x)))
        pg.on("response", lambda r: erori.append("HTTP %d %s" % (r.status, r.url)) if r.status >= 500 else None)
        import pasi
        ec = pasi._e2e("http://127.0.0.1:%d" % PORT, director).Ecran(pg, "verificator")
        eroare = None
        try:
            if e.get("firma"):
                ec.firma(firme[schema]["nume"])
            else:
                ec.acasa()
            for pas in e.get("pasi", []):
                _pas(pg, pas)
            pg.wait_for_timeout(800)
            if interventie:
                pg.evaluate(interventie)
                pg.wait_for_timeout(300)
        except Exception as ex:  # noqa: BLE001 — un ecran care nu se deschide e un rezultat, nu o oprire
            eroare = str(ex).splitlines()[0][:300]
        pg.evaluate("(e) => { window.__exceptieB = e; }", EXCEPTII_B.get(nume))
        pg.evaluate("(l) => { window.__pastreazaRenunta = l; }", PASTREAZA_RENUNTA)
        masuri = pg.evaluate(open(MASURI, encoding="utf-8").read())
        if masuri_alt:
            masuri["masuri_alt"] = pg.evaluate(open(masuri_alt, encoding="utf-8").read())
        masuri.update({"ecran": nume, "rezolutie": rez, "firma": e.get("firma"), "nivel": e.get("nivel"), "eroare_deschidere": eroare or None,
                       "erori_js": erori + ec.erori})
        baza = os.path.join(director, "%s_%s" % (slug(nume), rez))
        pg.screenshot(path=os.path.join(director_png or director, os.path.basename(baza) + ".png"))
        b.close()
    masuri["verdict_mecanic"] = verdict_mecanic(masuri)
    json.dump(masuri, open(baza + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(masuri, ensure_ascii=False, indent=1))
    return 0


def _pas(pg, pas):
    """Un pas al registrului: `{"click": CSS, "text": T}` | `{"text": T}` (clic pe butonul cu textul) | `{"pauza": MS}` | `{"scrie": CSS, "valoare": V}`."""
    if "click" in pas:
        loc = pg.locator(pas["click"])
        if pas.get("index_rand"):   # rândul care conține textul (tabelul DS sau rând-buton), apoi elementul din el
            loc = pg.locator("tr, .firme-rand, button.firme-rand").filter(has_text=pas["index_rand"]).locator(pas["click"])
        if pas.get("text"):
            loc = loc.filter(has_text=pas["text"])
        loc.first.click(timeout=20000)
    elif "text" in pas:
        pg.get_by_text(pas["text"], exact=pas.get("exact", False)).first.click(timeout=20000)
    elif "cauta" in pas:   # căutarea de funcții din bara de sus a ferestrei (aceeași cale ca a contabilului)
        pg.click("#cautare-fereastra")
        pg.fill("#cautare-fereastra", pas["cauta"])
        pg.wait_for_timeout(700)
        pg.locator("#cautare-fereastra-rez .cautare-item").first.click(timeout=20000)
    elif "scrie" in pas:
        pg.fill(pas["scrie"], pas["valoare"])
    elif "pauza" in pas:
        pass
    else:
        raise ValueError("pas necunoscut: %r" % (pas,))
    pg.wait_for_timeout(int(pas.get("pauza", 600)))


def verdict_mecanic(m):
    """Verdictul mecanic pe rândurile a–h, din măsurătorile paginii: {rând: {"verdict": "TRECE"|"PICĂ", "motive": [...]}}.
    E piesa „script care refuză” (R5): subagentul confirmă sau contrazice, cu captura, dar nu slăbește un PICĂ mecanic fără motiv scris."""
    out = {}
    for r in RANDURI:
        motive = list(m.get("pica", {}).get(r, []))
        if m.get("eroare_deschidere") and r == "a":
            motive.insert(0, "ecranul nu s-a deschis: %s" % m["eroare_deschidere"])
        out[r] = {"verdict": "PICĂ" if motive else "TRECE", "motive": motive}
    return out


def prompt(ecrane, director):
    """Promptul fix al verificatorului (`verificator_design_prompt.txt`) cu rândurile a–h din `RANDURI` și lista de ecrane; directorul capturilor
    se spune în prompt. Nimic altceva nu intră în el: subagentul nu vede modificările, notele sau testele lui Code."""
    txt = open(os.path.join(RAD, "scripts", "verificator_design_prompt.txt"), encoding="utf-8").read()
    rd = "\n".join("  %s. %s;" % (k, v) for k, v in RANDURI.items())
    ec = "\n".join("- %s" % e for e in ecrane)
    return txt.replace("{RANDURI}", rd).replace("{ECRANE}", ec).replace("<DIRECTORUL_CAPTURILOR>", director)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "porneste":
        return porneste()
    if argv[0] == "opreste":
        return opreste()
    if argv[0] == "prompt" and len(argv) >= 3:
        print(prompt(argv[2:], argv[1]))
        return 0
    if argv[0] == "lista":
        for e in registru():
            print("%-14s %-34s %s" % (e.get("nivel", "?"), e["nume"], e.get("firma", "")))
        return 0
    if argv[0] == "ecran" and len(argv) in (4, 5):
        return ecran(argv[1], argv[2], argv[3], director_png=argv[4] if len(argv) == 5 else None)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
