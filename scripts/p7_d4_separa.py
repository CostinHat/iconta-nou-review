# -*- coding: utf-8 -*-
"""P7 · valul D4 — instrumentul care scoate SQL-ul din modulele MIXTE, fara sa-l rescrie.

DE CE UN INSTRUMENT, si nu 215 editari cu mana. Universul e de **215 pozitii in 37 de module**
(derivat, nu numarat: `straturi.mixte()` + AST). O mutare facuta de mana pe atatea locuri are un mod
de esec propriu — parametrii schimbati de ordine, un `fetchone` devenit `fetchall`, un `%s` pierdut —
si niciunul nu se vede la citire. Instrumentul muta EXPRESII, nu text: primul argument al lui
`execute` pleaca **verbatim**, cu tot cu f-string si cu interpolarile lui; parametrii pleaca
verbatim; `fetchone`/`fetchall` se pastreaza cu felul lor.

CE FACE, exact:
  1. pentru fiecare `cur.execute(...)` dintr-un modul mixt, cauta FETCH-ul care il consuma — prima
     folosire a lui `cur.fetch*` din acelasi corp, oprindu-se la urmatorul `execute`;
  2. scrie in `core/repo_<modul>.py` o functie care primeste CURSORUL apelantului, executa aceeasi
     instructiune si intoarce acelasi fetch;
  3. inlocuieste in modul: instructiunea `execute` dispare, iar expresia `cur.fetch*()` devine apelul.

CE NU FACE, declarat:
  · nu atinge `commit`, `rollback`, `get_conn` — hotarele tranzactiei raman unde sunt (contract P4);
  · nu schimba niciun parametru, nicio ordine, niciun `%s`;
  · nu muta functii intregi si nu schimba nicio semnatura publica — deci probele existente raman
    verzi FARA sa fie rescrise, care e chiar criteriul din `PLAN_HARDENING.md`;
  · nu decide singur cand nu e sigur: orice pozitie pe care n-o poate rezolva mecanic o RAPORTEAZA
    si o lasa neatinsa. *Un instrument care ghiceste pe restul e mai rau decat unul care se opreste.*
"""
import ast
import builtins
import collections
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

_BUILTINS = set(dir(builtins))
_CUVINTE = ("select", "insert", "update", "delete", "with")


