# -*- coding: utf-8 -*-
"""scripts/scan_functionalitati.py — LISTA FUNCTIONALITATILOR, derivata din cod.

**Comanda** (Costin, 03.09.2026): *„Fa lista tuturor functionalitatilor aplicatiei, derivata din cod,
nu scrisa din memorie. … Nu lasa nimic afara. Lista cuprinde tot ce exista in aplicatie, fara
exceptii si fara filtrari de niciun fel."*

**CE E O UNITATE.** Un **punct de intrare** in aplicatie — locul prin care ceva poate fi cerut, apasat
sau declansat. Patru feluri, si toate patru intra:

  A. **rutele HTTP** — `main.py` (@app.*) plus cele montate din `core/spv_rute.py`;
  B. **ecranele** — id-urile `fa-*` din `static/js/`, plus fisierele de ecran care nu poarta niciun
     `fa-*` (cabinet, administrare, autentificare);
  C. **joburile de fundal** — `core/cron.RITMURI` (supravegheate) plus `core/cron.NESUPRAVEGHEATE`,
     ca sa nu dispara tocmai cele doua declarate ca nesupravegheate;
  D. **instrumentele din `scripts/`** — nu le atinge un contabil, dar exista si se executa.

**CE NU E O UNITATE, si de ce — declarat, nu filtrat tacit.** Modulele din `core/` nu apar ca unitati
proprii: nu sunt puncte de intrare, se ajunge la ele prin A sau C, si fiecare ar aparea de zeci de ori.
Ele apar ca **atribut** al unitatii (coloana de declaratie se calculeaza din ce scriu). La fel,
`frontend_test/` sunt probe, nu functionalitati. `core/test_*.py` sunt garzi, nu functionalitati.

**DE UNDE CITESTE.** `scripts/scan_trasee.py` — `citeste_rute()`, `citeste_module()`, `acoperire()`,
`tabele_cunoscute()`. Nu se rescrie niciun cititor: doua definitii ale lui „ruta" sau ale lui „tabel
scris" ar diverge tacut. Gruparea in functionalitati e chiar **traseul** (cele 35 + suprafetele
ne-documentare), fiindca el e singura grupare a repo-ului care e deja derivata si gardata.

**COLOANA „atinge date care ajung intr-o declaratie", cum se DERIVA.** Nu din nume si nu din impresie:
  1. modulele de declaratie = `core/d<cifre>*.py` + `declaratii_api` + `declaratii_componente` + `bilant`;
  2. tabelele pe care ACELEA le CITESC (`FROM` / `JOIN` in literalii lor de sir), pastrate numai daca
     sunt tabele reale (`scripts/trasee_tabele.json`);
  3. o unitate e **da** daca scrie (inline sau printr-un modul al ei) intr-unul dintre tabelele alea,
     sau daca ea insasi cheama un modul de declaratie.

**CE NU VEDE, declarat.** SQL construit din bucati la rulare; scrieri facute prin module de
infrastructura (`db`, `common` — scoase deliberat, altfel toate rutele ar iesi „da"); si, la ecrane,
caile compuse la rulare (`\\`/tenants/${id}/...\\`` se vede, dar una asamblata din variabile, nu).
Unde nu se poate decide, coloana scrie **`?`** — nu „nu".

**GENERAT O SINGURA DATA.** `LISTA_FUNCTIONALITATI.md` se regenereaza doar cu `--scrie`, si atunci
**pierde starile de probare scrise intre timp**. De aceea implicit doar tipareste.

    ./venv/bin/python scripts/scan_functionalitati.py            # numara si tipareste
    ./venv/bin/python scripts/scan_functionalitati.py --scrie    # (RE)SCRIE fisierul
"""
import ast
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from scripts import scan_trasee as T  # noqa: E402

CALE_MD = os.path.join(RAD, "LISTA_FUNCTIONALITATI.md")

