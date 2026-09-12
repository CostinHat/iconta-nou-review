# -*- coding: utf-8 -*-
"""P7 — cele TREI verificari mecanice ale separarii pe straturi, derivate din cod.

TEXTUL CANONIC, `PLAN_HARDENING.md:748-751`, verbatim: *„Mecanic, nu prin impresie: un motor fiscal
nu importa `db`; un use-case nu construieste `HTTPException`; ruta nu contine SQL. Fiecare din cele
trei se poate deriva cu `ast` si se poate garda cu clichet."* Deci nu una, ci TREI masuratori, fiecare
cu universul ei. Fisierul asta le produce; clasificarea lor e in `scripts/p7_clasificare.py`.

DE CE TREI DETECTOARE SI NU UNUL. Cele trei intrebari au universuri diferite (rute · module fiscale ·
module de sub stratul HTTP) si moduri diferite de orbire. Contopite intr-o cifra, un detector orb ar
fi acoperit de ceilalti doi, iar totalul ar parea sanatos.

---

## D1 — SQL IN RUTA

UNIVERS: fiecare functie decorata cu `@<obiect>.<metoda>(...)`, metoda dintre cele HTTP. Se citeste
din AST, nu dintr-o lista scrisa: 421 de rute, aceeasi populatie pe care o numara si verificatorul.

ITEM: un apel `.execute(...)` / `.executemany(...)` a carui TINTA e un cursor de baza de date,
lexical in corpul rutei.

CE NU E LEXICAL, si de aia detectorul nu se opreste la nume: `.execute` exista si pe alte obiecte
(executoare de fire, procese). Discriminatorul e LEGAREA: se urmareste, in corpul functiei, ce nume
sunt legate de `<ceva>.cursor()` — prin `with ... as X` sau prin `X = ...cursor()`. Un `.execute` pe
un nume nelegat asa e raportat separat, ca `NECUNOSCUT`, nu numarat drept SQL. *Un detector care ar
numara orice `.execute` ar masura cuvantul, nu operatia.*

## D2 — MOTOR FISCAL CARE ATINGE BAZA

UNIVERS: modulele DECLARATE `FISCAL_ENGINE` in `core/straturi.py`. Atat — nicio euristica, nicio a
doua definitie.

ITEM: un import sau o folosire a lui `core.db` intr-un asemenea modul.

[V3, 13.09.2026] PANA AZI universul venea din doua instrumente care nu cadeau de acord: generatoarele
celor noua declaratii (25 de module) si modulele care poarta valori fiscale (104). Sapte module
cadeau intre ele, iar pentru ele intrebarea nu se putea decide — clasa `EVIDENCE_LIMITATION`. *Un
criteriu al carui univers nu e definit nu e o masuratoare, e o aproximare.* Registrul le-a dat
fiecaruia un strat, iar cele doua instrumente raman ce erau: definesc UNIVERSUL REGISTRULUI (cine
trebuie sa aiba o declaratie), nu raspunsul.

## D4 — MODULE CARE FAC DOUA STRATURI DEODATA

ITEM: un modul declarat cu `mixt_cu` in registru. Nu e o toleranta si nu e un al cincilea strat: e
pozitia de lucru a valului care separa. Comanda V3 o cere explicit clasificata `ACTION_REQUIRED`.

## D3 — HTTP SUB STRATUL HTTP

UNIVERS: modulele din `core/` care nu sunt rute (`core/` nu contine stratul HTTP, prin conventia
casei: rutele stau in `main.py`).

ITEM: o constructie `HTTPException(...)` intr-un asemenea modul. Textul canonic o cere despre
„use-case"; stratul acela nu exista inca, iar pana exista, intrebarea masurabila e ACEEASI seam:
cine, de sub HTTP, vorbeste limba HTTP.

---

CE NU VEDE NICIUNUL, declarat:
  * SQL construit si executat prin ajutoare (`_exec(sql)`), daca ajutorul nu e in corpul rutei —
    detectorul e LEXICAL pe corpul functiei, deci masoara un PLAFON INFERIOR;
  * `HTTPException` ridicata printr-un alias (`from fastapi import HTTPException as HE`) — se prinde
    numele final al apelului, deci un alias ar scapa;
  * module fiscale care n-au generator probat (`bilant`, cele ~40 `dNNN` fara generator) — sunt in
    `in_afara()` la `scan_lanturi_declaratie`, si raman in afara si aici.
"""
from __future__ import annotations