# ============================================================
#  Analiza unui modul
# ============================================================
class Analiza(object):
    def __init__(self, cale):
        self.cale = cale
        self.text = io.open(os.path.join(RAD, cale), encoding="utf-8").read()
        self.linii = self.text.split("\n")
        self.arb = ast.parse(self.text)
        self.parinte = {}
        for n in ast.walk(self.arb):
            for c in ast.iter_child_nodes(n):
                self.parinte[c] = n
        self.corp_al = {}       # statement -> (lista, index)
        for n in ast.walk(self.arb):
            for camp in ("body", "orelse", "finalbody"):
                corp = getattr(n, camp, None)
                if isinstance(corp, list):
                    for i, st in enumerate(corp):
                        self.corp_al[st] = (corp, i)
        self.functia = {}
        for fn in ast.walk(self.arb):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(fn):
                    self.functia.setdefault(n, fn)

    # ---- utilitare de sursa ----
    def sursa(self, nod):
        return ast.get_source_segment(self.text, nod)

    def interval(self, nod):
        """(linie_start, col_start, linie_stop, col_stop) — 0-indexate pe linii."""
        return (nod.lineno - 1, nod.col_offset, nod.end_lineno - 1, nod.end_col_offset)

    # ---- cursori ----
    def cursori(self, fn):
        nume = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.With):
                for it in n.items:
                    if (isinstance(it.context_expr, ast.Call)
                            and isinstance(it.context_expr.func, ast.Attribute)
                            and it.context_expr.func.attr == "cursor"
                            and isinstance(it.optional_vars, ast.Name)):
                        nume.add(it.optional_vars.id)
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                f = n.value.func
                if isinstance(f, ast.Attribute) and f.attr == "cursor":
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            nume.add(t.id)
        for a in getattr(fn, "args", ast.arguments(args=[])).args:
            if a.arg in ("cur", "cursor", "_cur"):
                nume.add(a.arg)
        return nume

    def pozitii(self):
        """[(nod_execute, statement, corp, index, fn, nume_cursor)] — fiecare o data."""
        out = []
        for n in ast.walk(self.arb):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("execute", "executemany")):
                continue
            fn = self.functia.get(n)
            nume_cur = self.cursori(fn) if fn is not None else set()
            t = n.func.value
            if not (isinstance(t, ast.Name) and t.id in nume_cur):
                out.append((n, None, None, None, fn, None))
                continue
            st = n
            while st not in self.corp_al and st in self.parinte:
                st = self.parinte[st]
            if st not in self.corp_al:
                out.append((n, None, None, None, fn, t.id))
                continue
            corp, i = self.corp_al[st]
            out.append((n, st, corp, i, fn, t.id))
        out.sort(key=lambda x: (x[0].lineno, x[0].col_offset))
        return out

    def fetch_pentru(self, corp, i, nume_cur, nod_exec):
        """Nodul `cur.fetchX()` care consuma execute-ul, sau None — NUMAI din instructiunea urmatoare.

        INGUSTAT dupa o regresie reala (13.09.2026). Prima forma cauta inainte pana gasea un fetch,
        sarind peste orice instructiune fara `execute`. In generatoarele de declaratie tiparul e insa:

            cur.execute(SQL)
            cere_coloane_cursor(cur, ..., "firma_profil")   # citeste cur.description
            prof = cur.fetchone()

        Mutand executia SI fetch-ul in depozit, garda de coloane ajungea sa ruleze inainte de query.
        33 de probe rosii, toate cu acelasi mesaj — prinse de propria gardă a casei, la prima rulare.

        Deci: orice sta intre `execute` si `fetch` inseamna ca ORDINEA conteaza, iar instrumentul nu
        are cum sti de ce. Atunci se muta numai `execute`, la locul lui, si fetch-ul ramane unde e.
        *Un instrument care sare peste ce pare nevinovat isi alege singur ce e nevinovat.*
        """
        if i + 1 >= len(corp):
            return None
        st = corp[i + 1]
        alte_exec = [x for x in ast.walk(st)
                     if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                     and x.func.attr in ("execute", "executemany")
                     and isinstance(x.func.value, ast.Name) and x.func.value.id == nume_cur]
        fetches = [x for x in ast.walk(st)
                   if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                   and isinstance(x.func.value, ast.Name) and x.func.value.id == nume_cur
                   and x.func.attr in ("fetchone", "fetchall", "fetchmany")]
        alte_folosiri = [x for x in ast.walk(st)
                         if isinstance(x, ast.Name) and x.id == nume_cur
                         and not (isinstance(self.parinte.get(x), ast.Attribute)
                                  and self.parinte[x].attr in ("fetchone", "fetchall", "fetchmany"))]
        if len(fetches) == 1 and not alte_exec and not alte_folosiri:
            return fetches[0]
        return None


# ============================================================
#  Generarea functiei de depozit
# ============================================================
def _nume_din_sql(expr, text_sursa):
    """`select_firma_profil` din SQL-ul mutat — citit din text, nu inventat."""
    brut = ""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        brut = expr.value
    elif isinstance(expr, ast.JoinedStr):
        # interpolarile devin `{x}`, nu dispar: altfel `INSERT INTO {schema}.tabel` ramane
        # `INSERT INTO .tabel`, tiparul nu potriveste, iar numele iese din alt cuvant-cheie.
        brut = "".join(v.value if isinstance(v, ast.Constant) else "{x}" for v in expr.values)
    else:
        s = ast.get_source_segment(text_sursa, expr) or ""
        brut = re.sub(r"[^A-Za-z0-9_%.\s]", " ", s)
    t = " ".join(brut.split()).lower()
    verb = next((c for c in _CUVINTE if t.startswith(c)), "sql")
    m = re.search(r"\b(?:from|into|update|join)\s+(?:\{[a-z_][a-z0-9_]*\}\.)?([a-z_][a-z0-9_]*)", t)
    tabel = m.group(1) if m else ""
    nume = ("%s_%s" % (verb, tabel)).strip("_") or "sql"
    return re.sub(r"[^a-z0-9_]", "_", nume)[:48]


