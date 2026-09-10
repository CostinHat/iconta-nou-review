# -*- coding: utf-8 -*-
"""scripts/scan_blocante.py — CE ȚINE BUCLA DE EVENIMENTE OCUPATĂ, derivat din cod. (P5)

**CONTRACTUL, citit din sursa canonică, nu din memorie.** `PLAN_HARDENING.md:325-342`:

    # P5 — ASYNC / BLOCKING I/O
    Analiză per rută, nu migrare masivă. Nu se convertește aplicația la `async` pe orizontală;
    se caută rutele în care un I/O blocant ține bucla de evenimente ocupată.
    … apel de rețea sincron (SPV, BNR, Brevo), citire de fișier mare, `subprocess`
    (DUKIntegrator), interogare lungă.

**DE CE E UN INSTRUMENT SEPARAT DE `scan_tranzactii.py`.** Aceleași fișiere, alt lucru măsurat, și
mai ales: **P4 e o fază ÎNCHISĂ**. A extinde detectorul lui ca să prindă și primitive de blocare i-ar
schimba cele 332 de cifre pe care stă acceptarea. Deci graful se reconstruiește aici, cu aceeași
metodă (rezolvare pe modul → fișier gazdă → omonime, marcate), și P4 rămâne neatins. *Lineage-ul se
scrie, ca să nu pară că am uitat că există.*

---

## CE HOTĂRĂȘTE TOTUL: `async def` vs `def`

În FastAPI/Starlette, un handler **`def`** (sincron) rulează într-un **fir din threadpool**; unul
**`async def`** rulează **pe bucla de evenimente**. Consecința, care e chiar miezul lui P5:

  * un I/O blocant într-un handler `async def` **ține bucla ocupată** — TOATE celelalte cereri
    stau, oricâte fire ar fi libere;
  * un I/O blocant într-un handler `def` **ocupă un fir** din cele `40` ale limitatorului AnyIO —
    e o limită de capacitate, nu un blocaj al buclei.

Cele două nu se raportează împreună, fiindcă nu se repară la fel.

**Măsurat pe `8ce4cd84`:** `anyio 4.13.0` · `starlette 1.1.0` · `fastapi 0.136.3` ·
`uvicorn 0.48.0` · limitator implicit de fire: **40** · `ICONTA_POOL_MAX = 10` · un singur proces
(`ExecStart` fără `--workers`).

---

## DETECTORII

| ID | ce detectează | de ce e în contract |
|---|---|---|
| **C1** | `async def` cu primitivă blocantă atinsă **fără** trecere prin threadpool | chiar definiția canonică: I/O blocant care ține bucla ocupată |
| **C2** | rută **sincronă** care ajunge la un apel de **rețea** extern | „apel de rețea sincron (SPV, BNR, Brevo)" — ocupă un fir cât ține latența altcuiva |
| **C3** | cale care ajunge la **subproces** | „`subprocess` (DUKIntegrator)" |
| **C4** | cale care ajunge la **`time.sleep`** | o cerere care parchează deliberat resursa |
| **C5** | primitivă blocantă **NE-DB** executată cât timp e ținută o conexiune din pool | leagă resursa RARĂ (10) de latența unui serviciu străin — clasa lui R183 |
| **C6** | apel de rețea **fără `timeout`** | un capăt care nu răspunde parchează firul (și conexiunea) la nesfârșit |
| **C7** | **I/O de fișier** pe calea unei cereri | „citire de fișier mare" |

**„Interogare lungă" NU are detector, și se spune de ce.** Nu e decidabilă static: lungimea unei
interogări depinde de date și de planul ales, nu de forma apelului. Un detector care ar ghici-o
(„`SELECT` fără `LIMIT`") ar produce zgomot pe toate citirile legitime de nomenclator. Substitutul
declarat e **empiric**: timpul de bază pe rută, măsurat în `masuratori/p5/`, unde o interogare lungă
se vede ca durată, nu ca formă. *P3 a măsurat deja numărul de interogări pe rutele de portofoliu;
aici se măsoară timpul.*

## LIMITĂRI, FALS-POZITIVE, FALS-NEGATIVE — declarate înainte de cifre

**Ce nu vede (fals-negative):**
  * apeluri indirecte prin variabilă, `getattr`, dispecer pe dicționar;
  * primitive ajunse prin biblioteci terțe care nu apar în graful nostru (graful acoperă
    `main.py` + `core/*.py`);
  * adâncimea e mărginită (implicit 8); căile atinse de limită se **numără** și se tipăresc;
  * „interogare lungă", declarat mai sus.

**Ce numără în plus (fals-pozitive):**
  * **omonimii** — un nume rezolvat pe treapta a treia aduce evenimentele tuturor definițiilor cu
    acel nume. Marcat `omonim`, și numărat separat;
  * **ramuri exclusive** — `if`/`else` se aplatizează, deci o primitivă de pe o ramură care nu se
    execută niciodată împreună cu alta apare totuși;
  * **`C7` nu poate ști cât de mare e fișierul.** Detectează I/O de fișier, nu „fișier mare";
  * **`C6` nu vede un `timeout` ascuns** într-o sesiune (`requests.Session` cu adaptor) sau într-un
    ambalaj propriu — se declară, și fiecare caz e verificat la sursă în clasificare.
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

ADANCIME = 8
MAX_NODURI = 40000

# ============================================================================
#  PRIMITIVELE BLOCANTE — numai ce e primitiv. Restul iese din expandare.
# ============================================================================

#: `nume_apel -> fel`. Numele simple, valabile oriunde.
BLOCANT_APEL = {
    # baza de date — psycopg2 e sincron prin construcție
    "get_conn": "DB", "connect": "DB", "getconn": "DB",
    "execute": "DB", "executemany": "DB", "fetchone": "DB", "fetchall": "DB", "fetchmany": "DB",
    # rețea
    "urlopen": "RETEA", "urlretrieve": "RETEA",
    "sendmail": "RETEA", "SMTP": "RETEA", "SMTP_SSL": "RETEA",
    # subproces
    "Popen": "SUBPROC", "check_output": "SUBPROC", "check_call": "SUBPROC",
    # fișiere
    "read_text": "FS", "read_bytes": "FS", "write_text": "FS", "write_bytes": "FS",
    "extractall": "FS", "copyfile": "FS", "copy2": "FS", "copytree": "FS", "rmtree": "FS",
    "iglob": "FS", "listdir": "FS", "walk": "FS", "makedirs": "FS", "mkdtemp": "FS",
    "mkstemp": "FS", "NamedTemporaryFile": "FS", "savefig": "FS",
}

#: `(modul, atribut) -> fel`. Cer modulul, fiindcă numele singur e prea comun.
BLOCANT_MODUL = {
    ("requests", "get"): "RETEA", ("requests", "post"): "RETEA", ("requests", "put"): "RETEA",
    ("requests", "delete"): "RETEA", ("requests", "patch"): "RETEA", ("requests", "head"): "RETEA",
    ("requests", "request"): "RETEA",
    ("httpx", "get"): "RETEA", ("httpx", "post"): "RETEA", ("httpx", "put"): "RETEA",
    ("httpx", "delete"): "RETEA", ("httpx", "request"): "RETEA", ("httpx", "stream"): "RETEA",
    ("smtplib", "SMTP"): "RETEA", ("smtplib", "SMTP_SSL"): "RETEA",
    ("subprocess", "run"): "SUBPROC", ("subprocess", "call"): "SUBPROC",
    ("subprocess", "Popen"): "SUBPROC", ("subprocess", "check_output"): "SUBPROC",
    ("subprocess", "check_call"): "SUBPROC",
    ("os", "system"): "SUBPROC",
    ("time", "sleep"): "SLEEP",
    ("os", "listdir"): "FS", ("os", "walk"): "FS", ("os", "makedirs"): "FS",
    ("os", "remove"): "FS", ("os", "unlink"): "FS", ("os", "rename"): "FS",
    ("shutil", "rmtree"): "FS", ("shutil", "copy"): "FS", ("shutil", "copy2"): "FS",
    ("shutil", "copyfile"): "FS", ("shutil", "copytree"): "FS", ("shutil", "move"): "FS",
    ("glob", "glob"): "FS", ("glob", "iglob"): "FS",
    ("json", "load"): "FS",
}

#: felurile care sunt „rețea" — pentru C2 și C6
FEL_RETEA = ("RETEA",)

#: trecerile prin threadpool: ce e chemat de aici NU mai e pe buclă
IESIRE_DIN_BUCLA = {"run_in_threadpool", "to_thread", "run_in_executor", "run_sync"}

#: deschideri de conexiune, pentru domeniul C5
DESCHIDE = ("get_conn", "connect", "getconn")


def _nume_apel(nod):
    f = nod.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _modul_atribut(nod):
    f = nod.func
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
        return (f.value.id, f.attr)
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Attribute):
        return (f.value.attr, f.attr)
    return None


def _text_sir(nod):
    if isinstance(nod, ast.Constant) and isinstance(nod.value, str):
        return nod.value
    if isinstance(nod, ast.JoinedStr):
        return " ".join(v.value for v in nod.values
                        if isinstance(v, ast.Constant) and isinstance(v.value, str))
    return None


def _are_timeout(nod):
    """`"DA"` · `"NU"` · `"PRIN_KW"` — trei stări, fiindcă două mint.

    Forma dinainte întorcea `True/False` și dădea **fals-pozitiv** pe termenul primit prin
    despachetare: `requests.request(metoda, url, **kw)` n-are `timeout` la locul apelului, dar toți
    apelanții lui `spv_conector.apel_anaf` îl trimit prin `kw` (`efactura_send.py:393,400,407,442`
    și `etransport_send.py:82,89,97` — verificat rând cu rând). Două căi de cerere fuseseră
    clasificate `ACTION_REQUIRED` pe dovada asta.

    `"PRIN_KW"` **nu** înseamnă „e în regulă": înseamnă *nu se poate decide aici*. Se numără
    separat, fiindcă ascunde un risc care rămâne — `apel_anaf` n-are termen **implicit**, deci un
    apelant viitor care uită `timeout=` produce exact defectul pe care C6 îl caută, și nimic nu
    l-ar opri. Pentru `urlopen`, și al treilea argument pozițional e timeout.
    """
    for kw in nod.keywords:
        if kw.arg == "timeout":
            return "DA"
    nume = _nume_apel(nod)
    if nume == "urlopen" and len(nod.args) >= 3:
        return "DA"
    if any(kw.arg is None for kw in nod.keywords) or any(
            isinstance(a, ast.Starred) for a in nod.args):
        return "PRIN_KW"
    return "NU"


def _mod_deschidere(nod):
    """`open(...)` — întoarce `"citire"` / `"scriere"`; `None` dacă nu e `open`."""
    if _nume_apel(nod) not in ("open",):
        return None
    mod = None
    if len(nod.args) >= 2:
        mod = _text_sir(nod.args[1])
    for kw in nod.keywords:
        if kw.arg == "mode":
            mod = _text_sir(kw.value)
    if mod and re.search(r"[waxWAX+]", mod):
        return "scriere"
    return "citire"


# ============================================================================
#  STRATUL 1 — evenimentele unei funcții, în ordinea sursei, cu domeniile
#
#  Nod: ("ev", fel, detaliu, fisier, linie, in_domeniu)
#       ("apel", nume, fisier, linie, in_domeniu, modul, prin_threadpool)
#       ("domeniu", [noduri], fisier, linie)
# ============================================================================

def _expr(nod, rel, in_dom, out, alias):
    brute = []
    for sub in ast.walk(nod):
        if not isinstance(sub, ast.Call):
            continue
        cheie = (getattr(sub, "lineno", 0), getattr(sub, "col_offset", 0))
        nume = _nume_apel(sub)
        ma = _modul_atribut(sub)
        if nume in IESIRE_DIN_BUCLA:
            # ce e chemat de aici pleacă de pe buclă: argumentele-funcție se marchează
            for a in list(sub.args) + [k.value for k in sub.keywords]:
                if isinstance(a, ast.Name):
                    brute.append((cheie, ("apel", a.id, rel, sub.lineno, in_dom, None, True)))
            continue
        fel = None
        if ma is not None and ma in BLOCANT_MODUL:
            fel = BLOCANT_MODUL[ma]
        elif nume in BLOCANT_APEL:
            fel = BLOCANT_APEL[nume]
        elif nume == "sleep" and ma is None:
            fel = "SLEEP"
        mod = _mod_deschidere(sub)
        if mod is not None:
            fel = "FS"
            nume = "open:%s" % mod
        if fel:
            detaliu = "%s:%s" % (fel, nume)
            if fel in FEL_RETEA:
                detaliu += {"DA": "|timeout", "PRIN_KW": "|TIMEOUT_PRIN_KW",
                            "NU": "|FARA_TIMEOUT"}[_are_timeout(sub)]
            brute.append((cheie, ("ev", fel, detaliu, rel, sub.lineno, in_dom)))
            continue
        if nume:
            modul = None
            f = sub.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                modul = alias.get(f.value.id)
            brute.append((cheie, ("apel", nume, rel, sub.lineno, in_dom, modul, False)))
    brute.sort(key=lambda x: x[0])
    out.extend(n for _c, n in brute)


def _e_deschidere(nod):
    return isinstance(nod, ast.Call) and _nume_apel(nod) in DESCHIDE


def _stmt(nod, rel, in_dom, out, alias):
    if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return
    if isinstance(nod, (ast.With, ast.AsyncWith)):
        deschide = any(_e_deschidere(it.context_expr) for it in nod.items)
        for it in nod.items:
            if not _e_deschidere(it.context_expr):
                _expr(it.context_expr, rel, in_dom, out, alias)
            else:
                # deschiderea însăși e o primitivă DB
                out.append(("ev", "DB", "DB:get_conn", rel, nod.lineno, in_dom))
        for s in nod.body:
            _stmt(s, rel, True if deschide else in_dom, out, alias)
        return
    for _camp, valoare in ast.iter_fields(nod):
        elemente = valoare if isinstance(valoare, list) else [valoare]
        for el in elemente:
            if isinstance(el, ast.stmt):
                _stmt(el, rel, in_dom, out, alias)
            elif isinstance(el, ast.AST):
                _expr(el, rel, in_dom, out, alias)


def arbore_functie(nod, rel, alias):
    out = []
    for s in nod.body:
        _stmt(s, rel, False, out, alias)
    return out


# ============================================================================
#  STRATUL 2 — graful
# ============================================================================

def _fisiere():
    out = [os.path.join(RAD, "main.py")]
    core = os.path.join(RAD, "core")
    for n in sorted(os.listdir(core)):
        if n.endswith(".py") and not n.startswith("test_") and not n.startswith("scan_"):
            out.append(os.path.join(core, n))
    return out


def _alias(noduri, cunoscute):
    out = {}
    for nod in noduri:
        if isinstance(nod, ast.ImportFrom) and (nod.module or "").split(".")[0] == "core":
            for a in nod.names:
                cale = "core/%s.py" % a.name
                if cale in cunoscute:
                    out[a.asname or a.name] = cale
        elif isinstance(nod, ast.Import):
            for a in nod.names:
                if a.name.startswith("core."):
                    cale = "core/%s.py" % a.name.split(".", 1)[1]
                    if cale in cunoscute:
                        out[a.asname or a.name.split(".")[-1]] = cale
    return out


def _fara_functii(radacina):
    for n in ast.iter_child_nodes(radacina):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        yield n
        for sub in _fara_functii(n):
            yield sub


def _e_main(nod):
    t = nod.test
    return (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
            and t.left.id == "__name__" and t.comparators
            and isinstance(t.comparators[0], ast.Constant)
            and t.comparators[0].value == "__main__")


def _lucratori(nod_if):
    out = set()
    for c in ast.walk(nod_if):
        if not isinstance(c, ast.Call):
            continue
        n = _nume_apel(c)
        if n:
            out.add(n)
        for a in list(c.args) + [k.value for k in c.keywords]:
            if isinstance(a, ast.Name):
                out.add(a.id)
    return sorted(out)


def graf(fisiere=None, rad=None):
    """`(arbori, rute, definitii, module_main, async_def)`.

    `rute[(fisier, nume)]` — `[(metoda, cale)]`; `async_def` — mulțimea cheilor `async def`.
    """
    rad = rad or RAD
    fisiere = fisiere or _fisiere()
    cunoscute = {os.path.relpath(c, rad).replace(os.sep, "/") for c in fisiere}
    arbori, rute, definitii, module_main, asincrone, mw = {}, {}, {}, {}, set(), {}
    for cale in fisiere:
        rel = os.path.relpath(cale, rad).replace(os.sep, "/")
        try:
            radacina = ast.parse(io.open(cale, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        alias_fis = _alias(_fara_functii(radacina), cunoscute)
        for nod in ast.walk(radacina):
            if isinstance(nod, ast.If) and _e_main(nod):
                module_main[rel] = _lucratori(nod)
                continue
            if not isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            definitii.setdefault(nod.name, []).append((rel, nod.lineno))
            alias = dict(alias_fis)
            alias.update(_alias(ast.walk(nod), cunoscute))
            arbori.setdefault((rel, nod.name), []).extend(arbore_functie(nod, rel, alias))
            if isinstance(nod, ast.AsyncFunctionDef):
                asincrone.add((rel, nod.name))
            for d in nod.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and d.func.attr in ("get", "post", "put", "delete", "patch")
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    rute.setdefault((rel, nod.name), []).append(
                        (d.func.attr.upper(), d.args[0].value))
                # `@app.middleware("http")` — rulează pe buclă la FIECARE cerere
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and d.func.attr == "middleware"):
                    mw[(rel, nod.name)] = True
    return arbori, rute, definitii, module_main, asincrone, mw


def rezolva(nume, rel_gazda, modul, arbori, definitii):
    """Trei trepte: modulul de import → fișierul gazdă → toate omonimele (marcate)."""
    if modul and (modul, nume) in arbori:
        return [(modul, nume)], False
    if (rel_gazda, nume) in arbori:
        return [(rel_gazda, nume)], False
    chei = [(rel, nume) for rel, _l in definitii.get(nume, []) if (rel, nume) in arbori]
    return chei, len(chei) > 1


# ============================================================================
#  STRATUL 3 — expandarea unei căi, cu „pe buclă" și „în domeniu" propagate
# ============================================================================

def expandeaza(cheie, arbori, definitii, pe_bucla, adancime=ADANCIME, _stiva=(), _memo=None,
               _omonim=False, _in_dom=False, _contor=None):
    """`[(fel, detaliu, fisier, linie, pe_bucla, in_domeniu, via, omonim)]` pentru calea `cheie`."""
    _memo = _memo if _memo is not None else {}
    _contor = _contor if _contor is not None else [0]
    m = (cheie, adancime, pe_bucla, _omonim, _in_dom)
    if m in _memo:
        return _memo[m]
    if cheie in _stiva or adancime <= 0 or cheie not in arbori:
        return []
    _memo[m] = []
    rel_gazda, nume_gazda = cheie
    out = []
    for n in arbori[cheie]:
        if _contor[0] > MAX_NODURI:
            out.append(("TRUNCHIAT", "peste %d noduri" % MAX_NODURI, rel_gazda, 0,
                        pe_bucla, _in_dom, (nume_gazda,), False))
            break
        _contor[0] += 1
        if n[0] == "ev":
            _f, fel, det, fis, lin, in_dom = n
            out.append((fel, det, fis, lin, pe_bucla, bool(in_dom or _in_dom),
                        (nume_gazda,), _omonim))
            continue
        _f, chemat, fis, lin, in_dom, modul, prin_tp = n
        chei, om = rezolva(chemat, rel_gazda, modul, arbori, definitii)
        for ch in chei:
            sub = expandeaza(ch, arbori, definitii,
                             False if prin_tp else pe_bucla,
                             adancime - 1, _stiva + (cheie,), _memo,
                             _omonim or om, bool(in_dom or _in_dom), _contor)
            for e in sub:
                out.append(e[:6] + ((nume_gazda,) + e[6], e[7] or _omonim or om))
            _contor[0] += len(sub)
    _memo[m] = out
    return out


# ============================================================================
#  DETECTORII
# ============================================================================

DETECTORI = {
    "C1": "async def cu primitivă blocantă atinsă FĂRĂ trecere prin threadpool "
          "(ține bucla de evenimente ocupată)",
    "C2": "rută SINCRONĂ care ajunge la un apel de rețea extern (ocupă un fir din cele 40)",
    "C3": "cale care ajunge la un SUBPROCES",
    "C4": "cale care ajunge la `time.sleep`",
    "C5": "primitivă blocantă NE-DB executată cât timp e ținută o conexiune din pool",
    "C6": "apel de rețea FĂRĂ `timeout`",
    "C7": "I/O de fișier pe calea unei cereri",
}


def detectori(evenimente, e_ruta, e_async):
    """`{cod: motiv}` pentru o cale, din evenimentele ei expandate."""
    out = {}
    pe_bucla = [e for e in evenimente if e[4] and e[0] in ("DB", "RETEA", "SUBPROC", "FS", "SLEEP")]
    retea = [e for e in evenimente if e[0] == "RETEA"]
    subproc = [e for e in evenimente if e[0] == "SUBPROC"]
    somn = [e for e in evenimente if e[0] == "SLEEP"]
    fisiere = [e for e in evenimente if e[0] == "FS"]
    in_dom_nedb = [e for e in evenimente
                   if e[5] and e[0] in ("RETEA", "SUBPROC", "FS", "SLEEP")]
    fara_timeout = [e for e in retea if "FARA_TIMEOUT" in e[1]]

    if e_async and pe_bucla:
        feluri = sorted({e[0] for e in pe_bucla})
        out["C1"] = ("handler `async def`: %d primitive blocante pe bucla de evenimente (%s)"
                     % (len(pe_bucla), ", ".join(feluri)))
    if e_ruta and not e_async and retea:
        out["C2"] = "rută sincronă cu %d apeluri de rețea externe" % len(retea)
    if subproc:
        out["C3"] = "%d apeluri de subproces" % len(subproc)
    if somn:
        out["C4"] = "%d apeluri `time.sleep`" % len(somn)
    if in_dom_nedb:
        feluri = sorted({e[0] for e in in_dom_nedb})
        out["C5"] = ("%d primitive NE-DB executate cu o conexiune din pool ținută (%s)"
                     % (len(in_dom_nedb), ", ".join(feluri)))
    if fara_timeout:
        out["C6"] = "%d apeluri de rețea fără `timeout`" % len(fara_timeout)
    if e_ruta and fisiere:
        out["C7"] = "%d operații de fișier pe calea cererii" % len(fisiere)
    return out


# ============================================================================
#  INVENTARUL
# ============================================================================

def puncte_de_intrare(rute, module_main, arbori, definitii, asincrone, mw=None):
    """`[(fel, eticheta, cheie, e_ruta, e_async)]`.

    **Middleware-ul e punct de intrare, și e cel mai fierbinte dintre toate:** rulează pe buclă la
    FIECARE cerere, nu doar pe ruta lui. Prima formă a scanerului nu-l vedea — fals-negativ prins
    măsurând, nu citind."""
    out = []
    for cheie in sorted(mw or {}):
        out.append(("middleware", "middleware %s::%s()" % cheie, cheie, True,
                    cheie in asincrone))
    for (rel, fn), lst in sorted(rute.items()):
        for metoda, cale in lst:
            out.append(("ruta", "%s %s" % (metoda, cale), (rel, fn), True,
                        (rel, fn) in asincrone))
    for rel, chemate in sorted(module_main.items()):
        for c in chemate:
            if (rel, c) in arbori and (rel, c) not in rute:
                out.append(("fundal", "%s::__main__ -> %s()" % (rel, c), (rel, c), False,
                            (rel, c) in asincrone))
    # lifespan / startup: rulează pe buclă, ca orice `async def`
    for cheie in sorted(arbori):
        if cheie[1] in ("lifespan", "startup", "on_startup") and cheie not in rute:
            out.append(("pornire", "%s::%s()" % cheie, cheie, False, cheie in asincrone))
    return out


def inventar(adancime=ADANCIME, fisiere=None, rad=None):
    arbori, rute, definitii, module_main, asincrone, mw = graf(fisiere, rad)
    memo = {}
    intrari = puncte_de_intrare(rute, module_main, arbori, definitii, asincrone, mw)
    out, trunchiate = [], 0
    for fel, eticheta, cheie, e_ruta, e_async in intrari:
        ev = expandeaza(cheie, arbori, definitii, pe_bucla=e_async, adancime=adancime, _memo=memo)
        if any(e[0] == "TRUNCHIAT" for e in ev):
            trunchiate += 1
        d = detectori(ev, e_ruta, e_async)
        if not d:
            continue
        blocante = [e for e in ev if e[0] in ("DB", "RETEA", "SUBPROC", "FS", "SLEEP")]
        out.append({
            "id": "P5-%03d" % (len(out) + 1),
            "fel": fel, "intrare": eticheta, "functie": cheie[1], "fisier": cheie[0],
            "async": e_async, "e_ruta": e_ruta,
            "detectori": d,
            "fapte": {
                "primitive_total": len(blocante),
                "pe_bucla": len([e for e in blocante if e[4]]),
                "in_domeniu_db": len([e for e in blocante if e[5] and e[0] != "DB"]),
                "feluri": sorted({e[0] for e in blocante}),
                "retea_fara_timeout": len([e for e in blocante
                                           if e[0] == "RETEA" and "FARA_TIMEOUT" in e[1]]),
                "retea_timeout_prin_kw": len([e for e in blocante
                                              if e[0] == "RETEA" and "PRIN_KW" in e[1]]),
                "numai_omonim": bool(blocante) and all(e[7] for e in blocante),
            },
            "primitive": [{"fel": e[0], "detaliu": e[1], "loc": "%s:%d" % (e[2], e[3]),
                           "pe_bucla": e[4], "in_domeniu_db": e[5],
                           "via": " -> ".join(e[6]), "omonim": e[7]}
                          for e in blocante],
        })
    stat = {"intrari": len(intrari), "candidati": len(out), "trunchiate": trunchiate,
            "adancime": adancime,
            "rute_async": len([1 for x in intrari if x[3] and x[4]]),
            "rute_sync": len([1 for x in intrari if x[3] and not x[4]]),
            "middleware": len(mw)}
    return out, stat


# ============================================================================
#  CALIBRARE
# ============================================================================

CORPUS = '''
from core import db
import requests, subprocess, time
from starlette.concurrency import run_in_threadpool


@app.post("/numai_c1")
async def numai_c1():
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT 1")


@app.post("/numai_c2")
def numai_c2():
    requests.get("https://exemplu", timeout=5)


@app.post("/numai_c3")
def numai_c3():
    subprocess.run(["ls"], timeout=5)


@app.post("/numai_c4")
def numai_c4():
    time.sleep(1)


@app.post("/minim_c5")
def minim_c5():
    with db.get_conn() as c:
        requests.get("https://exemplu", timeout=5)


@app.post("/minim_c6")
def minim_c6():
    requests.get("https://exemplu")


@app.post("/numai_c7")
def numai_c7():
    open("/tmp/x").read()


@app.middleware("http")
async def mw_blocant(request, call_next):
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT 1")
    return await call_next(request)


@app.middleware("http")
async def mw_curat(request, call_next):
    return await call_next(request)


@app.middleware("http")
async def mw_prin_threadpool(request, call_next):
    r = await call_next(request)
    await run_in_threadpool(_munca_grea)
    return r


@app.post("/control_timeout_prin_kw")
def control_timeout_prin_kw(**kw):
    requests.get("https://exemplu.invalid/x", **kw)


@app.get("/control_curat")
def control_curat():
    return {"ok": True}


@app.get("/control_pur")
def control_pur():
    return sum(i * i for i in range(10))


@app.post("/control_threadpool")
async def control_threadpool():
    await run_in_threadpool(_munca_grea)


def _munca_grea():
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT 1")
'''

#: `cod -> (ruta, detectorii ASTEPTATI)`. Multimile sunt PINATE: ele poarta implicatiile.
CALIBRARE = {
    "C1": ("POST /numai_c1", {"C1"}),
    "C2": ("POST /numai_c2", {"C2"}),
    "C3": ("POST /numai_c3", {"C3"}),
    "C4": ("POST /numai_c4", {"C4"}),
    "C5": ("POST /minim_c5", {"C2", "C5"}),
    "C6": ("POST /minim_c6", {"C2", "C6"}),
    "C7": ("POST /numai_c7", {"C7"}),
}

#: calea care aprinde C2 dar NU C6 — termenul vine prin despachetare, deci nu se poate decide
CALIBRARE_PRIN_KW = ("POST /control_timeout_prin_kw", {"C2"})

CONTROALE_NEGATIVE = ("GET /control_curat", "GET /control_pur", "POST /control_threadpool",
                      "middleware main.py::mw_curat()",
                      "middleware main.py::mw_prin_threadpool()")

#: middleware-ul BLOCANT trebuie vazut — e cea mai fierbinte cale din aplicatie
CALIBRARE_MIDDLEWARE = ("middleware main.py::mw_blocant()", {"C1"})


def corpus_sintetic():
    """Scrie corpusul de calibrare într-un director temporar și întoarce inventarul lui."""
    import tempfile
    d = tempfile.mkdtemp(prefix="calib_p5_")
    os.makedirs(os.path.join(d, "core"), exist_ok=True)
    cale = os.path.join(d, "main.py")
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(CORPUS)
    inv, _stat = inventar(fisiere=[cale], rad=d)
    return {x["intrare"]: x for x in inv}, d


def probe_calibrare():
    """`[(nume, a_trecut)]` — proba cu proba, ca garda din suită să spună CARE a picat.

    POZITIV: fiecare detector se aprinde pe cazul lui, cu mulțimea PINATĂ.
    NEGATIV: controalele nu se aprind deloc — inclusiv cel care trece prin threadpool."""
    gasit, _d = corpus_sintetic()
    probe = []
    for cod, (ruta, astept) in sorted(CALIBRARE.items()):
        x = gasit.get(ruta)
        aprins = set(x["detectori"]) if x else set()
        probe.append(("%s se aprinde pe cazul lui" % cod, cod in aprins))
        probe.append(("%s: mulțimea e cea pinată %s" % (cod, sorted(astept)), aprins == astept))
    ruta_kw, astept_kw = CALIBRARE_PRIN_KW
    x_kw = gasit.get(ruta_kw)
    probe.append(("termen prin `**kw`: NU aprinde C6",
                  bool(x_kw) and "C6" not in x_kw["detectori"]))
    probe.append(("termen prin `**kw`: mulțimea e cea pinată %s" % sorted(astept_kw),
                  set(x_kw["detectori"]) == astept_kw if x_kw else False))
    probe.append(("termen prin `**kw`: se NUMĂRĂ separat, nu se uită",
                  bool(x_kw) and x_kw["fapte"].get("retea_timeout_prin_kw", 0) >= 1))
    ruta_mw, astept_mw = CALIBRARE_MIDDLEWARE
    x_mw = gasit.get(ruta_mw)
    probe.append(("middleware blocant e VAZUT ca punct de intrare", x_mw is not None))
    probe.append(("middleware blocant: mulțimea e cea pinată %s" % sorted(astept_mw),
                  set(x_mw["detectori"]) == astept_mw if x_mw else False))
    for ruta in CONTROALE_NEGATIVE:
        probe.append(("control NEGATIV %s nu se aprinde" % ruta, ruta not in gasit))
    return probe


def calibreaza(verbose=True):
    """Verdictul de linie de comandă peste `probe_calibrare()`."""
    probe = probe_calibrare()
    ok = all(r for _n, r in probe)
    if verbose:
        print("CALIBRARE scan_blocante — pozitiv + negativ (METODA §22):")
        for nume, rez in probe:
            print("  %-58s %s" % (nume[:58], "OK" if rez else "PICAT"))
        print("  VERDICT:", "OK" if ok else "PICAT — niciun inventar de mai jos n-ar valora nimic")
    return ok


# ============================================================================
#  CLI
# ============================================================================

def _scrie(cale, text):
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("scris: %s" % cale)


def raport_text(inv, stat):
    L = []
    L.append("INVENTARUL BRUT P5 — I/O BLOCANT, derivat mecanic din cod")
    L.append("Generat cu: ./venv/bin/python -m scripts.scan_blocante --inventar")
    L.append("Contract canonic: PLAN_HARDENING.md:325-342 (P5 — ASYNC / BLOCKING I/O)")
    L.append("Puncte de intrare: %d (rute async %d · rute sync %d) · candidati: %d · "
             "adancime %d · trunchiate: %d"
             % (stat["intrari"], stat["rute_async"], stat["rute_sync"], stat["candidati"],
                stat["adancime"], stat["trunchiate"]))
    L.append("=" * 78)
    L.append("")
    for cod in sorted(DETECTORI):
        L.append("  %-4s %s" % (cod, DETECTORI[cod]))
    L.append("")
    for x in inv:
        L.append("%s  %s   [%s]" % (x["id"], x["intrare"], ", ".join(sorted(x["detectori"]))))
        L.append("    handler : %s() in %s   %s"
                 % (x["functie"], x["fisier"], "ASYNC DEF" if x["async"] else "def (threadpool)"))
        for cod in sorted(x["detectori"]):
            L.append("    %-4s: %s" % (cod, x["detectori"][cod]))
        f = x["fapte"]
        L.append("    fapte   : %d primitive (%d pe bucla · %d cu conexiune tinuta) · %s%s"
                 % (f["primitive_total"], f["pe_bucla"], f["in_domeniu_db"],
                    ", ".join(f["feluri"]),
                    " · TOATE OMONIME" if f["numai_omonim"] else ""))
        for p in x["primitive"][:30]:
            L.append("        %-22s %-30s %s%s via %s%s"
                     % (p["detaliu"], p["loc"],
                        "BUCLA " if p["pe_bucla"] else "      ",
                        "CONN " if p["in_domeniu_db"] else "     ",
                        p["via"], "  (omonim)" if p["omonim"] else ""))
        if len(x["primitive"]) > 30:
            L.append("        ... inca %d" % (len(x["primitive"]) - 30))
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    if not calibreaza():
        sys.exit(2)
    print()
    inv, stat = inventar()
    print("PUNCTE DE INTRARE: %d (rute async %d · rute sync %d) · CANDIDATI: %d · trunchiate: %d"
          % (stat["intrari"], stat["rute_async"], stat["rute_sync"], stat["candidati"],
             stat["trunchiate"]))
    nr = {}
    for x in inv:
        for c in x["detectori"]:
            nr[c] = nr.get(c, 0) + 1
    print("  " + " · ".join("%s: %d" % (c, nr.get(c, 0)) for c in sorted(DETECTORI)))
    print()
    for x in inv:
        if "C1" in x["detectori"]:
            print("  C1  %-56s %s" % (x["intrare"][:56], ",".join(sorted(x["detectori"]))))
    if "--inventar" in sys.argv:
        _scrie(os.path.join(RAD, "masuratori", "p5", "P5_INVENTAR_BRUT.txt"),
               raport_text(inv, stat))
        _scrie(os.path.join(RAD, "masuratori", "p5", "P5_INVENTAR_BRUT.json"),
               json.dumps({"stat": stat, "detectori": DETECTORI, "candidati": inv},
                          ensure_ascii=False, indent=2))
