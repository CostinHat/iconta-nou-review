# -*- coding: utf-8 -*-
"""scripts/scan_instrumente.py - FAZA 4: pe ce instrument sta fiecare garda, si a fost calibrat.

Criteriul largit de Costin (23.08.2026): nu se masoara doar „cate garzi isi iau dovada din proza" si
„cate raporteaza verde pe zero randuri", ci si PE CE INSTRUMENT sta fiecare garda, si daca acel
instrument a fost CALIBRAT - inclusiv pe modul lui propriu de esec.

DOUA MASURATORI, amandoua cu definitie STRUCTURALA (pe AST), nu lexicala:

  A. CALIBRARE. O functie de test calibreaza un instrument daca il apeleaza si are cel putin o
     aserttiune al carei capat asteptat e un LITERAL concret - un sir, un numar, o apartenenta la un
     literal. Aia pineaza un CAZ. O aserttiune fara literal (`assert rez`, `assert len(x) > 0`) e o
     proprietate, nu o calibrare. Negativa = aceleasi forme sub `not` / `not in`.

     PRIMA FORMA A ACESTUI INSTRUMENT CAUTA CUVANTUL „calibrare" in docstring si raporta `graf_temei`
     cu ZERO calibrari, desi are patru afirmatii pozitive si una negativa scrise din 01.08. Adica
     instrumentul care numara garzi ce-si iau dovada din proza isi lua dovada din proza. Prins pe un
     caz cunoscut, nu la recitire - de aceea calibrarea de mai jos e in garda, nu in comentariu.

  B. VERDE PE ZERO RANDURI (interdictia 19). O garda e CANDIDAT daca TOATE aserttiunile ei sunt
     negative (`not`, `<=`, `== 0`, `not in`) si niciuna nu afirma ca multimea pe care lucreaza e
     nenula. Atunci o multime goala - scan orbit, parsare rupta, campanie epuizata - o face verde
     fara sa fi comparat nimic.

     CE NU VEDE: o garda care se apara cu `return` devreme nu apare aici (aserttiunea de nenulitate
     exista, doar ca e ocolita) - exact cazul celor doua teste de secventa din R18. Deci cifra e un
     PLAFON INFERIOR, si cazul care a declansat masuratoarea NU e printre cele numarate.
"""

import ast
import collections
import pathlib
import re

RAD = pathlib.Path("/home/costin/iconta_nou")


def e_instrument(p):
    n = p.name
    return (n.startswith(("scan_", "sonda_", "audit_", "vigoare_"))
            or n in {"graf_temei.py", "agenda.py", "agenda_drift.py", "verificator_conformitate.py"})


def instrumente():
    out = [p for p in sorted(RAD.glob("core/*.py")) if e_instrument(p)]
    out += [p for p in sorted(RAD.glob("scripts/*.py")) if e_instrument(p)]
    return out


def _literal(n):
    """Nodul e un literal concret (sir/numar) sau o colectie de literali?"""
    if isinstance(n, ast.Constant):
        return isinstance(n.value, (str, int, float))
    if isinstance(n, (ast.Tuple, ast.List, ast.Set)):
        return bool(n.elts) and all(_literal(e) for e in n.elts)
    return False


def _clasifica(test, apeluri_instrument):
    """(pozitive, negative) — numarul de aserttiuni care pineaza un caz concret."""
    poz = neg = 0
    for n in ast.walk(test):
        if not isinstance(n, ast.Assert):
            continue
        t = n.test
        negat = False
        if isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not):
            negat, t = True, t.operand
        gasit = False
        for sub in ast.walk(t):
            if isinstance(sub, ast.Compare):
                capete = [sub.left] + list(sub.comparators)
                if any(_literal(c) for c in capete):
                    gasit = True
                    if any(isinstance(o, ast.NotIn) for o in sub.ops):
                        negat = True
        if gasit:
            if negat:
                neg += 1
            else:
                poz += 1
    return poz, neg


def analizeaza(cale, module_instrument):
    """{nume_test: (poz, neg, atinge_instrument)}"""
    try:
        tree = ast.parse(cale.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, OSError):
        return {}
    src = cale.read_text(encoding="utf-8", errors="replace")
    out = {}
    for n in ast.walk(tree):
        if not (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")):
            continue
        corp = ast.unparse(n) if hasattr(ast, "unparse") else src
        atinge = any(re.search(r"\b%s\b" % re.escape(m), corp) for m in module_instrument)
        poz, neg = _clasifica(n, atinge)
        out[n.name] = (poz, neg, atinge)
    return out



# --- B. verde pe zero randuri -------------------------------------------------


POZITIV = re.compile(r"\b(assert)\b")

def negativa(a):
    t = a.test
    if isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not):
        return True
    if isinstance(t, ast.Compare):
        for op, comp in zip(t.ops, t.comparators):
            if isinstance(op, (ast.LtE, ast.Lt)):
                return True
            if isinstance(op, ast.Eq) and isinstance(comp, ast.Constant) and comp.value == 0:
                return True
            if isinstance(op, ast.NotIn):
                return True
    return False

def afirma_nenul(fn):
    """Exista o aserttiune care cere ca ceva sa fie NENUL/peste prag?"""
    for a in ast.walk(fn):
        if not isinstance(a, ast.Assert):
            continue
        t = a.test
        if isinstance(t, ast.Name):                     # assert rows
            return True
        if isinstance(t, ast.Compare):
            for op in t.ops:
                if isinstance(op, (ast.GtE, ast.Gt, ast.In)):
                    return True
        if isinstance(t, ast.Call):                     # assert len(x)
            return True
    return False



def instrumente_si_calibrare():
    """[(nume, garzi_care_il_ating, are_test_propriu, teste, calib_poz, calib_neg)]"""
    teste = sorted(RAD.glob("core/test_*.py"))
    out = []
    for inst in instrumente():
        modul = inst.stem
        nf = sum(1 for t in teste
                 if re.search(r"\b%s\b" % re.escape(modul), t.read_text(encoding="utf-8", errors="replace")))
        ded = RAD / "core" / ("test_%s.py" % modul)
        if not ded.exists():
            out.append((inst.name, nf, False, 0, 0, 0))
            continue
        d = analizeaza(ded, {modul})
        out.append((inst.name, nf, True, len(d),
                    sum(v[0] for v in d.values()), sum(v[1] for v in d.values())))
    return out


def garzi_vacuabile():
    """[(fisier, test)] — garzi cu aserttiuni exclusiv negative si fara afirmatie de nenulitate."""
    cand, tot = [], 0
    for p in sorted(RAD.glob("core/test_*.py")):
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for fn in ast.walk(tree):
            if not (isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and fn.name.startswith("test_")):
                continue
            aserts = [a for a in ast.walk(fn) if isinstance(a, ast.Assert)]
            if not aserts:
                continue
            tot += 1
            if all(negativa(a) for a in aserts) and not afirma_nenul(fn):
                cand.append((p.name, fn.name))
    return cand, tot


if __name__ == "__main__":
    print("%-32s %6s %8s %6s %6s %6s" % ("instrument", "garzi", "test-ded", "teste", "calib+", "calib-"))
    for n, nf, ded, nt, poz, neg in instrumente_si_calibrare():
        print("%-32s %6d %8s %6s %6s %6s"
              % (n, nf, "DA" if ded else "NU", nt or "-", poz if ded else "-", neg if ded else "-"))
    cand, tot = garzi_vacuabile()
    print("\ngarzi cu aserttiuni: %d · candidate la verde-pe-zero: %d (%.1f%%)"
          % (tot, len(cand), 100.0 * len(cand) / max(tot, 1)))