def _legate_local(expr):
    """Numele LEGATE inauntrul expresiei: tinte de comprehensiune, parametri de lambda, walrus.

    Fara asta, `[date.get(c) for c in campuri]` ar da `c` drept nume liber, iar functia de depozit
    ar primi un parametru pe care apelantul nu-l are. *Prins de `ruff` la prima aplicare, nu de
    mine — si e a doua oara in doua valuri cand instrumentul greseste in directia „prea mult".*
    """
    legate = set()
    for n in ast.walk(expr):
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for g in n.generators:
                for t in ast.walk(g.target):
                    if isinstance(t, ast.Name):
                        legate.add(t.id)
        elif isinstance(n, ast.Lambda):
            for a in list(n.args.args) + list(n.args.posonlyargs) + list(n.args.kwonlyargs):
                legate.add(a.arg)
            for a in (n.args.vararg, n.args.kwarg):
                if a is not None:
                    legate.add(a.arg)
        elif isinstance(n, ast.NamedExpr) and isinstance(n.target, ast.Name):
            legate.add(n.target.id)
    return legate


def _legate_in_functie(fn):
    """Numele legate in corpul functiei gazda: argumente, atribuiri, tinte de `for` si de `with`.

    Exista fiindca un builtin POATE fi umbrit: `def manual_sterge(..., id)` face din `id` o valoare
    locala, iar un instrument care-l sare fiindca „e builtin" muta in depozit un nume care acolo
    redevine functia `id`. Prins pe date reale, cu `can't adapt type 'builtin_function_or_method'`.
    """
    legate = set()
    if fn is None:
        return legate
    a = getattr(fn, "args", None)
    if a is not None:
        for lista in (a.args, getattr(a, "posonlyargs", []), a.kwonlyargs):
            for x in lista:
                legate.add(x.arg)
        for x in (a.vararg, a.kwarg):
            if x is not None:
                legate.add(x.arg)
    for n in ast.walk(fn):
        tinte = []
        if isinstance(n, (ast.Assign,)):
            tinte = list(n.targets)
        elif isinstance(n, (ast.AugAssign, ast.AnnAssign, ast.For, ast.AsyncFor)):
            tinte = [n.target]
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            tinte = [it.optional_vars for it in n.items if it.optional_vars is not None]
        elif isinstance(n, ast.NamedExpr):
            tinte = [n.target]
        for t in tinte:
            for x in ast.walk(t):
                if isinstance(x, ast.Name):
                    legate.add(x.id)
    return legate


def _libere(expr, legate_fn=()):
    """Numele citite si nelegate in expresie — parametrii functiei de depozit.

    Un builtin ramane afara DOAR daca nu e umbrit de o legare din functia gazda.
    """
    legate = _legate_local(expr)
    nume = []
    for n in ast.walk(expr):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            if n.id in legate or n.id in nume:
                continue
            if n.id in _BUILTINS and n.id not in legate_fn:
                continue
            nume.append(n.id)
    return nume


def _reindenteaza(bloc, nou="    "):
    linii = bloc.split("\n")
    if len(linii) == 1:
        return bloc
    cap, rest = linii[0], linii[1:]
    comun = min((len(x) - len(x.lstrip()) for x in rest if x.strip()), default=0)
    return "\n".join([cap] + [(nou + x[comun:]) if x.strip() else "" for x in rest])


# ============================================================
#  Transformarea unui modul
# ============================================================
Rezultat = collections.namedtuple("Rezultat", "cale mutate ramase functii sursa_modul sursa_repo")