#: Ce citesc modulele de declaratie. `RE_W` (scrierile) traieste in `scan_trasee`; simetricul lui
#: pentru citiri nu exista acolo, fiindca traseele nu aveau nevoie de el.
RE_R = re.compile(r'\b(?:FROM|JOIN)\s+(?:"?\{[^}]*\}"?\.|"?%\(?\w*\)?s"?\.|"?[a-z_]+"?\.)?'
                  r'"?([a-zA-Z_][a-zA-Z0-9_]*)"?', re.I)

VERB = {"GET": "citire / afisare", "POST": "creare sau executie",
        "PUT": "modificare", "PATCH": "modificare", "DELETE": "stergere"}


# ── A. RUTELE ────────────────────────────────────────────────────────────────
def _rute_montate(rel):
    """Rutele declarate in alt fisier decat `main.py` (azi: `core/spv_rute.py`, montat cu
    `monteaza(app, ...)`). Se citesc DOAR metoda, calea, functia si prima fraza a docstringului:
    modulele si scrierile lor nu se extrag aici, si de-aia coloana de declaratie le iese `?` daca
    nu se poate decide altfel. *Rutele astea sunt subtiri prin constructie — toata logica lor sta in
    `spv_conector` — dar diferenta se scrie, nu se presupune.*"""
    cale = os.path.join(RAD, *rel.split("/"))
    out = []
    arb = ast.parse(io.open(cale, encoding="utf-8").read())
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in fn.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            metoda = getattr(dec.func, "attr", None)
            if metoda not in T.METODE or not dec.args:
                continue
            if not isinstance(dec.args[0], ast.Constant):
                continue
            out.append({"metoda": metoda.upper(), "cale": dec.args[0].value,
                        "norm": T.normalizeaza(dec.args[0].value), "fn": fn.name,
                        "linie": fn.lineno, "garzi": set(), "roluri": set(), "fine": set(),
                        "module": [], "scrie_inline": {}, "refuzuri": 0,
                        "doc": T._prima_fraza(ast.get_docstring(fn)), "sursa": rel})
    return out


def rute():
    r = T.citeste_rute()
    for x in r:
        x["sursa"] = "main.py"
    r += _rute_montate("core/spv_rute.py")
    return r


# ── coloana de declaratie ────────────────────────────────────────────────────
def module_declaratie():
    """Modulele care PRODUC o declaratie. Criteriu structural pe nume — `d` + cifre —, plus cele
    trei care poarta lantul comun. Nu e o lista de mana: o declaratie noua `d777.py` intra singura."""
    out = set()
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        m = f[:-3]
        if re.match(r"^d\d+", m) or m in ("declaratii_api", "declaratii_componente", "bilant",
                                          "bilant_api", "saft"):
            out.add(m)
    return out


def _importuri_core(m):
    """Modulele din `core/` pe care le importa modulul `m`, fara infrastructura."""
    p = os.path.join(RAD, "core", m + ".py")
    if not os.path.exists(p):
        return set()
    try:
        arb = ast.parse(io.open(p, encoding="utf-8").read())
    except SyntaxError:
        return set()
    out = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
            for a in n.names:
                out.add(a.name)
    return out - T.INFRA


def module_hranitoare(decl):
    """Modulele pe care le importa generatoarele. Tabelele pe care le citesc ELE ajung tot sub ochii
    unui generator, doar cu un pas mai devreme — de-aia inchiderea e de UN nivel. Masurat, cele doua
    niveluri dau 18 si 23 de tabele, adica 158 si 197 de rute marcate `da` din 427: nivelul 1 nu
    degenereaza (n-ar avea rost o coloana care raspunde `da` la tot)."""
    imp = set()
    cdir = os.path.join(RAD, "core")
    for m in sorted(decl):
        p = os.path.join(cdir, m + ".py")
        if not os.path.exists(p):
            continue
        try:
            arb = ast.parse(io.open(p, encoding="utf-8").read())
        except SyntaxError:
            continue
        for n in ast.walk(arb):
            if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
                for a in n.names:
                    imp.add(a.name)
    return (imp - decl) - T.INFRA


