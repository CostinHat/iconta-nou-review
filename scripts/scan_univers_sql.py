# -*- coding: utf-8 -*-
"""Universul modulelor cu SQL, și AMESTECUL observat în cod (nu declarat).

DE CE (E2a, constatarea L1 a auditului). Registrul straturilor acoperea un univers derivat din două
definiții de „fiscal" plus modulele cu rute. Întrebarea care contează e alta: **orice modul al
aplicației care conține SQL**. Pe universul ăla, un modul nedeclarat e un modul despre care nimeni
n-a spus ce e.

DOUĂ CIFRE, CU NUME DIFERITE, ȘI ĂSTA E MIEZUL. `D4` — criteriul canonic al lui P7, `CLOSED_ACCEPTED`
— numără câte module **declară** două straturi (`mixt_cu`), și trebuie să rămână **0**. Amestecul
există totuși în cod, iar el se măsoară aici, pe observație, sub alt nume: **`D4b_MIXT_OBSERVAT`** =
module care au SQL **și** își deschid singure conexiunea sau comit. *O cifră veche și una nouă care
se ating primesc nume diferite* — altfel lărgirea universului ar fi redeschis o fază închisă printr-o
cifră, fără ca nimeni s-o fi cerut.

CLASA DE EXCLUDERE E NUMITĂ, nu tăcută: `MIGRARE_UNICA` = `core/migrare_*.py`, migrări care rulează o
dată și nu sunt straturi de aplicație. Câte sunt se raportează, ca să nu se ascundă nimic în ea.

UNDE E OARB: SQL-ul construit din bucăți la rulare nu se vede, iar `execute` pe un alt fel de obiect
(nu cursor) se numără la fel. Instrumentul spune **unde se atinge**, nu cât de tare.
"""
from __future__ import annotations

import ast
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

SQL = re.compile(r"\b(select|insert\s+into|update|delete\s+from|create\s+table|alter\s+table)\b",
                 re.I)
#: Migrările unice: rulează o dată, nu sunt strat de aplicație. Clasă NUMITĂ, nu tăcere.
MIGRARE_UNICA = "migrare_"


def _module_aplicatie():
    """`main.py` + `core/`. `scripts/`, `frontend_test/`, `date_test/`, `masuratori/` sunt unelte și
    date: un instrument care scrie SQL ca să măsoare nu e un depozit."""
    yield "main.py"
    cdir = os.path.join(RAD, "core")
    for f in sorted(os.listdir(cdir)):
        if f.endswith(".py") and not f.startswith(("test_", "scan_")):
            yield "core/" + f


def _arbore(cale, sursa=None):
    """Arborele modulului — sau al unei surse FABRICATE, ca garda să se poată calibra pe un univers
    pe care îl scrie ea, nu pe depozitul real."""
    try:
        if sursa is None:
            sursa = io.open(os.path.join(RAD, cale), encoding="utf-8", errors="ignore").read()
        return ast.parse(sursa)
    except (SyntaxError, OSError):
        return None


def sql_din(cale, sursa=None):
    """[(linia, sql)] — instrucțiunile SQL executate din modul (sau dintr-o sursă dată)."""
    arb = _arbore(cale, sursa)
    if arb is None:
        return []
    out = []
    for n in ast.walk(arb):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("execute", "executemany") and n.args):
            a = n.args[0]
            txt = None
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                txt = a.value
            elif isinstance(a, ast.JoinedStr):
                txt = "".join(v.value for v in a.values
                              if isinstance(v, ast.Constant) and isinstance(v.value, str))
            elif isinstance(a, ast.BinOp):
                txt = " ".join(v.value for v in ast.walk(a)
                               if isinstance(v, ast.Constant) and isinstance(v.value, str))
            if txt and SQL.search(txt):
                out.append((n.lineno, " ".join(txt.split())[:100]))
    return out


def deschide_sau_comite(cale, sursa=None):
    """(get_conn, commit) — de câte ori modulul își deschide singur conexiunea sau comite."""
    arb = _arbore(cale, sursa)
    if arb is None:
        return 0, 0
    g = c = 0
    for n in ast.walk(arb):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr == "get_conn":
                g += 1
            elif n.func.attr == "commit":
                c += 1
    return g, c


def universul():
    """{cale: [sql]} — modulele aplicației care conțin SQL, migrările INCLUSE."""
    return {c: s for c in _module_aplicatie() for s in [sql_din(c)] if s}


def migrari(univers=None):
    u = universul() if univers is None else univers
    return {c for c in u if os.path.basename(c).startswith(MIGRARE_UNICA)}


def fara_strat(univers=None):
    """Modulele cu SQL care n-au strat declarat — criteriul de ieșire al lui E2a: zero."""
    from core import straturi
    u = universul() if univers is None else univers
    decl = straturi.pe_cale()
    return sorted(c for c in u if c not in decl and c not in migrari(u))


def d4b_mixt_observat(univers=None):
    """[(cale, get_conn, commit, strat)] — amestecul OBSERVAT în cod, fără migrări.

    Nu e `D4`: acela numără declarații (`mixt_cu`) și rămâne 0, fiindcă P7 e închisă pe el.
    """
    from core import straturi
    u = universul() if univers is None else univers
    m = migrari(u)
    out = []
    for cale in sorted(u):
        if cale in m:
            continue
        g, c = deschide_sau_comite(cale)
        if g or c:
            out.append((cale, g, c, straturi.strat(cale)))
    return out


def repository_care_isi_deschid_conexiunea(univers=None):
    """Contradicția declarație↔cod: declarat REPOSITORY, dar își deschide conexiunea sau comite."""
    return [x for x in d4b_mixt_observat(univers) if x[3] == "REPOSITORY"]


if __name__ == "__main__":
    u = universul()
    mg = migrari(u)
    d4b = d4b_mixt_observat(u)
    repo = repository_care_isi_deschid_conexiunea(u)
    print("MODULE_CU_SQL (aplicatie)        = %d" % len(u))
    print("  MIGRARE_UNICA (clasa numita)   = %d" % len(mg))
    print("  in universul de declarat       = %d" % (len(u) - len(mg)))
    print("MODULE_CU_SQL_FARA_STRAT         = %d" % len(fara_strat(u)))
    print("D4b_MIXT_OBSERVAT                = %d" % len(d4b))
    print("REPOSITORY_CARE_ISI_DESCHID_CONEXIUNE_SAU_COMIT = %d" % len(repo))
    for cale, g, c, strat in d4b:
        print("   %-46s get_conn=%-2d commit=%-2d %s" % (cale, g, c, strat))