def separa(cale, prefix_repo="repo_"):
    a = Analiza(cale)
    baza = os.path.basename(cale)[:-3]
    modul_repo = "%s%s" % (prefix_repo, baza if baza != "main" else "main")
    editari = []           # (start_abs, stop_abs, text_nou)
    functii, folosite = [], collections.Counter()
    ramase = []

    def abs_poz(linie, col):
        return sum(len(x) + 1 for x in a.linii[:linie]) + col

    for nod, st, corp, i, fn, nume_cur in a.pozitii():
        if st is None or nume_cur is None:
            ramase.append((nod.lineno, "cursor nelegat sau pozitie neasezata",
                           fn.name if fn else "<modul>"))
            continue
        if not (isinstance(st, ast.Expr) and st.value is nod):
            ramase.append((nod.lineno, "execute folosit ca expresie, nu ca instructiune",
                           fn.name if fn else "<modul>"))
            continue
        sql_expr = nod.args[0] if nod.args else None
        if sql_expr is None:
            ramase.append((nod.lineno, "execute fara argument", fn.name if fn else "<modul>"))
            continue
        param_expr = nod.args[1] if len(nod.args) > 1 else None
        if len(nod.args) > 2 or nod.keywords:
            ramase.append((nod.lineno, "execute cu forma neasteptata (>2 argumente sau kwargs)",
                           fn.name if fn else "<modul>"))
            continue

        fetch = a.fetch_pentru(corp, i, nume_cur, nod)
        # parametrii functiei de depozit: numele libere din SQL + din parametri
        legate_fn = _legate_in_functie(fn)
        libere = _libere(sql_expr, legate_fn)
        if param_expr is not None:
            libere += [x for x in _libere(param_expr, legate_fn) if x not in libere]
        libere = [x for x in libere if x != nume_cur]

        nume = _nume_din_sql(sql_expr, a.text)
        folosite[nume] += 1
        if folosite[nume] > 1:
            nume = "%s_%d" % (nume, folosite[nume])

        sql_src = _reindenteaza(a.sursa(sql_expr), "    " + " " * len("cur.execute("))
        apel_exec = "cur.%s(%s%s)" % (nod.func.attr, sql_src,
                                      (", " + a.sursa(param_expr)) if param_expr is not None else "")
        semnatura = ", ".join(["cur"] + libere)
        corp_fn = ["def %s(%s):" % (nume, semnatura), "    " + apel_exec]
        fel = None
        if fetch is not None:
            fel = fetch.func.attr
            corp_fn.append("    return cur.%s()" % fel)
        functii.append("\n".join(corp_fn))

        argumente = ", ".join([nume_cur] + libere)
        apel = "_repo.%s(%s)" % (nume, argumente)

        # 1. scoate instructiunea `execute` (linia/liniile ei intregi)
        l0, _c0, l1, c1 = a.interval(st)
        start = abs_poz(l0, 0)
        stop = abs_poz(l1, c1)
        # include newline-ul si indentarea liniei, daca instructiunea ocupa linii proprii
        if a.text[stop:stop + 1] == "\n":
            stop += 1
        if fetch is None:
            indent = a.linii[l0][:len(a.linii[l0]) - len(a.linii[l0].lstrip())]
            editari.append((start, stop, "%s%s\n" % (indent, apel)))
        else:
            editari.append((start, stop, ""))
            fl0, fc0, fl1, fc1 = a.interval(fetch)
            editari.append((abs_poz(fl0, fc0), abs_poz(fl1, fc1), apel))

    if not functii:
        return Rezultat(cale, 0, ramase, [], None, None)

    editari.sort(key=lambda e: e[0], reverse=True)
    nou = a.text
    for start, stop, text in editari:
        nou = nou[:start] + text + nou[stop:]

    # importul depozitului, dupa ultimul import de nivel de modul
    linie_import = "from core import %s as _repo" % modul_repo
    if linie_import not in nou:
        arb2 = ast.parse(nou)
        ultim = 0
        for n in arb2.body:
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                ultim = n.end_lineno
        l = nou.split("\n")
        l.insert(ultim, linie_import)
        nou = "\n".join(l)

    antet = ANTET_REPO % {"modul": cale, "repo": modul_repo}
    sursa_repo = antet + "\n\n" + "\n\n\n".join(functii) + "\n"
    return Rezultat(cale, len(functii), ramase, functii, nou, sursa_repo)


ANTET_REPO = '''# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `%(modul)s`.

[P7 · valul D4, 13.09.2026] Statele in `%(modul)s`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""'''


# ============================================================
#  Linia de comanda
# ============================================================
def main():
    from core import straturi as R
    tinte = [d.cale for d in R.mixte()]
    if len(sys.argv) > 1 and sys.argv[1] != "--scrie":
        tinte = [x for x in sys.argv[1:] if x != "--scrie"]
    scrie = "--scrie" in sys.argv
    total_m, total_r = 0, 0
    for cale in sorted(tinte):
        r = separa(cale)
        total_m += r.mutate
        total_r += len(r.ramase)
        print("%-42s mutate=%-4d ramase=%d" % (cale, r.mutate, len(r.ramase)))
        for linie, motiv, fn in r.ramase:
            print("        l.%-6d %-52s (%s)" % (linie, motiv, fn))
        if scrie and r.sursa_modul:
            baza = os.path.basename(cale)[:-3]
            io.open(os.path.join(RAD, "core", "repo_%s.py" % baza), "wb").write(
                r.sursa_repo.encode("utf-8"))
            io.open(os.path.join(RAD, cale), "wb").write(r.sursa_modul.encode("utf-8"))
    print()
    print("TOTAL mutate=%d ramase=%d" % (total_m, total_r))


if __name__ == "__main__":
    main()