import ast
import collections
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

METODE_HTTP = ("get", "post", "put", "delete", "patch", "head", "options")

#: Ce nu intra in nicio masuratoare, si de ce. Fiecare excludere e o REGULA, nu o omisiune.
EXCLUDERI = (
    ("core/test_*.py", "probe, nu cod care serveste cereri"),
    ("core/scan_*.py", "instrumente de masura, nu strat de aplicatie"),
    ("scripts/*", "unelte de lucru; nu sunt pe calea unei cereri"),
    ("_arhiva_*", "arhiva: cod scos din folosinta, pastrat ca istorie"),
    ("frontend_test/*", "probe de ecran"),
)

Item = collections.namedtuple("Item", "detector fisier linie simbol cale dovada")


def _sursa(rel):
    with io.open(os.path.join(RAD, rel), encoding="utf-8") as f:
        return f.read()


def _arbore(rel):
    return ast.parse(_sursa(rel))


def module_core():
    """Modulele din `core/` care nu sunt probe si nu sunt instrumente de masura."""
    baza = os.path.join(RAD, "core")
    return ["core/" + f for f in sorted(os.listdir(baza))
            if f.endswith(".py") and not f.startswith(("test_", "scan_"))]


# ============================================================
#  D1 — SQL IN RUTA
# ============================================================
def _decorator_ruta(nod):
    for d in getattr(nod, "decorator_list", []):
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Attribute) and f.attr in METODE_HTTP and isinstance(f.value, ast.Name):
            return "%s.%s" % (f.value.id, f.attr)
    return None


def fisiere_de_aplicatie():
    """`main.py` + modulele din `core/` care nu sunt probe si nu sunt instrumente.

    [13.09.2026] Prima forma cauta rute NUMAI in `main.py` — si a gresit: `core/spv_rute.py` are
    trei, montate prin `monteaza(app, ...)`. Detectorul si-a gasit singur punctul orb la prima
    rulare, fiindca D3 l-a raportat ca modul de `core/` care vorbeste HTTP. *Universul se DERIVA,
    nu se presupune din unde ne asteptam sa stea rutele.*
    """
    return ["main.py"] + module_core()


def rute_din_arbore(arb, rel):
    """[(fisier, nume, linie, decorator, nod)] dintr-un arbore deja parsat.

    Primitivele lucreaza pe ARBORE, nu pe cale, ca probele de calibrare sa poata trece prin ele un
    fragment scris de mana: un detector care se poate hrani numai din repo nu se poate arata nici
    gresind, nici nimerind.
    """
    out = []
    for nod in ast.walk(arb):
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
            dec = _decorator_ruta(nod)
            if dec:
                out.append((rel, nod.name, nod.lineno, dec, nod))
    return out


def rute(fisiere=None):
    """[(fisier, nume, linie, decorator, nod)] — universul lui D1, derivat din AST."""
    out = []
    for rel in (fisiere if fisiere is not None else fisiere_de_aplicatie()):
        try:
            arb = _arbore(rel)
        except SyntaxError:
            continue
        out += rute_din_arbore(arb, rel)
    return sorted(out, key=lambda x: (x[0], x[2]))


def _nume_cursoare(corp):
    """Numele legate, in corpul asta, de un `<ceva>.cursor()`.

    Aici se desparte operatia de cuvant: `.execute` pe un cursor e SQL, `.execute` pe altceva nu e.
    """
    legate = set()
    for x in ast.walk(corp):
        tinta = None
        if isinstance(x, ast.withitem):
            if (isinstance(x.context_expr, ast.Call)
                    and isinstance(x.context_expr.func, ast.Attribute)
                    and x.context_expr.func.attr == "cursor"):
                tinta = x.optional_vars
        elif isinstance(x, ast.Assign):
            if (isinstance(x.value, ast.Call) and isinstance(x.value.func, ast.Attribute)
                    and x.value.func.attr == "cursor"):
                tinta = x.targets[0] if x.targets else None
        if isinstance(tinta, ast.Name):
            legate.add(tinta.id)
    return legate


