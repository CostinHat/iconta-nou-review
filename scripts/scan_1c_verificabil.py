# -*- coding: utf-8 -*-
"""SE POATE VERIFICA CE IESE? — pasul 1c, 29.08.2026.

DE CE EXISTĂ. `PLAN_INVESTIGATII.md`, faza 1, pasul 1c: *„Un artefact care iese și se validează, dar
pe care contabilul nu-l poate verifica, îl obligă să-l refacă în altă parte. Atunci produsul nu i-a
economisit munca."* Cele patru întrebări ale planului, pentru un eșantion de cifre:

  Q1. **se poate vedea din ce se compune**, la cerere?
  Q2. **se vede ce NU s-a aplicat și de ce** — o deducere neacordată, o scutire neaplicată?
  Q3. **se vede ce s-a schimbat față de perioada anterioară**, cu motivul?
  Q4. **temeiul ajunge pe ecran**, sau trăiește doar în cod?

CE E NOU FAȚĂ DE 22.08. Atunci s-a măsurat pe **trei cifre** (netul de pe fluturaș, o poziție din
decont, un rând din D112) și pe **cod**. Aici se măsoară pe **ARTEFACTELE CARE CHIAR IES** — lista lor
o dă 1b, pe regimurile reale — și pe **răspunsul VIU al rutei**, nu pe grep. Diferența contează:
un artefact poate avea componentele în cod și să nu le trimită, iar grepul nu deosebește.

CUM MĂSOARĂ, ca să nu fie o aserțiune pe text (METODA §23). Fiecare întrebare se pune **pe STRUCTURA
răspunsului JSON**, nu pe șiruri:

  Q1 = există în răspuns o **listă de obiecte** care poartă cel puțin un câmp numeric — adică
       elementele din care e făcută cifra, nu numărul lor. `{"operatiuni": 18}` e un CONTOR, nu o
       componentă, și de-asta nu trece;
  Q2 = există un canal de **absență motivată** — o listă nevidă de afirmații despre ce nu s-a
       aplicat (`avertismente`, `note_rezultat`, `limite`, `constatari`);
  Q3 = există vreo cheie care numește perioada anterioară sau diferența față de ea;
  Q4 = există o cheie `temei` **și** se scrie AL CUI e temeiul — al cifrei, sau al altcuiva.
       *Distincția e a mea, nu a instrumentului: `valideaza` întoarce un `temei`, dar el e al
       VALIDATORULUI („DUKIntegrator -v D300"), nu al cifrei. Se raportează separat, ca să nu se
       numere un DA fals.*

CE NU VEDE, declarat:
  - **ecranul.** Se măsoară ce TRIMITE ruta, nu ce randează JS-ul. Un câmp trimis și neafișat trece
    aici ca DA — deci cifrele sunt **plafon superior** pentru „se poate verifica". Partea de randare
    rămâne la uneltele vizuale, și se spune în raport;
  - **PDF-urile.** Fluturașul își arată componentele pe hârtie, nu în JSON. Se numără separat, ca
    excepție declarată — altfel singurul loc unde o cifră își arată azi componentele ar apărea ca zero;
  - **o singură perioadă** (08/2026), aceeași ca la 1b, ca rândurile să fie comparabile;
  - **dacă explicația e BUNĂ.** Că textul e citibil de un contabil e o judecată de om.

    set -a && . ~/.iconta/db.env && . ~/.iconta/api_keys.env && set +a
    ./venv/bin/python scripts/scan_1c_verificabil.py [--firme tenant_013] [--json]
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import db  # noqa: E402

BAZA = "http://127.0.0.1:8010"
AN, LUNA, TRIM = 2026, 8, 3

# Cheile care poartă o ABSENȚĂ MOTIVATĂ — canalele prin care aplicația spune „nu s-a aplicat, fiindcă".
CANALE_ABSENTA = ("avertismente", "note_rezultat", "limite", "constatari", "verificari_contabile",
                  "neaplicabile", "motiv", "cauza")
# Cheile care ar purta o comparație cu PERIOADA ANTERIOARĂ. Tiparul cere noțiunea de perioadă, nu
# doar cuvântul „diferență": prima formă prindea `diferenta` gol și a raportat un DA fals pe semafor,
# unde el e diferența dintre soldul contabil și fișele CV — o RECONCILIERE, nu o comparație în timp.
# Verificat la sursă (`main.py:7658`) înainte de a fi corectat. *A patra oară în două zile când un
# scan pe formă brută supra-numără, iar citirea corectează.*
TIPAR_ANTERIOR = re.compile(
    r"anterior|precedent|luna_trecut|perioada_precedenta|diferenta_(luna|perioada|fata)", re.I)

# Componentele NETULUI, numite pe 22.08 la interdicția 63 (și reparate pe hârtie în aceeași zi).
# Se caută pe NUME, în rândul de stat — ca să se poată spune dacă ruta le trimite, nu doar dacă
# trimite un rând.
COMPONENTE_NET = ("deducere", "deducere_baza", "deducere_tineri", "deducere_copii", "facilitate",
                  "cas_suprataxa", "cass_suprataxa")


def _call(cale, corp=None, tok=None, metoda=None, timeout=180):
    h = {"Content-Type": "application/json"}
    if tok:
        h["Authorization"] = "Bearer " + tok
    date = json.dumps(corp).encode() if corp is not None else None
    cerere = urllib.request.Request(BAZA + cale, date, h, method=metoda)
    try:
        return json.load(urllib.request.urlopen(cerere, timeout=timeout)), None
    except urllib.error.HTTPError as e:
        try:
            corp_e = json.load(e)
        except Exception:
            corp_e = {"detail": e.read().decode(errors="replace")[:300]}
        return None, {"cod": e.code,
                      "detail": corp_e.get("detail") if isinstance(corp_e, dict) else corp_e}
    except Exception as e:
        return None, {"cod": 0, "detail": str(e)[:200]}


def _token(email):
    from core import auth_api
    import psycopg2.extras as E
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT * FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
    assert u, "user %r inexistent" % email
    return auth_api.emite_token(dict(u))


# ───────────────────────── cele patru întrebări, pe STRUCTURĂ ─────────────────────────

def _liste_de_obiecte(x, adancime=0):
    """[(cale, câte)] pentru fiecare listă de dicționare care poartă cel puțin un câmp NUMERIC.

    Asta e „componenta": elementele din care e făcută cifra. Un `{"operatiuni": 18}` e un CONTOR și
    NU se califică — chiar asta e distincția pe care 1c o cere.
    """
    out = []
    if adancime > 4:
        return out
    if isinstance(x, dict):
        for k, v in x.items():
            if isinstance(v, list) and v and all(isinstance(e, dict) for e in v):
                if any(isinstance(val, (int, float)) and not isinstance(val, bool)
                       for e in v for val in e.values()):
                    out.append((k, len(v)))
            out += [(k + "." + c, n) for c, n in _liste_de_obiecte(v, adancime + 1)]
    elif isinstance(x, list):
        for e in x[:20]:
            out += _liste_de_obiecte(e, adancime + 1)
    return out


def _chei(x, adancime=0):
    out = set()
    if adancime > 4:
        return out
    if isinstance(x, dict):
        for k, v in x.items():
            out.add(k)
            out |= _chei(v, adancime + 1)
    elif isinstance(x, list):
        for e in x[:20]:
            out |= _chei(e, adancime + 1)
    return out


def _absente_motivate(x):
    """[(cheie, câte)] pentru canalele de absență motivată care sunt NEVIDE.

    Un canal gol nu e un răspuns: `avertismente: []` înseamnă „n-am ce spune", nu „am spus".
    """
    out = []
    if isinstance(x, dict):
        for k, v in x.items():
            if k in CANALE_ABSENTA and v:
                out.append((k, len(v) if isinstance(v, (list, dict)) else 1))
            out += _absente_motivate(v)
    elif isinstance(x, list):
        for e in x[:20]:
            out += _absente_motivate(e)
    return out


def cele_patru(raspuns):
    chei = _chei(raspuns)
    comp = _liste_de_obiecte(raspuns)
    abs_m = _absente_motivate(raspuns)
    ant = sorted(k for k in chei if TIPAR_ANTERIOR.search(k))
    return {"Q1_componente": comp, "Q2_absente_motivate": abs_m, "Q3_anterior": ant,
            "Q4_temei": ("temei" in chei),
            # Cât din componentele NETULUI ajung în răspuns — întrebarea lui 63, pusă pe câmpuri,
            # nu pe „există o listă de rânduri". Pentru artefactele care n-au net, rămâne None.
            "componente_net": sorted(c for c in COMPONENTE_NET if c in chei) or None,
            "chei": len(chei)}


# ───────────────────────── artefactele, cu ruta fiecăruia ─────────────────────────

def artefacte_de_probat(tid):
    """(eticheta, metoda, cale, corp) — artefactele care IES, după 1b.

    Declarațiile se cheamă pe ruta care GENEREAZĂ și validează, adică exact ce vede contabilul când
    apasă „validează". Registrele, pe rutele lor de citire.
    """
    a = []
    for tip, per in (("d100", "trim"), ("d101", "an"), ("d112", "luna"), ("d205", "an"),
                     ("d300", "trim"), ("d301", "luna"), ("d390", "luna"), ("d394", "trim"),
                     ("d406", "trim")):
        corp = {"tenant_id": tid, "an": AN}
        if per == "luna":
            corp["luna"] = LUNA
        elif per == "trim":
            corp["trim"], corp["luna"] = TRIM, LUNA
        a.append(("declaratie %s" % tip.upper(), "POST", "/declaratii/%s/valideaza" % tip, corp))
    a.append(("registrul-jurnal 14-1-1", "GET",
              "/tenants/%d/jurnal?an=%d&luna=%d" % (tid, AN, LUNA), None))
    a.append(("registrul de casa 14-4-7A", "GET",
              "/tenants/%d/casa/registru?an=%d&luna=%d" % (tid, AN, LUNA), None))
    a.append(("statul de plata (netul)", "GET",
              "/tenants/%d/stat-plata?an=%d&luna=%d" % (tid, AN, LUNA), None))
    a.append(("control fiscal (semaforul)", "GET", "/control-fiscal/%d" % tid, None))
    return a


def masoara(tid, tok):
    out = {}
    for eticheta, metoda, cale, corp in artefacte_de_probat(tid):
        r, e = _call(cale, corp, tok=tok, metoda=(metoda if metoda == "POST" else None))
        if e:
            out[eticheta] = {"nu_iese": "%s %s" % (e.get("cod"), str(e.get("detail"))[:110])}
            continue
        out[eticheta] = cele_patru(r)
    return out


# ───────────────────────── partea de COD: 63–66, remăsurate ─────────────────────────

def numara_temei(rad):
    """(ocurențe `Temei(` în producție, module, ocurențe în teste) — cifra lui 66, remăsurată."""
    prod = test = 0
    module = set()
    for r, d, fs in os.walk(os.path.join(rad, "core")):
        d[:] = [x for x in d if x != "__pycache__"]
        for f in fs:
            if not f.endswith(".py"):
                continue
            cale = os.path.join(r, f)
            try:
                n = open(cale, encoding="utf-8").read().count("Temei(")
            except (UnicodeDecodeError, OSError):
                continue
            if not n:
                continue
            if f.startswith("test_"):
                test += n
            else:
                prod += n
                module.add(os.path.relpath(cale, rad).replace("\\", "/"))
    return prod, sorted(module), test


def temei_in_js(rad):
    """(ocurențe, fișiere) pentru cuvântul `temei` în `static/js` — cifra lui 66, cealaltă jumătate."""
    n, fis = 0, set()
    for r, d, fs in os.walk(os.path.join(rad, "static", "js")):
        for f in fs:
            if not f.endswith(".js"):
                continue
            cale = os.path.join(r, f)
            try:
                k = open(cale, encoding="utf-8").read().lower().count("temei")
            except (UnicodeDecodeError, OSError):
                continue
            if k:
                n += k
                fis.add(os.path.relpath(cale, rad).replace("\\", "/"))
    return n, sorted(fis)


def mecanisme_de_comparatie(rad):
    """Cifra lui 65: mecanisme care compară o perioadă cu cea dinainte. Se caută în COD, pe nume."""
    tipare = ("luna_anterioara", "luna_precedenta", "perioada_anterioara", "fata de luna",
              "diferenta_luna", "fata_de_anterior")
    gasite = {}
    for zona in ("core", "static/js"):
        baza = os.path.join(rad, *zona.split("/"))
        for r, d, fs in os.walk(baza):
            d[:] = [x for x in d if x != "__pycache__"]
            for f in fs:
                if not (f.endswith(".py") or f.endswith(".js")) or f.startswith("test_"):
                    continue
                try:
                    s = open(os.path.join(r, f), encoding="utf-8").read().lower()
                except (UnicodeDecodeError, OSError):
                    continue
                for t in tipare:
                    if t in s:
                        gasite.setdefault(t, []).append(
                            os.path.relpath(os.path.join(r, f), rad).replace("\\", "/"))
    return gasite, tipare


def ruleaza(doar=None):
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.id, t.schema_name, t.nume,
                       (SELECT u.email FROM public.users u
                         WHERE u.accounting_firm_id = t.accounting_firm_id
                           AND u.rol IN ('admin_firma','angajat')
                         ORDER BY CASE u.rol WHEN 'admin_firma' THEN 0 ELSE 1 END, u.id LIMIT 1)
                FROM public.tenants t WHERE t.activ ORDER BY t.schema_name""")
            firme = cur.fetchall()
    assert firme, "domeniul e gol — nicio firmă activă"
    tinta = [f for f in firme if (not doar or f[1] in doar)]
    assert tinta, "filtrul --firme a golit domeniul"

    rez, cache = {}, {}
    for tid, schema, nume, email in tinta:
        if not email:
            continue
        if email not in cache:
            cache[email] = _token(email)
        rez[schema] = {"nume": nume, "artefacte": masoara(tid, cache[email])}
        print("  măsurat %-12s %s" % (schema, (nume or "")[:34]))

    # anti-vacuu: dacă niciun artefact nu iese nicăieri, instrumentul măsoară altceva decât crede
    iesite = sum(1 for r in rez.values() for a in r["artefacte"].values() if "nu_iese" not in a)
    assert iesite > 0, ("CALIBRARE PICATĂ: niciun artefact n-a ieșit pe tot portofoliul — app oprit, "
                        "token greșit, sau rutele s-au mutat")
    cod = {"temei_productie": numara_temei(rad), "temei_js": temei_in_js(rad),
           "comparatie": mecanisme_de_comparatie(rad)}
    return rez, cod, iesite