def tabele_declaratie(decl, cunoscute):
    """Tabelele CITITE de modulele de declaratie. Aici se decide ce inseamna «ajunge intr-o
    declaratie»: nu ce se numeste fiscal, ci ce ajunge sub ochii unui generator."""
    tab = set()
    cdir = os.path.join(RAD, "core")
    for m in sorted(decl):
        try:
            src = io.open(os.path.join(cdir, m + ".py"), encoding="utf-8").read()
        except OSError:
            continue
        for g in RE_R.finditer("\n".join(T._siruri(src))):
            t = g.group(1)
            if t.lower() in ("select", "where", "set", "into", "as", "on"):
                continue
            if cunoscute is None or t in cunoscute:
                tab.add(t)
    return tab


def scrie_unitatea(r, mod):
    """Tabelele in care scrie o ruta: inline, plus prin modulele ei (fara infrastructura)."""
    t = set(r.get("scrie_inline") or {})
    for m in r.get("module") or []:
        t |= set((mod.get(m) or {}).get("scrie") or {})
    return t


def atinge_declaratie(r, mod, decl, tab_decl):
    """`da` / `nu` / `?`. `?` cand unitatea nu poate fi decisa mecanic — nu se rotunjeste la «nu»."""
    if set(r.get("module") or []) & decl:
        return "da"
    if scrie_unitatea(r, mod) & tab_decl:
        return "da"
    if r.get("sursa") and r["sursa"] != "main.py":
        return "?"
    return "nu"


# ── B. ECRANELE ──────────────────────────────────────────────────────────────
RE_ID = re.compile(r"\bfa-[a-z0-9]+\b")
#: Un literal de cale din JS. Clasa de caractere e PERMISIVA dinadins: prima formă cerea numai
#: `[A-Za-z0-9_/{}$.-]`, deci o cale cu interogare — `` `/tenants/${id}/facturi?pagina=${p}` `` —
#: nu se potrivea DELOC, iar ecranul ieșea cu zero rute chemate. Se taie la `?` mai jos.
RE_CALE_JS = re.compile(r"""['"`](/[^'"`\n]*)['"`]""")
#: Numele functiei care randeaza un ecran, asa cum e chemata din handlerul butonului `#fa-*`.
RE_HANDLER = re.compile(r"\b((?:randeaza|ecran)[A-Za-z0-9_]*)\s*\(")


def _js():
    out = []
    for rad, _d, fis in os.walk(os.path.join(RAD, "static", "js")):
        for f in sorted(fis):
            if f.endswith(".js"):
                out.append(os.path.relpath(os.path.join(rad, f), RAD).replace("\\", "/"))
    return sorted(out)


def _cai_din_js(text):
    """Caile pe care le cheama un ecran. `${...}` devine `{}`, ca sa se poata potrivi cu forma
    normalizata a rutelor. O cale asamblata din variabile NU se vede — limita e in antet."""
    out = set()
    for m in RE_CALE_JS.finditer(text):
        c = m.group(1).split("?")[0].split("#")[0]
        c = re.sub(r"\$\{[^}]*\}", "{}", c)
        c = re.sub(r"\{[^}]*\}", "{}", c)
        if c.startswith("/static") or c == "/" or " " in c:
            continue
        out.add(c.rstrip("/") or "/")
        out.add(c)
    return out


def _definitii(texte):
    """{nume functie: fisier} — unde e definita fiecare functie de randare. JavaScript n-are AST
    aici, deci se citeste cu expresii regulate; forma e declarata in antet, si greseala posibila e
    o atribuire RATATA (functia nu se gaseste), nu una falsa."""
    rd = re.compile(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_]+)"
                    r"|(?:const|let|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?[\(A-Za-z]")
    out = {}
    for rel, text in texte.items():
        for m in rd.finditer(text):
            nume = m.group(1) or m.group(2)
            out.setdefault(nume, rel)
    return out