# ------------------------------------------------------------
#  FELUL instrucțiunii — READ / WRITE / TRANSACTION_CONTROL / UNKNOWN
# ------------------------------------------------------------
READ = "READ"
WRITE = "WRITE"
TRANSACTION_CONTROL = "TRANSACTION_CONTROL"
UNKNOWN = "UNKNOWN"

#: Cuvintele care deschid o scriere. Cautate ca CUVINTE (margini), nu ca subsiruri: un tabel numit
#: `insert_log` n-are voie sa transforme o citire in scriere.
_SCRIERE = ("INSERT", "UPDATE", "DELETE", "MERGE", "TRUNCATE")


def text_sql(nod):
    """Textul literal al argumentului, cat se poate afla STATIC. `None` daca nu incepe cu literal.

    [V1, 13.09.2026] Prefixul e de ajuns pentru a citi primul cuvant-cheie, si de-aia se accepta:
    `f"UPDATE {schema}.facturi SET " + ", ".join(...)` are partea dreapta necunoscuta, dar stanga
    spune limpede ce operatie e. *Ce nu incepe cu literal ramane UNKNOWN — nu se ghiceste.*
    """
    if isinstance(nod, ast.Constant) and isinstance(nod.value, str):
        return nod.value
    if isinstance(nod, ast.JoinedStr):
        out = []
        for x in nod.values:
            if isinstance(x, ast.Constant) and isinstance(x.value, str):
                out.append(x.value)
            else:
                out.append(" ")          # partea interpolata: un spatiu, ca sa nu lipeasca cuvinte
        return "".join(out)
    if isinstance(nod, ast.BinOp) and isinstance(nod.op, ast.Add):
        st = text_sql(nod.left)
        if st is None:
            return None
        dr = text_sql(nod.right)
        return st + (dr if dr is not None else " ")
    return None


def _curat(sql):
    """SQL-ul, fara linii goale si fara comentarii `--`, pe un singur rand, majuscule."""
    linii = []
    for linie in sql.splitlines():
        l = linie.strip()
        if not l or l.startswith("--"):
            continue
        linii.append(l)
    return " ".join(linii).lstrip("( ").upper()


def _contine_cuvant(text, cuvinte):
    return any(re.search(r"\b%s\b" % c, text) for c in cuvinte)


def fel_sql(sql):
    """(clasa, cuvant) pentru textul unei instructiuni. `(UNKNOWN, None)` cand nu se poate sti.

    CE NU GHICESTE, declarat:
      * un `WITH` NU e citire doar fiindca incepe cu `WITH`: se cauta in tot corpul o operatie de
        scriere (`INSERT`/`UPDATE`/`DELETE`/`MERGE`), fiindca un CTE poate scrie;
      * `SET` e control de tranzactie NUMAI pe `search_path` — orice alt `SET` ramane UNKNOWN, ca sa
        nu intre o clasa intreaga pe usa din dos;
      * SQL fara prefix literal: UNKNOWN.
    """
    if sql is None:
        return UNKNOWN, None
    cap = _curat(sql)
    if not cap:
        return UNKNOWN, None
    if cap.startswith("SELECT"):
        return READ, "SELECT"
    if cap.startswith("WITH"):
        return (WRITE, "WITH_SCRIERE") if _contine_cuvant(cap, _SCRIERE) else (READ, "WITH_CITIRE")
    for c in _SCRIERE:
        if cap.startswith(c + " "):
            return WRITE, c
    if cap.startswith("SAVEPOINT") or cap.startswith("RELEASE SAVEPOINT") \
            or cap.startswith("ROLLBACK TO SAVEPOINT"):
        return TRANSACTION_CONTROL, "SAVEPOINT"
    if cap.startswith("SET LOCAL SEARCH_PATH") or cap.startswith("SET SEARCH_PATH"):
        return TRANSACTION_CONTROL, "SEARCH_PATH"
    return UNKNOWN, None