def tipar(rez, cod, iesite):
    print("\n" + "=" * 104)
    print("1c — SE POATE VERIFICA CE IESE?   (luna %02d/%d · trim T%d/%d · anual %d)"
          % (LUNA, AN, TRIM, AN, AN))
    print("=" * 104)
    print("Se măsoară RĂSPUNSUL RUTEI, nu ecranul: un câmp trimis și neafișat trece aici ca DA.")
    print("Deci cifrele de mai jos sunt PLAFON SUPERIOR pentru «se poate verifica».\n")

    etichete = []
    for r in rez.values():
        for e in r["artefacte"]:
            if e not in etichete:
                etichete.append(e)

    tot = {e: {"iese": 0, "q1": 0, "q2": 0, "q3": 0, "q4": 0} for e in etichete}
    for schema, r in sorted(rez.items()):
        for e, a in r["artefacte"].items():
            if "nu_iese" in a:
                continue
            tot[e]["iese"] += 1
            tot[e]["q1"] += 1 if a["Q1_componente"] else 0
            tot[e]["q2"] += 1 if a["Q2_absente_motivate"] else 0
            tot[e]["q3"] += 1 if a["Q3_anterior"] else 0
            tot[e]["q4"] += 1 if a["Q4_temei"] else 0

    print("%-28s %6s %8s %8s %8s %8s" % ("artefact", "iese", "Q1 comp", "Q2 abs", "Q3 ant", "Q4 tem"))
    for e in etichete:
        t = tot[e]
        if not t["iese"]:
            print("%-28s %6d   — n-a ieșit pe nicio firmă —" % (e, 0))
            continue
        print("%-28s %6d %8d %8d %8d %8d" % (e, t["iese"], t["q1"], t["q2"], t["q3"], t["q4"]))

    print("\n═══ Q1, ascuțit: COMPONENTELE NETULUI ajung în răspunsul statului de plată?")
    print("    *Q1 de mai sus întreabă «există o listă de elemente cu cifre». Pentru registre asta")
    print("     CHIAR înseamnă componentele; pentru statul de plată înseamnă doar «un rând per")
    print("     salariat». Componentele netului sunt CÂMPURI în rând, deci se numără pe nume.*")
    for schema, r in sorted(rez.items()):
        a = r["artefacte"].get("statul de plata (netul)") or {}
        if "nu_iese" in a:
            continue
        print("  %-12s %s" % (schema, a.get("componente_net") or "NICIUNA"))

    print("\n═══ Q3 — COMPARAȚIA CU PERIOADA ANTERIOARĂ, în cod")
    gasite, tipare = cod["comparatie"]
    print("  tipare căutate: %s" % ", ".join(tipare))
    print("  găsite: %s" % (gasite if gasite else "NICIUNUL"))

    print("\n═══ Q4 — TEMEIUL: unde trăiește")
    prod, module, testte = cod["temei_productie"]
    njs, fjs = cod["temei_js"]
    print("  `Temei(` în PRODUCȚIE: %d ocurențe, în %d module — %s" % (prod, len(module), module))
    print("  `Temei(` în teste:     %d" % testte)
    print("  `temei` în static/js:  %d ocurențe, în %d fișiere — %s" % (njs, len(fjs), fjs))
    print("  *Cheia `temei` din raspunsul lui `valideaza` e a VALIDATORULUI (DUKIntegrator -v ...),")
    print("   nu a cifrei. Un DA la Q4 pe o declarație NU înseamnă că poziția își poartă temeiul.*")
    print("\n(anti-vacuu: %d artefacte au ieșit pe portofoliu)" % iesite)


if __name__ == "__main__":
    _doar = None
    if "--firme" in sys.argv:
        _doar = set(sys.argv[sys.argv.index("--firme") + 1].split(","))
    _r, _c, _i = ruleaza(_doar)
    tipar(_r, _c, _i)
    if "--json" in sys.argv:
        open("/tmp/1c_rezultat.json", "w", encoding="utf-8").write(
            json.dumps(_r, ensure_ascii=False, indent=1))
        print("\nJSON: /tmp/1c_rezultat.json")
