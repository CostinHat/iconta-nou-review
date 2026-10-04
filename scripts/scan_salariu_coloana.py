# -*- coding: utf-8 -*-
"""scripts/scan_salariu_coloana.py — instrumentul gardului `core/test_2b_coloana.py` (punctul 4, 04.10.2026).

Răspunde la două întrebări, mecanic: (1) mai există în cod o expresie SQL care numește `salariu_brut` fără să țintească
`salariu_istoric`? (o a doua sursă a salariului contractual, după retragerea coloanei `salariati.salariu_brut`);
(2) ce coloane are `salariati` în `tenant_template.sql`?

    python scripts/scan_salariu_coloana.py
"""
import ast
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


_SQL = re.compile(r"\b(select|insert|update|alter)\b", re.I)


def sql_pe_coloana(rad=None):
    """(fișier, linie) pentru fiecare expresie SQL din cod care numește `salariu_brut` FĂRĂ să țintească `salariu_istoric`.

    Se citește TEXTUL SURSĂ al expresiei, nu doar șirul constant: numele tabelului vine adesea ca argument
    (`"SELECT salariu_brut FROM %s" % _t(schema, "salariati")`, f-string-uri cu `{schema}.salariati`). Prima formă a
    gardului citea doar constantele și a lăsat să treacă exact puntea și SELECT-ul din `stat_plata_api` (mutațiile M1/M2)."""
    RAD = rad or globals()["RAD"]
    out = []
    fisiere = [f for f in glob.glob(os.path.join(RAD, "core", "*.py")) if not os.path.basename(f).startswith("test_")]
    fisiere += [f for f in [os.path.join(RAD, "main.py")] if os.path.exists(f)] + glob.glob(os.path.join(RAD, "scripts", "*.py"))
    fisiere += glob.glob(os.path.join(RAD, "date_test", "**", "*.py"), recursive=True)
    for f in fisiere:
        if f.endswith("migrare_2b_coloana.py"):
            continue   # migrarea care o scoate e singura care are voie s-o numească
        src = open(f, encoding="utf-8").read()
        t = ast.parse(src)
        # docstring-urile (expresii-șir de sine stătătoare) descriu, nu interoghează — se sar
        docs = {id(n.value) for n in ast.walk(t) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
        vazute = set()
        if "salariu_brut" not in src:
            continue
        linii = {i for i, l in enumerate(src.split("\n"), 1) if "salariu_brut" in l}

        def _atinge(p):
            return any(p.lineno <= i <= (p.end_lineno or p.lineno) for i in linii)
        noduri = [p for p in ast.walk(t) if isinstance(p, (ast.Constant, ast.JoinedStr, ast.BinOp, ast.Call)) and _atinge(p)]
        tinte = [(p.lineno, p.end_lineno or p.lineno) for p in noduri if isinstance(p, (ast.BinOp, ast.Call))
                 and "salariu_istoric" in (ast.get_source_segment(src, p) or "")]
        for n in noduri:
            if id(n) in docs:
                continue
            if isinstance(n, ast.Constant) and not isinstance(n.value, str):
                continue
            seg = ast.get_source_segment(src, n) or ""
            if not (re.search(r"\bsalariu_brut\b", seg) and _SQL.search(seg)):
                continue
            if "salariu_istoric" in seg or n.lineno in vazute:
                continue
            # o expresie mai mare care o conține poate numi tabela (BinOp/Call) — se judecă cea mai mare
            if any(a0 <= n.lineno <= a1 for a0, a1 in tinte):
                continue
            vazute.add(n.lineno)
            out.append((os.path.relpath(f, RAD), n.lineno))
    return sorted(set(out))


def coloane_template(tabela="salariati", rad=None):
    """Numele coloanelor din `CREATE TABLE TENANT_PLACEHOLDER.<tabela> (…)` din tenant_template.sql."""
    tpl = open(os.path.join(rad or RAD, "tenant_template.sql"), encoding="utf-8").read()
    corp = re.search(r"CREATE TABLE TENANT_PLACEHOLDER\.%s \((.*?)\n\);" % re.escape(tabela), tpl, re.S).group(1)
    return {l.split()[0] for l in corp.split("\n") if l.strip() and not l.strip().startswith("--")
            and not l.strip().upper().startswith("CONSTRAINT")}


if __name__ == "__main__":
    print("SQL pe coloana retrasa:", sql_pe_coloana() or "niciunul")
    print("salariati:", sorted(coloane_template()))