def _apel_la(rel, linie, arbore_cache={}):
    """Nodul `Call` de la (fisier, linie) — ca sa se poata citi argumentul instructiunii."""
    if rel not in arbore_cache:
        cache = {}
        for x in ast.walk(_arbore(rel)):
            if (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                    and x.func.attr in ("execute", "executemany")):
                cache.setdefault(x.lineno, x)
        arbore_cache[rel] = cache
    return arbore_cache[rel].get(linie)


def fel_itemului(it):
    """(clasa, cuvant) pentru un item D1."""
    n = _apel_la(it.fisier, it.linie)
    if n is None or not n.args:
        return UNKNOWN, None
    return fel_sql(text_sql(n.args[0]))


def d1_pe_fel(itemi=None):
    """{clasa: [Item]} — universul lui D1, despartit pe felul instructiunii."""
    itemi = d1_sql_in_ruta()[0] if itemi is None else itemi
    out = {READ: [], WRITE: [], TRANSACTION_CONTROL: [], UNKNOWN: []}
    for it in itemi:
        clasa, _cuvant = fel_itemului(it)
        out[clasa].append(it)
    return out


def d1_din_rute(lista_rute):
    """(gasite, necunoscute) pentru o listă de rute deja derivată — miezul lui D1."""
    gasite, necunoscute = [], []
    for rel, nume, linie, dec, nod in lista_rute:
        cursoare = _nume_cursoare(nod)
        for x in ast.walk(nod):
            if not (isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)):
                continue
            if x.func.attr not in ("execute", "executemany"):
                continue
            tinta = x.func.value
            nume_tinta = tinta.id if isinstance(tinta, ast.Name) else (
                tinta.attr if isinstance(tinta, ast.Attribute) else "<expresie>")
            item = Item("D1_SQL_IN_RUTA", rel, x.lineno, "%s.%s" % (nume_tinta, x.func.attr),
                        "%s (%s:%d)" % (nume, dec, linie),
                        "apel pe un nume legat de `.cursor()` in corpul rutei")
            if nume_tinta in cursoare:
                gasite.append(item)
            else:
                necunoscute.append(item._replace(
                    dovada="`.%s` pe `%s`, care NU e legat de `.cursor()` in corpul rutei"
                           % (x.func.attr, nume_tinta)))
    return gasite, necunoscute


def d1_sql_in_ruta():
    """[Item] pentru SQL executat lexical in corpul unei rute, si lista celor NECUNOSCUTE."""
    return d1_din_rute(rute())


# ============================================================
#  D2 — MOTOR FISCAL CARE ATINGE BAZA
# ============================================================
def module_fiscale():
    """(module, sursa) — modulele DECLARATE motor fiscal. O singura sursa: registrul."""
    from core import straturi
    return straturi.module_din_strat(straturi.FISCAL_ENGINE), "core/straturi.py::REGISTRU"


def generatoare_declaratii():
    """Generatoarele celor noua declaratii. NU mai defineste D2 — intra in universul registrului."""
    import scan_lanturi_declaratie as L
    module = set()
    for _declaratie, lista in L.generatoare().items():
        module.update("core/%s.py" % m for m in lista)
    return module


def module_cu_valori_fiscale():
    """Modulele care POARTA valori fiscale. Ca si cele de mai sus: intra in UNIVERSUL registrului,
    nu in raspunsul lui D2."""
    from core import scan_constante as C
    return {"core/" + h["f"] for h in C.inventar()}


def univers_registru():
    """Cine TREBUIE sa aiba o declaratie de strat — derivat din repo, nu scris.

    Reuniunea celor doua definitii candidate de „fiscal" cu modulele care poarta rute; fara
    instrumentele de masura si fara probe, care nu sunt strat de aplicatie. Un modul care intra
    maine in multimea asta si n-are declaratie pica poarta — asa ramane registrul exhaustiv fata de
    UNIVERS, nu fata de ziua in care a fost scris.
    """
    u = generatoare_declaratii() | module_cu_valori_fiscale() | {r[0] for r in rute()}
    return {m for m in u if not os.path.basename(m).startswith(("scan_", "test_"))}