def _corp(text, nume):
    """Corpul functiei `nume`, prin potrivire de acolade. Aproximativ prin constructie (nu se sar
    acoladele din siruri); daca nu se poate inchide, se intoarce None si atribuirea cade inapoi pe
    FISIER — mai grosolana, dar scrisa ca atare in tabel."""
    m = re.search(r"(?:function\s+%s\b|(?:const|let|var)\s+%s\s*=)" % (re.escape(nume), re.escape(nume)), text)
    if not m:
        return None
    # LISTA DE PARAMETRI se sare INTAI. Prima forma lua prima acolada de dupa nume — iar pe o
    # semnatura cu destructurare, `randeazaFacturi(c2, nav, id, {optiuni})`, acolada aia era chiar
    # parametrul: corpul „gasit" avea trei randuri, iar ecranul iesea cu ZERO rute chemate.
    p = text.find("(", m.end())
    a = text.find("{", m.end())
    j0 = m.end()
    if p >= 0 and (a < 0 or p < a):
        nivel = 0
        for k in range(p, len(text)):
            if text[k] == "(":
                nivel += 1
            elif text[k] == ")":
                nivel -= 1
                if nivel == 0:
                    j0 = k + 1
                    break
    i = text.find("{", j0)
    if i < 0:
        return None
    nivel = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            nivel += 1
        elif text[j] == "}":
            nivel -= 1
            if nivel == 0:
                return text[i:j + 1]
    return None


def ecrane(rute_norm):
    """[(identitate, fisiere, [rute chemate], granularitate)].

    Un `fa-*` = un ecran de firma. Toate cele 32 traiesc in `static/js/ecrane/firme.js`, dar
    fiecare buton cheama o **functie de randare** care sta, de obicei, in alt fisier
    (`#fa-facturi` -> `randeazaFacturi` -> `facturi_ecran.js`). Atribuirea rutelor se face pe
    CORPUL functiei aleia; daca nu se poate, cade inapoi pe fisierul intreg, si tabelul o spune.
    Un fisier de ecran care nu poarta niciun `fa-*` (cabinet, administrare, autentificare) e si el
    un ecran, sub numele lui."""
    texte = {rel: io.open(os.path.join(RAD, rel), encoding="utf-8").read() for rel in _js()}
    definitii = _definitii(texte)

    def potrivite(cai):
        return sorted({n for n in rute_norm if n in cai})

    per_id, cu_id = {}, set()
    for rel, text in texte.items():
        for m in RE_ID.finditer(text):
            ident = m.group(0)
            cu_id.add(rel)
            # Fereastra se OPRESTE la urmatorul `#fa-*`. Prima forma lua 700 de caractere fixe si
            # trecea peste butonul urmator: `fa-acces` primea `randeazaFacturi`, `fa-mijloace`
            # primea `ecranEtransport`. *O atribuire falsa e mai rea decat una lipsa — arata la fel
            # de plina.* Si se ia PRIMUL handler, nu toate: al doilea e deja al altui buton.
            urm = RE_ID.search(text, m.end())
            fer = text[m.end(): (urm.start() if urm else len(text))][:700]
            gasite = [h for h in RE_HANDLER.findall(fer) if h in definitii]
            handlere = gasite[:1]
            d = per_id.setdefault(ident, {"fisiere": set(), "rute": set(), "gran": set()})
            if handlere:
                for h in handlere:
                    f2 = definitii[h]
                    corp = _corp(texte[f2], h)
                    d["fisiere"].add("%s::%s()" % (f2, h))
                    d["rute"] |= set(potrivite(_cai_din_js(corp if corp else texte[f2])))
                    d["gran"].add("funcție" if corp else "fișier")
            else:
                # Handlerul nu s-a gasit. NU se cade pe fisierul intreg: `firme.js` are 94 de rute,
                # si i le-ar atribui pe toate unui singur buton — o atribuire falsa, care arata la
                # fel de plina ca una adevarata. Se scrie ca negasita, si atat.
                d["fisiere"].add(rel)
                d["gran"].add("handler negăsit")

    out = [(i, sorted(d["fisiere"]), sorted(d["rute"]),
            "/".join(sorted(d["gran"])) or "fișier") for i, d in sorted(per_id.items())]
    for rel, text in sorted(texte.items()):
        if rel not in cu_id:
            out.append((rel, [rel], potrivite(_cai_din_js(text)), "fișier"))
    return out


