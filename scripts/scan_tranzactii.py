# -*- coding: utf-8 -*-
"""scripts/scan_tranzactii.py — CINE DEȚINE LIMITA TRANZACȚIEI, derivat din cod.

**DE CE EXISTĂ.** P4 întreabă unde sunt limitele tranzacționale. Ca să nu inventariez din memorie
use-case-urile „care scriu în mai multe locuri", lista se DERIVĂ: se parsează codul cu `ast` și se
construiește, pentru fiecare punct de intrare (rută FastAPI, lucrător de fundal), **arborele de
domenii tranzacționale** al căii — nu o listă plată de apeluri.

**MODELUL.** În casa asta o tranzacție are exact o formă: `with db.get_conn(schema) as conn:`
(`core/db.py` — `commit` la ieșire normală, `rollback` la excepție). Deci:

  * fiecare `with ... get_conn(...)` deschide un **DOMENIU**;
  * un eveniment (scriere SQL, efect extern, `commit()` explicit) aparține domeniului cel mai
    apropiat care îl cuprinde;
  * un eveniment care nu e cuprins de niciun domeniu **al funcției lui** urcă la apelant — exact
    cum o funcție care primește `conn` scrie în tranzacția apelantului;
  * o funcție chemată dintr-un domeniu, care își deschide domeniul ei, produce o tranzacție
    **a doua**, independentă: un `rollback` pe prima nu o desface pe a doua.

Întrebarea lui P4 devine astfel mecanică: **peste câte domenii distincte sunt împrăștiate
scrierile unei singure operații logice?** Una = tranzacția e deținută de use-case. Două sau mai
multe = stare parțială posibilă între ele.

**CELE ȘASE SEMNE cerute de comandă**, calculate pe arbore:

  C1  mai multe frontiere de tranzacție în aceeași operație logică (≥2 domenii, sau un `commit()`
      explicit înăuntrul unui domeniu urmat de alte scrieri);
  C2  scrieri către două sau mai multe surse/tabele/scheme distincte în aceeași cale;
  C3  scriere în bază + efect extern (fișier, coadă/job, e-mail/webhook, rețea, subproces);
  C4  scriere în sursă + invalidare/recalculare/model de citire în aceeași operație;
  C5  domenii tranzacționale **multiple care scriu** — adică mai multe conexiuni pentru aceeași
      operație logică;
  C6  scriere A → frontieră (commit / alt domeniu) sau efect extern → scriere B, unde o eroare la
      mijloc poate lăsa stare parțială.

**CE NU VEDE, declarat.** Cifrele de mai jos nu sunt un plafon într-o singură direcție; unele axe
supra-numără, altele sub-numără, iar cele două nu se anulează (METODA §22):

  * **omonimii, reduse dar nu stinse**: un apel se rezolvă în trei trepte — (1) modulul, când
    apelul e `modul.functie(...)` și `modul` e un alias de import cunoscut; (2) fișierul gazdă,
    când funcția e definită acolo; (3) abia dacă niciuna nu ține, TOATE definițiile cu acel nume,
    reunite (**supra-numărare**). Evenimentele venite din treapta a treia poartă `omonim`, iar
    căile care se sprijină numai pe ele se raportează separat. *Fără treptele 1 și 2, cele
    cincizeci de module de migrare — toate cu un `_main()` — se contopeau într-o singură cale cu
    161 de domenii scriitoare.*
  * **apeluri indirecte** prin variabilă, `getattr` sau dispecer pe dicționar — invizibile
    (**sub-numărare**).
  * **ramurile exclusive se aplatizează**: `if`/`else` produc evenimente în ordinea sursei, deci
    două scrieri care nu se execută niciodată împreună pot aprinde C6 (**supra-numărare**).
    Ramura de eroare (`except`) și `finally` sunt însă MARCATE, nu confundate cu calea normală.
  * **buclele** se parcurg o dată, deci multiplicitatea se pierde — dar evenimentele dintr-o buclă
    sunt **MARCATE**, fiindcă ordinea din sursă nu mai apără nimic acolo: un efect extern scris
    ÎNAINTEA scrierii care îl consemnează se execută, la a doua iterație, cu scrierea celei dintâi
    încă necomisă. *Instanța: `notificari_scadenta.emite_pentru_firma` — e-mailul pleacă, rândul
    care împiedică retrimiterea se scrie după el, și tot ce e în buclă stă în aceeași tranzacție.*
  * **SQL construit din variabile** nu se citește: se prinde numai partea din literal.
  * **`zipfile.ZipFile` NU e primitivă de disc**, deliberat: peste un `BytesIO` nu atinge discul
    (`gdpr_export.export_cabinet`), iar deosebirea nu se poate face static. Ce atinge discul intră
    oricum, prin `open(...,"w")`, `makedirs`, `remove`, `rmtree`, `extractall` — care sunt chiar
    apelurile pe care le face codul care scrie fișiere.
  * **conexiuni surori**: dacă o funcție ține două conexiuni deschise simultan și scrie pe cea
    exterioară dinăuntrul celei interioare, scrierea se atribuie domeniului interior (greșit, în
    direcția „mai multe domenii care scriu" — **supra-numărare**).
  * **adâncimea e mărginită**; căile atinse de limită se NUMĂRĂ și se tipăresc, nu se ascund.

**CALIBRARE.** `calibreaza()` probează instrumentul în **ambele** direcții pe un corpus sintetic cu
răspuns cunoscut: trebuie să vadă ce e acolo ȘI să refuze ce nu e. Un detector care ar întoarce
„toate rutele" ar trece o calibrare doar pozitivă.
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
#  PRIMITIVELE — numai ce e cu adevărat primitiv; restul iese din expandare.
#  `trimite_email`, `spv_*`, `alerteaza` NU sunt în nicio listă: ele ajung, pe
#  lanț, la `requests` / `smtplib` / `subprocess` / `open(...,"w")`.
# ============================================================================

DESCHIDE = ("get_conn", "connect", "getconn")

FRONTIERA_APEL = {"commit": "commit", "rollback": "rollback",
                  "set_session": "set_session", "set_isolation_level": "izolare"}

FRONTIERA_SQL = (
    (re.compile(r"\bRELEASE\s+SAVEPOINT\s+([a-zA-Z_]\w*)", re.I), "release"),
    (re.compile(r"\bROLLBACK\s+TO\s+(?:SAVEPOINT\s+)?([a-zA-Z_]\w*)", re.I), "rollback_to"),
    (re.compile(r"\bSAVEPOINT\s+([a-zA-Z_]\w*)", re.I), "savepoint"),
    (re.compile(r"^\s*BEGIN\s*;?\s*$", re.I | re.M), "begin"),
    (re.compile(r"^\s*COMMIT\s*;?\s*$", re.I | re.M), "commit"),
)

SCRIERE_SQL = (
    (re.compile(r"\bINSERT\s+INTO\s+([a-zA-Z_][\w.\"]*)", re.I), "INSERT"),
    (re.compile(r"\bUPDATE\s+(?:ONLY\s+)?([a-zA-Z_][\w.\"]*)\s+SET\b", re.I), "UPDATE"),
    (re.compile(r"\bDELETE\s+FROM\s+([a-zA-Z_][\w.\"]*)", re.I), "DELETE"),
    (re.compile(r"\bTRUNCATE\s+(?:TABLE\s+)?([a-zA-Z_][\w.\"]*)", re.I), "TRUNCATE"),
    (re.compile(r"\bCOPY\s+([a-zA-Z_][\w.\"]*)\s*\(", re.I), "COPY"),
    (re.compile(r"\bCREATE\s+(?:TABLE|SCHEMA|INDEX|UNIQUE\s+INDEX|SEQUENCE|TRIGGER|VIEW)"
                r"(?:\s+IF\s+NOT\s+EXISTS)?\s+([a-zA-Z_][\w.\"]*)", re.I), "DDL"),
    (re.compile(r"\bALTER\s+(?:TABLE|SCHEMA|SEQUENCE)\s+(?:IF\s+EXISTS\s+)?"
                r"([a-zA-Z_][\w.\"]*)", re.I), "DDL"),
    (re.compile(r"\bDROP\s+(?:TABLE|SCHEMA|INDEX|SEQUENCE|TRIGGER|VIEW)"
                r"(?:\s+IF\s+EXISTS\s+)?\s*([a-zA-Z_][\w.\"]*)", re.I), "DDL"),
    (re.compile(r"\b(?:setval|nextval)\s*\(\s*'([^']+)'", re.I), "SEQ"),
)

BLOCAJ_SQL = re.compile(r"\bFOR\s+UPDATE\b|\bpg_advisory_(?:xact_)?lock", re.I)

EXTERN_APEL = {
    "write_text": "FS", "write_bytes": "FS", "rmtree": "FS", "copyfile": "FS", "copy2": "FS",
    "copytree": "FS", "extractall": "FS", "savefig": "FS",
    "NamedTemporaryFile": "FS", "mkstemp": "FS", "mkdtemp": "FS",
    "urlopen": "RETEA", "urlretrieve": "RETEA",
    "sendmail": "EMAIL", "SMTP": "EMAIL", "SMTP_SSL": "EMAIL",
    "Popen": "SUBPROC", "check_output": "SUBPROC", "check_call": "SUBPROC",
    "add_task": "JOB", "create_task": "JOB", "Thread": "JOB", "submit": "JOB",
    "run_in_threadpool": "JOB", "run_in_executor": "JOB",
}

EXTERN_MODUL_ATRIBUT = {
    ("requests", "get"): "RETEA", ("requests", "post"): "RETEA", ("requests", "put"): "RETEA",
    ("requests", "delete"): "RETEA", ("requests", "patch"): "RETEA",
    ("requests", "request"): "RETEA", ("requests", "head"): "RETEA",
    ("httpx", "get"): "RETEA", ("httpx", "post"): "RETEA", ("httpx", "put"): "RETEA",
    ("httpx", "delete"): "RETEA", ("httpx", "request"): "RETEA", ("httpx", "stream"): "RETEA",
    ("subprocess", "run"): "SUBPROC", ("subprocess", "call"): "SUBPROC",
    ("subprocess", "Popen"): "SUBPROC", ("subprocess", "check_output"): "SUBPROC",
    ("subprocess", "check_call"): "SUBPROC",
    ("os", "system"): "SUBPROC", ("os", "remove"): "FS", ("os", "unlink"): "FS",
    ("os", "rename"): "FS", ("os", "replace"): "FS", ("os", "makedirs"): "FS",
    ("os", "mkdir"): "FS", ("os", "rmdir"): "FS", ("os", "write"): "FS",
    ("shutil", "rmtree"): "FS", ("shutil", "move"): "FS", ("shutil", "copy"): "FS",
    ("shutil", "copy2"): "FS", ("shutil", "copyfile"): "FS", ("shutil", "copytree"): "FS",
    ("smtplib", "SMTP"): "EMAIL", ("smtplib", "SMTP_SSL"): "EMAIL",
    ("asyncio", "create_task"): "JOB", ("threading", "Thread"): "JOB",
}

_MOD_SCRIE = re.compile(r"[waxWAX+]")


# ============================================================================
#  ajutoare de citit AST
# ============================================================================

def _e_normal(ramura):
    """Ramura de execuție normală (nu `except`, nu `finally`) — cu sau fără buclă."""
    return ramura.split("|")[0] == "normal"


def _e_bucla(ramura):
    return "|bucla:" in ramura


def _compune_ramura(exterioara, interioara):
    """Contextul unui eveniment atins PRIN APEL: al locului de apel, peste al lui propriu.

    Fără compunere, un efect ajuns printr-o funcție chemată din buclă pierde bucla — și cu ea
    tocmai proprietatea care contează. *Instanța: `notificari_scadenta.emite_pentru_firma`
    cheamă `observare.trimite_email_html` din buclă; e-mailul apărea ca `normal`, deci ordinea
    din sursă părea să-l apere.*"""
    baza = ("eroare" if "eroare" in (exterioara.split("|")[0], interioara.split("|")[0])
            else "finally" if "finally" in (exterioara.split("|")[0], interioara.split("|")[0])
            else "normal")
    bucle = list(_bucle(exterioara)) + [b for b in _bucle(interioara)
                                        if b not in _bucle(exterioara)]
    return "|".join([baza] + ["bucla:%s" % b for b in bucle])


def _bucle(ramura):
    """Identitățile buclelor care cuprind evenimentul — cea mai din afară prima."""
    return tuple(x[6:] for x in ramura.split("|") if x.startswith("bucla:"))


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


def _open_scrie(nod):
    """`open(cale, "w")` scrie; `open(cale)` citește. Fără mod explicit → citire."""
    if len(nod.args) >= 2:
        m = _text_sir(nod.args[1])
        if m is not None:
            return bool(_MOD_SCRIE.search(m))
    for kw in nod.keywords:
        if kw.arg == "mode":
            m = _text_sir(kw.value)
            if m is not None:
                return bool(_MOD_SCRIE.search(m))
    return False


def _tinta(nume):
    """`(sursa, tabel)`. Necalificat → `firma`, fiindcă `search_path` îl duce în schema firmei."""
    t = nume.strip().strip('"').lower()
    if "." in t:
        p, tab = t.split(".", 1)
        return p.strip('"'), tab.strip('"')
    return "firma", t


def _e_deschidere(nod):
    """True dacă expresia `nod` deschide o conexiune (`db.get_conn(...)`, `pool.getconn()`)."""
    return isinstance(nod, ast.Call) and _nume_apel(nod) in DESCHIDE


# ============================================================================
#  STRATUL 1 — arborele de domenii al UNEI funcții
#
#  Nod: ("ev", fel, detaliu, fisier, linie, ramura)
#       ("apel", nume, fisier, linie, ramura)
#       ("domeniu", [noduri], fisier, linie, ramura)
# ============================================================================

def _expr(nod, rel, ramura, out, alias=None):
    """Evenimentele dintr-o EXPRESIE, în ordinea sursei."""
    alias = alias or {}
    brute = []
    for sub in ast.walk(nod):
        cheie = (getattr(sub, "lineno", 0), getattr(sub, "col_offset", 0))
        if isinstance(sub, ast.Call):
            nume = _nume_apel(sub)
            ma = _modul_atribut(sub)
            if nume in DESCHIDE:
                # deschidere care NU e într-un `with` (rar) — o marcăm ca frontieră
                brute.append((cheie, ("ev", "frontiera", "deschide_fara_with", rel,
                                      sub.lineno, ramura)))
                continue
            if nume in FRONTIERA_APEL:
                brute.append((cheie, ("ev", "frontiera", FRONTIERA_APEL[nume], rel,
                                      sub.lineno, ramura)))
                continue
            fel = None
            if ma is not None and ma in EXTERN_MODUL_ATRIBUT:
                fel = EXTERN_MODUL_ATRIBUT[ma]
            elif nume in EXTERN_APEL:
                fel = EXTERN_APEL[nume]
            elif nume in ("open", "mkdir", "touch") and _open_scrie(sub):
                fel = "FS"
            if fel:
                brute.append((cheie, ("ev", "extern", "%s:%s" % (fel, nume), rel,
                                      sub.lineno, ramura)))
                continue
            if nume:
                modul = None
                f = sub.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                    modul = alias.get(f.value.id)
                brute.append((cheie, ("apel", nume, rel, sub.lineno, ramura, modul)))
            continue
        text = _text_sir(sub)
        if not text or len(text) < 6:
            continue
        for rx, fel in FRONTIERA_SQL:
            if rx.search(text):
                brute.append((cheie, ("ev", "frontiera", fel, rel, sub.lineno, ramura)))
        for rx, verb in SCRIERE_SQL:
            for m in rx.finditer(text):
                sursa, tabel = _tinta(m.group(1))
                brute.append((cheie, ("ev", "scriere", "%s|%s|%s" % (verb, sursa, tabel),
                                      rel, sub.lineno, ramura)))
        if BLOCAJ_SQL.search(text):
            brute.append((cheie, ("ev", "blocaj", "lock", rel, sub.lineno, ramura)))
    brute.sort(key=lambda x: x[0])
    out.extend(n for _c, n in brute)


def _stmt(nod, rel, ramura, out, alias=None):
    """Un ENUNȚ: își pune expresiile proprii, apoi coboară în corpuri, păstrând ordinea."""
    alias = alias or {}
    if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return                                    # au propria intrare în graf
    if isinstance(nod, (ast.With, ast.AsyncWith)):
        deschide = any(_e_deschidere(it.context_expr) for it in nod.items)
        for it in nod.items:
            if not _e_deschidere(it.context_expr):
                _expr(it.context_expr, rel, ramura, out, alias)
        if deschide:
            corp = []
            for s in nod.body:
                _stmt(s, rel, ramura, corp, alias)
            out.append(("domeniu", corp, rel, nod.lineno, ramura))
        else:
            for s in nod.body:
                _stmt(s, rel, ramura, out, alias)
        return
    if isinstance(nod, ast.Try):
        for s in nod.body:
            _stmt(s, rel, ramura, out, alias)
        for h in nod.handlers:
            for s in h.body:
                _stmt(s, rel, "eroare", out, alias)
        for s in nod.orelse:
            _stmt(s, rel, ramura, out, alias)
        for s in nod.finalbody:
            _stmt(s, rel, "finally" if ramura == "normal" else ramura, out, alias)
        return
    if isinstance(nod, (ast.For, ast.AsyncFor, ast.While)):
        # Bucla poartă IDENTITATE (`fisier:linie`). Fără ea, un efect dintr-o buclă și o scriere
        # din ALTĂ buclă a aceleiași căi ar părea că se împletesc — și chiar așa a ieșit prima
        # oară: `gdpr_sterge.executa` comite, apoi `sterge_fisiere` șterge într-o buclă proprie,
        # iar regula fără identitate raporta ordinea CORECTĂ ca defect.
        ram_b = ramura + ("" if _e_bucla(ramura) else "|bucla:%s:%d" % (rel, nod.lineno))
        for camp, valoare in ast.iter_fields(nod):
            elemente = valoare if isinstance(valoare, list) else [valoare]
            for el in elemente:
                if isinstance(el, ast.stmt):
                    _stmt(el, rel, ram_b, out, alias)
                elif isinstance(el, ast.AST):
                    _expr(el, rel, ram_b, out, alias)
        return
    for camp, valoare in ast.iter_fields(nod):
        elemente = valoare if isinstance(valoare, list) else [valoare]
        for el in elemente:
            if isinstance(el, ast.stmt):
                _stmt(el, rel, ramura, out, alias)
            elif isinstance(el, ast.AST):
                _expr(el, rel, ramura, out, alias)


def arbore_functie(nod, rel, alias=None):
    """Arborele de domenii al corpului funcției `nod`."""
    out = []
    for s in nod.body:
        _stmt(s, rel, "normal", out, alias)
    return out


def _noduri_fara_functii(radacina):
    """Nodurile din `radacina` SĂRIND corpurile funcțiilor — adică importurile de MODUL."""
    for n in ast.iter_child_nodes(radacina):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        yield n
        for sub in _noduri_fara_functii(n):
            yield sub


def alias_module(noduri, fisiere_cunoscute):
    """`{nume_local: fisier}` — aliasurile de import care duc la un fișier din graf.

    `from core import facturi_api` · `from core import x as y` · `import core.x as y`.

    **Aliasurile se citesc pe DOMENIU DE VIZIBILITATE, nu pe fișier.** În `main.py`, `_cc` e
    `centre_cost_api` într-o rută, `coduri_cm_api` în alta și `comodat_chirii` în a treia — unsprezece
    aliasuri sunt refolosite așa. Un dicționar pe fișier ar fi păstrat ultima legare și ar fi
    atribuit tăcut scrierile altui modul; instanța care a scos-o la iveală a fost
    `POST /centre-cost`, căruia i se atribuiau commituri din `casa_api` și `d300_manual_api`.
    """
    out = {}
    for nod in noduri:
        if isinstance(nod, ast.ImportFrom) and (nod.module or "").split(".")[0] == "core":
            for a in nod.names:
                cale = "core/%s.py" % a.name
                if cale in fisiere_cunoscute:
                    out[a.asname or a.name] = cale
        elif isinstance(nod, ast.Import):
            for a in nod.names:
                if a.name.startswith("core."):
                    cale = "core/%s.py" % a.name.split(".", 1)[1]
                    if cale in fisiere_cunoscute:
                        out[a.asname or a.name.split(".")[-1]] = cale
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


def _e_main(nod):
    t = nod.test
    return (isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
            and t.left.id == "__name__" and t.comparators
            and isinstance(t.comparators[0], ast.Constant)
            and t.comparators[0].value == "__main__")


def _lucratori(nod_if):
    """Funcțiile pornite dintr-un `if __name__ == "__main__"`, ca NUME.

    Două forme, amândouă reale în casă:
      * `ruleaza()` — apel direct;
      * `cron.ruleaza("facturi_recurente", _main)` — funcția e dată ca REFERINȚĂ ambalajului de
        job. *Fără forma a doua, lucrătorii de fundal — exact căile fără om care să vadă o eroare
        — lipseau din inventar, iar în locul lor intrau omonimele lui `ruleaza`.*
    """
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


def _poarta(nod):
    if not nod.args.defaults:
        return None
    for _a, impl in zip(nod.args.args[-len(nod.args.defaults):], nod.args.defaults):
        if (isinstance(impl, ast.Call) and getattr(impl.func, "id", None) == "Depends"
                and impl.args):
            a0 = impl.args[0]
            if isinstance(a0, ast.Name):
                return a0.id
            if isinstance(a0, ast.Call):
                return "%s(...)" % getattr(a0.func, "id", "?")
    return None


def graf(fisiere=None, rad=None):
    """`(arbori, rute, definitii, module_main)`.

    * `arbori[(fisier, nume)]` — arborele de domenii al fiecărei DEFINIȚII, nu al fiecărui nume;
    * `definitii[nume]` — `[(fisier, linie)]`, ca să se știe ce nume e omonim;
    * `rute[(fisier, nume)]` — `[(metoda, cale, poarta)]`;
    * `module_main[fisier]` — funcțiile chemate din `if __name__ == "__main__"`.
    """
    rad = rad or RAD
    fisiere = fisiere or _fisiere()
    cunoscute = {os.path.relpath(c, rad).replace(os.sep, "/") for c in fisiere}
    arbori, rute, definitii, module_main = {}, {}, {}, {}
    for cale in fisiere:
        rel = os.path.relpath(cale, rad).replace(os.sep, "/")
        try:
            radacina = ast.parse(io.open(cale, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        alias_fis = alias_module(_noduri_fara_functii(radacina), cunoscute)
        for nod in ast.walk(radacina):
            if isinstance(nod, ast.If) and _e_main(nod):
                module_main[rel] = _lucratori(nod)
                continue
            if not isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            definitii.setdefault(nod.name, []).append((rel, nod.lineno))
            alias = dict(alias_fis)
            alias.update(alias_module(ast.walk(nod), cunoscute))
            arbori.setdefault((rel, nod.name), []).extend(arbore_functie(nod, rel, alias))
            poarta = _poarta(nod)
            for d in nod.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                        and d.func.attr in ("get", "post", "put", "delete", "patch")
                        and d.args and isinstance(d.args[0], ast.Constant)):
                    rute.setdefault((rel, nod.name), []).append(
                        (d.func.attr.upper(), d.args[0].value, poarta))
    return arbori, rute, definitii, module_main


def rezolva(nume, rel_gazda, modul, arbori, definitii):
    """Cheile de definiție ale unui apel, în trei trepte. `(chei, omonim)`.

    1. **modulul** — `facturi_api.emite(...)` cu `facturi_api` alias de import cunoscut;
    2. **fișierul gazdă** — funcția e definită chiar acolo;
    3. **toate** definițiile cu acel nume — reunite, și marcate `omonim`.

    Treapta 3 e singura care supra-numără, și e singura marcată. Fără primele două, cele ~50 de
    module de migrare (fiecare cu un `_main()`) se contopeau într-una singură."""
    if modul and (modul, nume) in arbori:
        return [(modul, nume)], False
    if (rel_gazda, nume) in arbori:
        return [(rel_gazda, nume)], False
    locuri = definitii.get(nume, [])
    chei = [(rel, nume) for rel, _l in locuri if (rel, nume) in arbori]
    return chei, len(chei) > 1


# ============================================================================
#  STRATUL 3 — expandarea unei căi
# ============================================================================

def expandeaza(cheie, arbori, definitii, adancime=ADANCIME, _stiva=(), _memo=None,
               _omonim=False):
    """Arborele căii care pleacă din definiția `cheie = (fisier, nume)`, cu apelurile expandate."""
    _memo = _memo if _memo is not None else {}
    m = (cheie, adancime, _omonim)
    if m in _memo:
        return _memo[m]
    if cheie in _stiva or adancime <= 0 or cheie not in arbori:
        return []
    _memo[m] = []
    out, _c = _expandeaza_lista(arbori[cheie], cheie, arbori, definitii, adancime,
                                _stiva + (cheie,), _memo, _omonim, [0])
    _memo[m] = out
    return out


def _expandeaza_lista(noduri, gazda, arbori, definitii, adancime, stiva, memo, omonim, contor):
    rel_gazda, nume_gazda = gazda
    out = []
    for n in noduri:
        if contor[0] > MAX_NODURI:
            out.append(("ev", "TRUNCHIAT", "peste %d noduri" % MAX_NODURI, rel_gazda, 0,
                        "normal", (nume_gazda,), False))
            break
        contor[0] += 1
        if n[0] == "ev":
            _f, fel, det, fis, lin, ram = n
            out.append(("ev", fel, det, fis, lin, ram, (nume_gazda,), omonim))
        elif n[0] == "domeniu":
            sub, _c = _expandeaza_lista(n[1], gazda, arbori, definitii, adancime, stiva,
                                        memo, omonim, contor)
            out.append(("domeniu", sub, n[2], n[3], n[4], (nume_gazda,)))
        else:
            _f, chemat, fis, lin, ram, modul = n
            chei, om = rezolva(chemat, rel_gazda, modul, arbori, definitii)
            for ch in chei:
                sub = expandeaza(ch, arbori, definitii, adancime - 1, stiva, memo,
                                 omonim or om)
                out.extend(_prefixeaza(sub, nume_gazda, omonim or om, ram))
                contor[0] += len(sub)
    return out, contor


def _prefixeaza(noduri, gazda, omonim, ram_apel="normal"):
    out = []
    for n in noduri:
        if n[0] == "domeniu":
            out.append(("domeniu", _prefixeaza(n[1], gazda, omonim, ram_apel), n[2], n[3],
                        _compune_ramura(ram_apel, n[4]), (gazda,) + n[5]))
        else:
            out.append(n[:5] + (_compune_ramura(ram_apel, n[5]), (gazda,) + n[6],
                                n[7] or omonim))
    return out


# ============================================================================
#  DOMENIILE unei căi — ce scrie fiecare tranzacție
# ============================================================================

def domenii(arbore):
    """`([domeniu, ...], secventa_plata)`.

    Un domeniu e `{"id", "parinte", "loc", "via", "scrieri", "externe", "frontiere"}`.
    Domeniul `0` e cel IMPLICIT — ce se întâmplă în afara oricărui `with get_conn`, adică în
    tranzacția apelantului (pentru un punct de intrare: în nicio tranzacție).
    """
    lista = [{"id": 0, "parinte": None, "loc": "(în afara oricărui get_conn)", "via": "",
              "scrieri": [], "externe": [], "frontiere": [], "blocaje": []}]
    plat = []

    def coboara(noduri, curent):
        for n in noduri:
            if n[0] == "domeniu":
                d = {"id": len(lista), "parinte": curent, "via": " -> ".join(n[5]),
                     "loc": "%s:%d" % (n[2], n[3]), "ramura": n[4],
                     "scrieri": [], "externe": [], "frontiere": [], "blocaje": []}
                lista.append(d)
                plat.append(("DESCHIDE", d["id"], d["loc"], n[4], " -> ".join(n[5]), False,
                     " -> ".join(n[5])))
                coboara(n[1], d["id"])
                plat.append(("INCHIDE", d["id"], d["loc"], n[4], " -> ".join(n[5]), False,
                     " -> ".join(n[5])))
                continue
            _f, fel, det, fis, lin, ram, via, omonim = n
            e = {"detaliu": det, "loc": "%s:%d" % (fis, lin), "ramura": ram,
                 "via": " -> ".join(via), "omonim": omonim, "domeniu": curent}
            cheie = {"scriere": "scrieri", "extern": "externe", "frontiera": "frontiere",
                     "blocaj": "blocaje"}.get(fel)
            if cheie:
                lista[curent][cheie].append(e)
            plat.append((fel.upper(), curent, e["loc"], ram, det, omonim, e["via"]))

    coboara(arbore, 0)
    return lista, plat


# ============================================================================
#  CELE ȘASE SEMNE
# ============================================================================

_MODEL_CITIRE = None


def model_citire():
    """Tabelele modelului de citire — DERIVATE din `DEPENDENTE_P2.md`, nu scrise din memorie."""
    global _MODEL_CITIRE
    if _MODEL_CITIRE is not None:
        return _MODEL_CITIRE
    nume = set()
    cale = os.path.join(RAD, "DEPENDENTE_P2.md")
    if os.path.exists(cale):
        text = io.open(cale, encoding="utf-8", errors="replace").read()
        nume |= set(re.findall(r"`([a-z_]*rezumat[a-z_]*)`", text))
        nume |= set(re.findall(r"`(p2_[a-z_]+)`", text))
    _MODEL_CITIRE = {n for n in nume if not n.endswith("_md")} or {"firma_rezumat"}
    return _MODEL_CITIRE


def _e_model(det):
    tabel = det.split("|")[2]
    return tabel in model_citire() or "rezumat" in tabel


def semne(dom, plat):
    """`{cod: motiv}` pentru cele șase semne cerute de comandă."""
    out = {}
    scriitoare = [d for d in dom if d["scrieri"]]
    domenii_reale = [d for d in dom if d["id"] != 0]
    toate_scrieri = [s for d in dom for s in d["scrieri"]]
    toate_externe = [e for d in dom for e in d["externe"]]
    commituri = [f for d in dom for f in d["frontiere"]
                 if f["detaliu"] in ("commit", "savepoint", "rollback_to", "release")]

    if len(domenii_reale) > 1 or commituri:
        out["C1"] = "%d domenii tranzacționale%s" % (
            len(domenii_reale),
            (" + %d frontiere explicite (%s)" % (
                len(commituri), ", ".join(sorted({c["detaliu"] for c in commituri}))))
            if commituri else "")
    tabele = {(s["detaliu"].split("|")[1], s["detaliu"].split("|")[2]) for s in toate_scrieri}
    surse = {t[0] for t in tabele}
    if len(tabele) > 1:
        out["C2"] = "%d tabele în %d surse (%s)" % (
            len(tabele), len(surse), ", ".join(sorted(surse)))
    if toate_scrieri and toate_externe:
        out["C3"] = "%d scrieri + %d efecte externe (%s)" % (
            len(toate_scrieri), len(toate_externe),
            ", ".join(sorted({e["detaliu"].split(":")[0] for e in toate_externe})))
    model = [s for s in toate_scrieri if _e_model(s["detaliu"])]
    if model and len(tabele) > len(model):
        out["C4"] = "scriere în sursă + model de citire (%s)" % ", ".join(
            sorted({s["detaliu"] for s in model}))
    if len(scriitoare) > 1:
        out["C5"] = "%d domenii SCRIU (%s)" % (
            len(scriitoare), ", ".join("#%d %s" % (d["id"], d["loc"]) for d in scriitoare[:6]))

    # C6 — între prima și ultima scriere de pe calea PLATĂ apare o frontieră sau un efect extern
    idx = [i for i, p in enumerate(plat) if p[0] == "SCRIERE" and _e_normal(p[3])]
    if len(idx) > 1:
        mijloc = set()
        for p in plat[idx[0] + 1:idx[-1]]:
            if p[0] in ("DESCHIDE", "INCHIDE") or p[0] == "EXTERN" or (
                    p[0] == "FRONTIERA" and p[4] in ("commit", "savepoint", "rollback_to")):
                if _e_normal(p[3]):
                    mijloc.add("%s/%s" % (p[0].lower(), p[4] if p[0] == "EXTERN"
                                          or p[0] == "FRONTIERA" else "domeniu #%d" % p[1]))
        if mijloc:
            out["C6"] = "între prima și ultima scriere: %s" % ", ".join(sorted(mijloc)[:6])
    return out


# ============================================================================
#  CELE TREI MĂRIMI CARE DECID CLASIFICAREA
#
#  Semnele C1..C6 spun „e un candidat". Ele nu spun „e o gaură". Mărimile de mai
#  jos sunt cele pe care le cere lista de acceptare a comenzii, iar fiecare se
#  calculează pe arbore, nu prin citire.
# ============================================================================

FEL_IREVERSIBIL = ("FS", "EMAIL", "RETEA", "SUBPROC", "JOB")


def _loc_stabil(loc, via):
    """`fisier:functie_gazda` — cheia sub care se judeca un efect extern.

    Linia se schimba la orice editare de deasupra; functia care gazduieste apelul, nu. Prima
    forma a registrului de verdicte era cheiata pe `fisier:linie`, iar prima reparatie din
    `spv_conector.py` a facut toate verdictele lui sa para statute."""
    fisier = loc.rsplit(":", 1)[0]
    gazda = (via or "").split(" -> ")[-1] or "?"
    return "%s:%s" % (fisier, gazda)


def analiza(dom, plat):
    """`dict` cu mărimile derivate ale unei căi.

    * `domenii_care_scriu` — peste câte tranzacții sunt împrăștiate scrierile. **>1 =
      TRANSACTION_OWNERSHIP_GAP**: între ele există un moment în care prima e comisă și a doua nu.
    * `partial_commit` — un `commit()` explicit pe calea normală, urmat de **altă scriere în
      același domeniu**. Tranzacția pe care use-case-ul crede că o deține a fost deja închisă;
      o eroare după el lasă prima jumătate comisă. *Clasa lui `_salveaza_cache` (04.09).*
    * `extern_in_tranzactie` — efect nedesfăcut de `rollback` (fișier, e-mail, apel extern,
      subproces, job) executat cât timp **există scrieri necomise** în domeniul lui. Dacă
      tranzacția cade după el, efectul rămâne, iar scrierea nu.

      **Ce NU e**: un efect de după un `commit()` explicit. `gdpr_sterge.executa` comite ÎNTÂI și
      abia apoi șterge fișierele de pe disc — și scrie de ce, lângă cod: *„un `rmtree` nu se dă
      înapoi, iar o tranzacție întoarsă ar lăsa firma în bază fără bonurile ei"*. O metrică oarbă
      la commitul explicit ar fi raportat exact ordinea CORECTĂ ca defect.
    """
    scriitoare = {d["id"] for d in dom if d["scrieri"]}
    partial, extern_in = [], []

    # partial commit: commit (normal) urmat de o scriere (normal) în ACELAȘI domeniu
    for i, e in enumerate(plat):
        if e[0] != "FRONTIERA" or not _e_normal(e[3]) or e[4] not in ("commit", "commit_sql"):
            continue
        for u in plat[i + 1:]:
            if u[0] == "INCHIDE" and u[1] == e[1]:
                break
            if u[0] == "SCRIERE" and u[1] == e[1] and _e_normal(u[3]):
                partial.append({"commit": e[2], "apoi_scrie": u[2], "detaliu": u[4],
                                "domeniu": e[1]})
                break

    # Domeniile care scriu ÎNTR-O BUCLĂ: acolo ordinea din sursă nu mai apără nimic, fiindcă
    # iterația a doua începe cu scrierea celei dintâi încă necomisă.
    scriu_in_bucla = {(e[1], b) for e in plat
                      if e[0] == "SCRIERE" and _e_normal(e[3]) and _e_bucla(e[3])
                      for b in _bucle(e[3])}
    # necomis[domeniu] = există scrieri în domeniul ăsta care încă n-au fost comise
    necomis = {}
    for e in plat:
        if e[0] == "DESCHIDE":
            necomis[e[1]] = False
        elif e[0] == "INCHIDE":
            necomis[e[1]] = False
        elif e[0] == "SCRIERE" and _e_normal(e[3]):
            necomis[e[1]] = True
        elif e[0] == "FRONTIERA" and _e_normal(e[3]) and e[4] in ("commit", "commit_sql"):
            necomis[e[1]] = False
        elif e[0] == "EXTERN" and _e_normal(e[3]) and (
                necomis.get(e[1])
                or any((e[1], b) in scriu_in_bucla for b in _bucle(e[3]))):
            if e[4].split(":")[0] in FEL_IREVERSIBIL:
                extern_in.append({"efect": e[4], "loc": e[2], "domeniu": e[1],
                                  "omonim": e[5], "unde": _loc_stabil(e[2], e[6])})
    return {
        "domenii_care_scriu": len(scriitoare),
        "partial_commit": partial,
        "extern_in_tranzactie": extern_in,
    }


# ============================================================================
#  INVENTARUL
# ============================================================================

def puncte_de_intrare(rute, module_main, arbori, definitii):
    """`[(fel, eticheta, cheie, poarta)]` — rutele HTTP și lucrătorii de fundal."""
    out = []
    for (rel, fn), lst in sorted(rute.items()):
        for metoda, cale, poarta in lst:
            out.append(("ruta", "%s %s" % (metoda, cale), (rel, fn), poarta))
    for rel, chemate in sorted(module_main.items()):
        for c in chemate:
            # NUMAI definiția din chiar modulul lucrătorului. Un nume care nu e definit acolo
            # (`cron.ruleaza`, `db.init_pool`) e ambalajul, nu lucrătorul — iar rezolvarea lui pe
            # omonimie ar fi produs trei căi false pentru fiecare job.
            if (rel, c) in arbori and (rel, c) not in rute:
                out.append(("fundal", "%s::__main__ -> %s()" % (rel, c), (rel, c), None))
    return out


def inventar(adancime=ADANCIME):
    """`(candidati, statistici)` — inventarul BRUT cerut de pasul A al comenzii."""
    return inventar_din(None, None, adancime)


def inventar_din(fisiere=None, rad=None, adancime=ADANCIME):
    """Acelasi inventar, pe un corpus DAT. Cu `fisiere=None` e chiar repo-ul.

    Exista pentru calibrarea negativa a completitudinii: se injecteaza cai sintetice care aprind
    cate un singur criteriu, si se arata pe ele ca mecanismul refuza inventarul daca raman
    neclasificate."""
    arbori, rute, definitii, module_main = graf(fisiere, rad)
    memo = {}
    intrari = puncte_de_intrare(rute, module_main, arbori, definitii)
    out, trunchiate = [], 0
    for fel, eticheta, cheie, poarta in intrari:
        arb = expandeaza(cheie, arbori, definitii, adancime, _memo=memo)
        dom, plat = domenii(arb)
        if any(p[0] == "TRUNCHIAT" for p in plat):
            trunchiate += 1
        sn = semne(dom, plat)
        if not sn:
            continue
        an = analiza(dom, plat)
        toate = [x for d in dom for x in d["scrieri"] + d["externe"] + d["frontiere"]]
        scrieri = [s2 for d in dom for s2 in d["scrieri"]]
        externe = [e for d in dom for e in d["externe"]]
        frontiere = [f for d in dom for f in d["frontiere"]]
        out.append({
            "fel": fel, "intrare": eticheta, "functie": cheie[1], "fisier": cheie[0],
            "poarta": poarta, "semne": sn, "analiza": an,
            # FAPTELE pe care se sprijina clasificarea pe clase structurale. `domenii_total`
            # numara TOATE domeniile caii, inclusiv pe cele care doar citesc — pe care lista
            # `domenii` de mai jos nu le poarta, fiindca ea tine numai domeniile cu evenimente.
            "fapte": {
                "domenii_total": len([d for d in dom if d["id"] != 0]),
                "domenii_care_scriu": an["domenii_care_scriu"],
                "scrieri_total": len(scrieri),
                "tabele": sorted({s2["detaliu"].split("|", 1)[1] for s2 in scrieri}),
                "externe_total": len(externe),
                "feluri_externe": sorted({e["detaliu"].split(":")[0] for e in externe}),
                "frontiere_explicite": sorted({f["detaliu"] for f in frontiere}),
                "scrieri_in_domeniul_apelantului":
                    len([s2 for d in dom if d["id"] == 0 for s2 in d["scrieri"]]),
            },
            "domenii_care_scriu": an["domenii_care_scriu"],
            "numai_omonim": bool(toate) and all(x["omonim"] for x in toate),
            "domenii": [{"id": d["id"], "loc": d["loc"], "via": d.get("via", ""),
                         "scrieri": d["scrieri"], "externe": d["externe"],
                         "frontiere": d["frontiere"], "blocaje": d["blocaje"]}
                        for d in dom if d["scrieri"] or d["externe"] or d["frontiere"]
                        or d["blocaje"]],
        })
    stat = {"intrari": len(intrari), "candidati": len(out), "trunchiate": trunchiate,
            "adancime": adancime,
            "ownership_gaps": len([x for x in out if x["domenii_care_scriu"] > 1]),
            "partial_commit_paths": len([x for x in out if x["analiza"]["partial_commit"]]),
            "extern_in_tranzactie_paths":
                len([x for x in out if x["analiza"]["extern_in_tranzactie"]])}
    return sorted(out, key=lambda x: (-x["domenii_care_scriu"], -len(x["semne"]),
                                      x["intrare"])), stat


# ============================================================================
#  CALIBRARE — ambele direcții (METODA §22)
# ============================================================================

CORPUS_MAIN = '''
from core import db
import requests, os, subprocess

def scrie_doua_tabele(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (nr) VALUES (%s)", (1,))
        cur.execute("UPDATE public.tenants SET nume = %s WHERE id = %s", ("x", 1))

def commit_la_mijloc(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO note (a) VALUES (1)")
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO linii (b) VALUES (2)")

def extern_apoi_scriere(conn):
    requests.post("https://exemplu", json={})
    with conn.cursor() as cur:
        cur.execute("UPDATE facturi SET trimis = true")

def doua_domenii_scriu():
    with db.get_conn() as a:
        with a.cursor() as cur:
            cur.execute("INSERT INTO public.jurnal (x) VALUES (1)")
    with db.get_conn("tenant_001") as b:
        with b.cursor() as cur:
            cur.execute("INSERT INTO facturi (y) VALUES (2)")

def un_domeniu_o_scriere():
    with db.get_conn("tenant_001") as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")

def numai_citeste(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM facturi WHERE id = %s", (1,))
    return cur.fetchall()

def citeste_fisier():
    return open("/tmp/x.txt").read()

def rollback_pe_eroare(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
    except Exception:
        conn.rollback()

def apel_care_deschide_a_doua():
    with db.get_conn("tenant_001") as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
        _ajutor_care_deschide()

def _ajutor_care_deschide():
    with db.get_conn() as p:
        with p.cursor() as cur:
            cur.execute("INSERT INTO public.audit (x) VALUES (1)")

def scrie_apoi_fisier(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (nr) VALUES (1)")
    with open("/tmp/f.xml", "w") as f:
        f.write("x")

def alias_intai(conn):
    from core import modul_a as _x
    return _x.adauga(conn)

def alias_al_doilea(conn):
    from core import modul_b as _x
    return _x.adauga(conn)

def efect_in_bucla(conn):
    for x in [1, 2, 3]:
        requests.post("https://exemplu", json={"x": x})
        with conn.cursor() as cur:
            cur.execute("INSERT INTO trimiteri (x) VALUES (%s)", (x,))

def efect_inainte_de_scriere_fara_bucla(conn):
    requests.post("https://exemplu", json={})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO trimiteri (x) VALUES (1)")

def bucla_prin_apel(conn):
    for x in [1, 2, 3]:
        _trimite_si_scrie(conn, x)

def _trimite_si_scrie(conn, x):
    requests.post("https://exemplu", json={"x": x})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO trimiteri (x) VALUES (%s)", (x,))

def doua_bucle_diferite(conn):
    for x in [1, 2]:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO trimiteri (x) VALUES (%s)", (x,))
    conn.commit()
    for y in ["a", "b"]:
        os.remove("/tmp/%s" % y)

def efect_dupa_commit_explicit():
    with db.get_conn("tenant_001") as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
        c.commit()
        os.remove("/tmp/dupa_commit.xml")

def efect_in_tranzactie():
    with db.get_conn("tenant_001") as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
        with open("/tmp/inauntru.xml", "w") as f:
            f.write("x")

def efect_dupa_tranzactie():
    with db.get_conn("tenant_001") as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO facturi (nr) VALUES (1)")
    with open("/tmp/dupa.xml", "w") as f:
        f.write("x")
'''

CORPUS_A = '''
def adauga(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO tabel_a (x) VALUES (1)")
'''

CORPUS_B = '''
def adauga(conn):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO tabel_b (y) VALUES (2)")
'''


def calibreaza(verbose=True):
    """Instrumentul trebuie să vadă ce e acolo **și** să refuze ce nu e (METODA §22)."""
    import tempfile
    d = tempfile.mkdtemp(prefix="calib_tranz_")
    os.makedirs(os.path.join(d, "core"), exist_ok=True)
    fisiere = []
    for rel, text in (("main.py", CORPUS_MAIN), ("core/modul_a.py", CORPUS_A),
                      ("core/modul_b.py", CORPUS_B)):
        cale = os.path.join(d, rel.replace("/", os.sep))
        with io.open(cale, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        fisiere.append(cale)
    arbori, _r, definitii, _m = graf(fisiere, rad=d)
    rel = "main.py"

    def s(fn):
        dom, plat = domenii(expandeaza((rel, fn), arbori, definitii, ADANCIME, _memo={}))
        return semne(dom, plat), dom, analiza(dom, plat)

    def tabele(fn):
        return {e["detaliu"].split("|")[2] for dm in s(fn)[1] for e in dm["scrieri"]}

    def nr_scriitoare(fn):
        return len([x for x in s(fn)[1] if x["scrieri"]])

    probe = [
        ("vede două tabele distincte (C2)", "C2" in s("scrie_doua_tabele")[0]),
        ("vede commit la mijloc (C1+C6)", {"C1", "C6"} <= set(s("commit_la_mijloc")[0])),
        ("vede efect extern + scriere (C3)", "C3" in s("extern_apoi_scriere")[0]),
        ("vede două domenii care scriu (C5)", "C5" in s("doua_domenii_scriu")[0]),
        ("vede al doilea domeniu prin APEL", "C5" in s("apel_care_deschide_a_doua")[0]),
        ("numără corect domeniile scriitoare", nr_scriitoare("doua_domenii_scriu") == 2),
        ("vede scriere → fișier (C3)", "C3" in s("scrie_apoi_fisier")[0]),
        ("vede commitul parțial ca mărime",
         len(s("commit_la_mijloc")[2]["partial_commit"]) == 1),
        ("vede efectul ireversibil ÎN tranzacție",
         len(s("efect_in_tranzactie")[2]["extern_in_tranzactie"]) == 1),
        ("vede efectul ireversibil din BUCLĂ",
         len(s("efect_in_bucla")[2]["extern_in_tranzactie"]) == 1),
        ("vede bucla și PRIN APEL",
         len(s("bucla_prin_apel")[2]["extern_in_tranzactie"]) == 1),
        ("NU împletește două BUCLE diferite",
         s("doua_bucle_diferite")[2]["extern_in_tranzactie"] == []),
        ("NU aprinde pe același tipar FĂRĂ buclă",
         s("efect_inainte_de_scriere_fara_bucla")[2]["extern_in_tranzactie"] == []),
        ("NU numără efectul de DUPĂ un `commit()` explicit",
         s("efect_dupa_commit_explicit")[2]["extern_in_tranzactie"] == []),
        # aliasul se citește pe DOMENIU DE VIZIBILITATE, nu pe fișier
        ("aliasul `_x` duce la modul_a în prima funcție", tabele("alias_intai") == {"tabel_a"}),
        ("același alias duce la modul_b în a doua", tabele("alias_al_doilea") == {"tabel_b"}),
        # NEGATIVE — nu trebuie inventate
        ("NU aprinde pe o citire curată", s("numai_citeste")[0] == {}),
        ("NU ia `open()` de citire ca efect", s("citeste_fisier")[0] == {}),
        ("NU aprinde pe un domeniu cu o scriere", s("un_domeniu_o_scriere")[0] == {}),
        ("NU confundă `rollback` din `except`",
         s("rollback_pe_eroare")[0].get("C6") is None),
        ("un domeniu scriitor, nu doi", nr_scriitoare("un_domeniu_o_scriere") == 1),
        ("NU numără ca ireversibil un efect de DUPĂ tranzacție",
         s("efect_dupa_tranzactie")[2]["extern_in_tranzactie"] == []),
    ]
    ok = all(r for _n, r in probe)
    if verbose:
        print("CALIBRARE scan_tranzactii — ambele direcții (METODA §22):")
        for nume, rez in probe:
            print("  %-42s %s" % (nume, "OK" if rez else "PICAT"))
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
    L.append("INVENTARUL BRUT AL OPERAȚIILOR COMPUSE — derivat mecanic din cod")
    L.append("Generat cu: ./venv/bin/python -m scripts.scan_tranzactii --inventar")
    L.append("Puncte de intrare parcurse: %d · candidați: %d · adâncime %d · căi trunchiate: %d"
             % (stat["intrari"], stat["candidati"], stat["adancime"], stat["trunchiate"]))
    L.append("Un candidat = o cale cu cel puțin unul din cele șase semne cerute de comandă.")
    L.append("Găuri de proprietate (scrieri în >1 domeniu): %d · commituri parțiale: %d · "
             "efecte ireversibile în tranzacție: %d"
             % (stat["ownership_gaps"], stat["partial_commit_paths"],
                stat["extern_in_tranzactie_paths"]))
    L.append("=" * 78)
    L.append("")
    for x in inv:
        L.append("%s   [%s]  domenii care scriu: %d"
                 % (x["intrare"], ", ".join(sorted(x["semne"])), x["domenii_care_scriu"]))
        L.append("    handler : %s()  în %s   poarta: %s"
                 % (x["functie"], x["fisier"], x["poarta"] or "-"))
        for cod in sorted(x["semne"]):
            L.append("    %-3s : %s" % (cod, x["semne"][cod]))
        an = x["analiza"]
        if an["partial_commit"]:
            for pc in an["partial_commit"]:
                L.append("    !! COMMIT PARȚIAL : commit la %s, apoi scrie %s la %s (domeniu #%d)"
                         % (pc["commit"], pc["detaliu"], pc["apoi_scrie"], pc["domeniu"]))
        for ex in an["extern_in_tranzactie"]:
            L.append("    !! EFECT ÎN TRANZACȚIE : %s la %s (domeniu #%d)%s"
                     % (ex["efect"], ex["loc"], ex["domeniu"],
                        "  (omonim)" if ex["omonim"] else ""))
        if x["numai_omonim"]:
            L.append("    ATENȚIE : toate evenimentele vin din nume cu mai multe definiții")
        for d in x["domenii"]:
            L.append("    domeniu #%d  %s   %s" % (d["id"], d["loc"], d["via"]))
            for cheie, et in (("scrieri", "scrie"), ("externe", "extern"),
                              ("frontiere", "front"), ("blocaje", "blocaj")):
                for e in d[cheie][:25]:
                    L.append("        %-6s %-34s %-26s [%s] via %s%s"
                             % (et, e["detaliu"], e["loc"], e["ramura"], e["via"],
                                "  (omonim)" if e["omonim"] else ""))
                if len(d[cheie]) > 25:
                    L.append("        %-6s ... încă %d" % (et, len(d[cheie]) - 25))
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    if not calibreaza():
        sys.exit(2)
    print()
    adancime = ADANCIME
    for a in sys.argv[1:]:
        if a.startswith("--adancime="):
            adancime = int(a.split("=", 1)[1])
    inv, stat = inventar(adancime)
    print("PUNCTE DE INTRARE: %d · CANDIDAȚI: %d · trunchiate: %d"
          % (stat["intrari"], stat["candidati"], stat["trunchiate"]))
    nr = {}
    for x in inv:
        for c in x["semne"]:
            nr[c] = nr.get(c, 0) + 1
    print("  " + " · ".join("%s: %d" % (c, nr[c]) for c in sorted(nr)))
    multi = [x for x in inv if x["domenii_care_scriu"] > 1]
    print("  TRANSACTION_OWNERSHIP_GAPS (scrieri în >1 domeniu): %d" % stat["ownership_gaps"])
    print("  PARTIAL_COMMIT_PATHS (commit apoi scrie, în același domeniu): %d"
          % stat["partial_commit_paths"])
    print("  EFECTE IREVERSIBILE ÎNĂUNTRUL UNEI TRANZACȚII CARE SCRIE: %d căi"
          % stat["extern_in_tranzactie_paths"])
    print()
    for x in multi[:80]:
        print("  %-2d %-56s %s" % (x["domenii_care_scriu"], x["intrare"][:56],
                                   ",".join(sorted(x["semne"]))))
    if len(multi) > 80:
        print("  ... încă %d" % (len(multi) - 80))
    if "--inventar" in sys.argv:
        _scrie(os.path.join(RAD, "masuratori", "p4", "inventar_brut.txt"), raport_text(inv, stat))
        _scrie(os.path.join(RAD, "masuratori", "p4", "inventar_brut.json"),
               json.dumps({"stat": stat, "candidati": inv}, ensure_ascii=False, indent=2))