def _atinge_db(rel):
    """[(linie, cum)] — importuri sau folosiri ale lui `core.db` in modulul asta."""
    out = []
    for x in ast.walk(_arbore(rel)):
        if isinstance(x, ast.ImportFrom):
            if (x.module or "") in ("core.db", "db"):
                out.append((x.lineno, "from %s import ..." % x.module))
            elif (x.module or "") == "core" and any(a.name == "db" for a in x.names):
                out.append((x.lineno, "from core import db"))
        elif isinstance(x, ast.Import):
            for a in x.names:
                if a.name in ("core.db", "db"):
                    out.append((x.lineno, "import %s" % a.name))
    return out


def d4_strat_mixt():
    """[Item] — modulele care ating doua straturi, luate din registru."""
    from core import straturi
    return [Item("D4_STRAT_MIXT", d.cale, 1, "%s + %s" % (d.strat, d.mixt_cu), d.cale, d.motiv)
            for d in straturi.mixte()]


def d2_motor_fiscal_cu_db():
    fiscale, sursa = module_fiscale()
    gasite = []
    for rel in sorted(fiscale):
        if not os.path.exists(os.path.join(RAD, rel)):
            continue
        for linie, cum in _atinge_db(rel):
            gasite.append(Item("D2_MOTOR_FISCAL_CU_DB", rel, linie, cum, rel,
                               "modul fiscal dupa %s" % sursa))
    return gasite


# ============================================================
#  D3 — HTTP SUB STRATUL HTTP
# ============================================================
def d3_http_sub_http():
    """[Item] — `HTTPException` construita SUB stratul HTTP, adica in afara unei rute.

    Excluderea rutelor nu e o toleranta: o ruta CHIAR e stratul HTTP, oriunde ar sta fisierul ei.
    `core/spv_rute.py` e exemplul care a impus deosebirea — trei rute montate din `core/`.
    """
    gasite = []
    for rel in module_core():
        try:
            arb = _arbore(rel)
        except SyntaxError:
            continue
        gasite += d3_din_arbore(arb, rel)
    return gasite


def d3_din_arbore(arb, rel):
    """Miezul lui D3, pe un arbore deja parsat. `id()` are sens numai in interiorul unei parsari,
    deci rutele se cauta in ACELASI arbore, nu intr-o a doua."""
    in_ruta = set()
    for rel_, _n, _l, _d, nod in rute_din_arbore(arb, rel):
        in_ruta.update(id(x) for x in ast.walk(nod))
    gasite = []
    for x in ast.walk(arb):
        if isinstance(x, ast.Call):
            f = x.func
            nume = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
            if nume == "HTTPException" and id(x) not in in_ruta:
                gasite.append(Item("D3_HTTP_SUB_HTTP", rel, x.lineno, "HTTPException(...)", rel,
                                   "constructie HTTP in afara oricarei rute"))
    return gasite


# ============================================================
#  Inventarul, intr-un singur loc
# ============================================================
def inventar():
    d1, d1_necunoscute = d1_sql_in_ruta()
    return {
        "rute": len(rute()),
        "module_core": len(module_core()),
        "D1": d1,
        "D1_necunoscute": d1_necunoscute,
        "D2": d2_motor_fiscal_cu_db(),
        "D3": d3_http_sub_http(),
        "D4": d4_strat_mixt(),
    }


def main():
    inv = inventar()
    print("P7 — universul, derivat din cod")
    print("  rute (universul D1)          : %d" % inv["rute"])
    print("  module core/ (universul D3)  : %d" % inv["module_core"])
    fiscale, sursa = module_fiscale()
    print("  module fiscale (universul D2): %d   <- %s" % (len(fiscale), sursa))
    print()
    for cheie in ("D1", "D2", "D3", "D4"):
        print("  %-22s %d itemi" % (cheie, len(inv[cheie])))
    print("  %-22s %d (apeluri `.execute` pe ceva ce nu e cursor)"
          % ("D1_necunoscute", len(inv["D1_necunoscute"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