# ── C. JOBURILE DE FUNDAL ────────────────────────────────────────────────────
def joburi():
    from core import cron
    out = [(n, "supravegheat, prag %d h" % p) for n, p in sorted(cron.RITMURI.items())]
    out += [(n, "NESUPRAVEGHEAT — %s" % m) for n, m in sorted(cron.NESUPRAVEGHEATE.items())]
    return out


# ── D. INSTRUMENTELE ─────────────────────────────────────────────────────────
def instrumente():
    out = []
    for f in sorted(os.listdir(os.path.join(RAD, "scripts"))):
        if f.endswith(".py"):
            out.append("scripts/" + f)
    return out


# ── redarea ──────────────────────────────────────────────────────────────────
def _curata(s, n=120):
    s = " ".join((s or "").split()).replace("|", "/")
    return (s[: n - 1] + "…") if len(s) > n else s


def _nume_functionalitate(r):
    return _curata(r.get("doc") or r["fn"].replace("_", " "))


def construieste():
    r = rute()
    mod = T.citeste_module()
    cunoscute = T.tabele_cunoscute()
    decl = module_declaratie()
    tab_decl = tabele_declaratie(decl | module_hranitoare(decl), cunoscute)
    per_traseu, orfane, dublate, nedoc = T.acoperire([x for x in r if x["sursa"] == "main.py"])
    et_nedoc = {(m, c): e for m, c, e in nedoc}
    grup = {}
    for x in r:
        cheie = None
        for tid, lst in per_traseu.items():
            if any(y is x for y in lst):
                cheie = (tid, dict((t[0], t[1]) for t in T.TRASEE)[tid])
                break
        if cheie is None:
            e = et_nedoc.get((x["metoda"], x["cale"]))
            if e:
                cheie = ("S-" + e[:3].upper(), "suprafata ne-documentara: " + e)
            elif x["sursa"] != "main.py":
                cheie = ("T-SPV", "Conectorul SPV/ANAF (rute montate din core/spv_rute.py)")
            else:
                cheie = ("ORFAN", "rute care nu intra in niciun traseu")
        x["_grup"] = cheie
        x["_decl"] = atinge_declaratie(x, mod, decl, tab_decl)
        grup.setdefault(cheie, []).append(x)
    return r, grup, mod, decl, tab_decl, orfane, dublate


def redare_md():
    r, grup, mod, decl, tab_decl, orfane, dublate = construieste()
    rute_norm = {x["norm"] for x in r}
    ecr = ecrane(rute_norm)
    job = joburi()
    ins = instrumente()
    decl_ruta = {x["norm"]: x["_decl"] for x in r}

    L = []
    nr = 0
    L.append("# LISTA FUNCȚIONALITĂȚILOR")
    L.append("")
    L.append("**Derivată din cod cu `scripts/scan_functionalitati.py`** (03.09.2026), la comanda lui "
             "Costin: *„lista tuturor funcționalităților aplicației, derivată din cod, nu scrisă din "
             "memorie … nu lăsa nimic afară, fără excepții și fără filtrări de niciun fel.”*")
    L.append("")
    L.append("**Fișierul se EDITEAZĂ de aici încolo, nu se regenerează.** Regenerarea "
             "(`--scrie`) rescrie tabelele și **pierde stările de probare**. Numerotarea e stabilă "
             "cât timp nu se regenerează: un rând se citează ca `#nr`.")
    L.append("")
    L.append("**Ce e o unitate:** un **punct de intrare** — locul prin care ceva poate fi cerut, "
             "apăsat sau declanșat. Patru feluri, toate patru în listă: **A** rutele HTTP · "
             "**B** ecranele · **C** joburile de fundal · **D** instrumentele din `scripts/`.")
    L.append("")
    L.append("**Ce NU e unitate, declarat:** modulele din `core/` (nu sunt puncte de intrare — se "
             "ajunge la ele prin A sau C, și apar ca *atribut*: coloana de declarație se calculează "
             "din ce scriu ele) · `frontend_test/` (probe) · `core/test_*.py` (gărzi).")
    L.append("")
    L.append("**Coloana „declarație” se derivă**, nu se judecă: modulele `core/d<cifre>*` + "
             "`declaratii_api` + `declaratii_componente` + `bilant*` citesc un set de tabele; o "
             "unitate primește **da** dacă scrie într-unul dintre ele sau dacă cheamă ea însăși un "
             "modul de declarație. **`?`** înseamnă *nu se poate decide mecanic* — nu se rotunjește "
             "la „nu”.")
    L.append("")
    L.append("**Stare probare:** `neprobat` peste tot la scriere. Se schimbă pe măsură ce se probează.")
    L.append("")

    randuri_a, randuri_b, randuri_c, randuri_d = [], [], [], []

    for cheie in sorted(grup, key=lambda k: (k[0].startswith("S-"), k[0])):
        tid, nume = cheie
        randuri_a.append((tid, nume, grup[cheie]))

    total_rute = sum(len(x[2]) for x in randuri_a)
    L.append("## A. Rute HTTP — %d" % total_rute)
    L.append("")
    L.append("*Grupate pe traseul din `TRASEE.md` (derivat de `scan_trasee.acoperire`). "
             "Rolul cerut, unde există, e scris lângă rută — de el atârnă proba.*")
    L.append("")
    for tid, nume, lst in randuri_a:
        L.append("### %s — %s (%d)" % (tid, nume, len(lst)))
        L.append("")
        L.append("| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |")
        L.append("|---|---|---|---|---|---|")
        for x in sorted(lst, key=lambda y: (y["cale"], y["metoda"])):
            nr += 1
            rol = ""
            if x["roluri"]:
                rol = " · rol `%s`" % "/".join(sorted(x["roluri"]))
            elif x["garzi"]:
                rol = " · `%s`" % "/".join(sorted(x["garzi"]))
            else:
                rol = " · fără gardă"
            L.append("| %d | %s | `%s %s`%s | %s — `%s()` | %s | neprobat |" % (
                nr, _nume_functionalitate(x), x["metoda"], x["cale"], rol,
                VERB.get(x["metoda"], x["metoda"]), x["fn"], x["_decl"]))
        L.append("")

    L.append("## B. Ecrane — %d" % len(ecr))
    L.append("")
    L.append("*Un `fa-*` = un ecran de firmă; rutele lui se iau din **corpul funcției** care îl "
             "randează (`#fa-facturi` → `randeazaFacturi` → `facturi_ecran.js`). Un fișier de ecran "
             "fără niciun `fa-*` (cabinet, administrare, autentificare) e și el un ecran, sub numele "
             "fișierului.*")
    L.append("")
    L.append("*Un fișier care e implementarea unui `fa-*` apare **și** ca unitate proprie, "
             "deliberat: cardul e intrarea, fișierul e suprafața cu dialogurile lui. Nu e o "
             "dublură — sunt două lucruri de probat. Unde handlerul nu s-a găsit, se scrie "
             "`handler negăsit` și rutele rămân neatribuite: `firme.js` are 94 de rute, iar "
             "atribuirea lor toate unui singur buton ar fi arătat la fel de plină ca una adevărată.*")
    L.append("")
    L.append("| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |")
    L.append("|---|---|---|---|---|---|")
    for ident, fisiere, chemate, gran in ecr:
        nr += 1
        d = "nu"
        if not chemate:
            d = "?"
        elif any(decl_ruta.get(c) == "da" for c in chemate):
            d = "da"
        elif any(decl_ruta.get(c) == "?" for c in chemate):
            d = "?"
        L.append("| %d | Ecranul `%s` — %d rute chemate%s | `%s` | interacțiune de ecran "
                 "(atribuire pe %s) | %s | neprobat |"
                 % (nr, ident, len(chemate),
                    (": " + _curata(", ".join("`" + c + "`" for c in chemate), 300)) if chemate else "",
                    _curata(", ".join(fisiere), 110), gran, d))
    L.append("")

    L.append("## C. Joburi de fundal — %d" % len(job))
    L.append("")
    L.append("*Din `core/cron.RITMURI` (supravegheate) și `core/cron.NESUPRAVEGHEATE`. Cele două "
             "nesupravegheate intră în listă tocmai fiindcă sunt declarate ca atare.*")
    L.append("")
    L.append("| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |")
    L.append("|---|---|---|---|---|---|")
    for nume, det in job:
        nr += 1
        info = mod.get(nume) or {}
        # Scrierile jobului INCLUD modulele pe care le cheama — la fel ca la rute. Fara pasul asta
        # `facturi_recurente` iesea „nu", desi el chiar produce facturi: scrierea traieste in
        # `facturi_api`, nu in corpul jobului.
        scrie = set((info.get("scrie") or {}))
        chemate = _importuri_core(nume)
        for m2 in chemate:
            scrie |= set((mod.get(m2) or {}).get("scrie") or {})
        d = "da" if (scrie & tab_decl or nume in decl or chemate & decl) else ("nu" if info else "?")
        L.append("| %d | Jobul `%s` — %s | `core/%s.py` (fundal) | rulare periodică | %s | neprobat |"
                 % (nr, nume, det, nume, d))
    L.append("")

    L.append("## D. Instrumente din `scripts/` — %d" % len(ins))
    L.append("")
    L.append("*Nu le atinge un contabil, dar există și se execută. Intră în listă fiindcă comanda "
             "spune „fără filtrări de niciun fel”; se probează altfel decât o rută — prin rulare "
             "directă —, iar unele n-au sens de probat invalid/valid. Motivul se scrie la probare.*")
    L.append("")
    L.append("| nr | funcționalitate | ecran sau rută | acțiune | declarație | stare probare |")
    L.append("|---|---|---|---|---|---|")
    for f in ins:
        nr += 1
        L.append("| %d | %s | `%s` | rulare din linia de comandă | nu | neprobat |"
                 % (nr, _curata(_doc_scurt(f)), f))
    L.append("")

    L.append("---")
    L.append("")
    L.append("## Ce a ieșit din derivare, ca cifre")
    L.append("")
    L.append("- **rute**: %d (din care %d montate din `core/spv_rute.py`)" % (
        len(r), len([x for x in r if x["sursa"] != "main.py"])))
    L.append("- **ecrane**: %d · **joburi**: %d · **instrumente**: %d" % (len(ecr), len(job), len(ins)))
    L.append("- **TOTAL unități: %d**" % nr)
    L.append("- **rute orfane** (în niciun traseu și în nicio suprafață declarată): %d%s" % (
        len(orfane), (" — " + ", ".join("%s %s" % o for o in orfane)) if orfane else ""))
    L.append("- **module de declarație** din care s-a derivat coloana: %d · "
             "**tabele citite de ele**: %d" % (len(decl), len(tab_decl)))
    L.append("- **rute** cu declarație = **da**: %d · **nu**: %d · **?**: %d "
             "*(numai secțiunea A; ecranele și joburile își poartă coloana în tabelele lor)*" % (
        sum(1 for x in r if x["_decl"] == "da"), sum(1 for x in r if x["_decl"] == "nu"),
        sum(1 for x in r if x["_decl"] == "?")))
    L.append("")
    return "\n".join(L) + "\n"


def _doc_scurt(rel):
    try:
        arb = ast.parse(io.open(os.path.join(RAD, rel), encoding="utf-8").read())
        d = ast.get_docstring(arb)
        return T._prima_fraza(d) if d else rel
    except (SyntaxError, OSError, UnicodeDecodeError):
        return rel


def main(argv):
    md = redare_md()
    if "--scrie" in argv:
        with io.open(CALE_MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(md)
        print("SCRIS: LISTA_FUNCTIONALITATI.md (%d octeti)" % len(md))
    else:
        print(md[-1200:])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
