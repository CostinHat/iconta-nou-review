# -*- coding: utf-8 -*-
"""scripts/scan_instrumente.py - FAZA 4: pe ce instrument sta fiecare garda, si a fost calibrat.

Criteriul largit de Costin (23.08.2026): nu se masoara doar „cate garzi isi iau dovada din proza" si
„cate raporteaza verde pe zero randuri", ci si PE CE INSTRUMENT sta fiecare garda, si daca acel
instrument a fost CALIBRAT - inclusiv pe modul lui propriu de esec.

TREI FORME GRESITE ALE ACESTUI FISIER, toate din aceeasi familie: instrumentul se lega de o FORMA DE
SUPRAFATA in loc de fapt. Le scriu fiindca sunt chiar clasa pe care faza 4 o numara.

  1. CALIBRAREA cautata dupa CUVANTUL „calibrare" in docstring -> `graf_temei` aparea cu ZERO, desi
     are patru afirmatii pozitive si una negativa din 01.08. Instrumentul care numara garzi ce-si iau
     dovada din proza isi lua dovada din proza.
  2. LEGATURA garda<->instrument cautata prin numele fisierului (`core/test_<modul>.py`) ->
     `scan_ancore` aparea „fara test propriu", desi garda lui exista din 21.08 si se numeste
     `core/test_ancore_in_cod.py`. O conventie de nume luata drept fapt.
  3. „TESTUL ATINGE instrumentul" cautat prin pomenirea numelui de modul in corpul functiei ->
     `graf_temei` aparea cu 0 teste, fiindca testele lui importa numele DIRECT
     (`from core.graf_temei import depinde_de`) si apoi cheama `depinde_de(...)`, fara prefix.

FORMA DE ACUM, structurala pe AST:
  - un fisier de test e legat de un instrument daca IMPORTA din el, in orice forma (inclusiv
    `importlib` pe cale, cum face `test_vigoare_punct`);
  - se aduna NUMELE aduse de acel import (aliasul de modul si numele importate direct);
  - o functie de test ATINGE instrumentul daca refera vreunul dintre acele nume;
  - o functie CALIBREAZA daca atinge instrumentul si are cel putin o aserttiune al carei capat
    asteptat e un LITERAL concret - aia pineaza un CAZ. `assert rez` e o proprietate, nu o calibrare.
    Negativa = aceleasi forme sub `not` / `not in`: cazul care NU trebuie gasit.

Axa VIDULUI (interdictia 19) NU se masoara aici: DELEAGA la `core/scan_garzi.py`, care exista din
22.08 si e mai bine fundamentat. Vezi `garzi_vacuabile`.
"""
import ast
import pathlib
import re

RAD = pathlib.Path(__file__).resolve().parents[1]
RAD_REPO = str(RAD)


def e_instrument(p):
    """Criteriu DECLARAT, ca sa se poata contrazice."""
    n = p.name
    return (n.startswith(("scan_", "sonda_", "audit_", "vigoare_"))
            or n in {"graf_temei.py", "agenda.py", "agenda_drift.py", "verificator_conformitate.py"})


def instrumente():
    out = [p for p in sorted(RAD.glob("core/*.py")) if e_instrument(p)]
    out += [p for p in sorted(RAD.glob("scripts/*.py")) if e_instrument(p)]
    return out


def nume_aduse(cale_test, modul):
    """Numele prin care testul poate ajunge la instrument: alias de modul + nume importate direct.

    set() gol daca fisierul nu-l importa deloc. Prinde si incarcarea prin `importlib` pe o cale care
    contine numele modulului - forma folosita pentru instrumentele din `scripts/`."""
    try:
        src = cale_test.read_text(encoding="utf-8", errors="replace")
        arb = ast.parse(src)
    except (OSError, SyntaxError):
        return set()
    nume = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.ImportFrom):
            if n.module in ("core", "core.%s" % modul, modul):
                for a in n.names:
                    if n.module == "core" and a.name != modul:
                        continue
                    nume.add(a.asname or a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                if a.name in ("core.%s" % modul, modul):
                    nume.add(a.asname or a.name.split(".")[-1])
    if not nume and re.search(re.escape(modul) + r"\.py", src):
        for n in ast.walk(arb):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                if getattr(n.value.func, "attr", "") == "module_from_spec":
                    for tg in n.targets:
                        if isinstance(tg, ast.Name):
                            nume.add(tg.id)
    return nume


def _literal(n):
    if isinstance(n, ast.Constant):
        return isinstance(n.value, (str, int, float))
    if isinstance(n, (ast.Tuple, ast.List, ast.Set)):
        return bool(n.elts) and all(_literal(e) for e in n.elts)
    return False


def _clasifica(test):
    """(pozitive, negative) - aserttiuni care pineaza un caz concret."""
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
                if any(_literal(c) for c in [sub.left] + list(sub.comparators)):
                    gasit = True
                    if any(isinstance(o, ast.NotIn) for o in sub.ops):
                        negat = True
        if gasit:
            if negat:
                neg += 1
            else:
                poz += 1
    return poz, neg


def _atinge(fn, nume):
    for n in ast.walk(fn):
        if isinstance(n, ast.Name) and n.id in nume:
            return True
        if isinstance(n, ast.Attribute) and getattr(n.value, "id", None) in nume:
            return True
    return False


def garzile_unui_instrument(modul):
    """[(cale_test, nume_aduse)] - fisierele care IMPORTA instrumentul, in orice forma."""
    out = []
    for t in sorted(RAD.glob("core/test_*.py")):
        nume = nume_aduse(t, modul)
        if nume:
            out.append((t, nume))
    return out


def instrumente_si_calibrare():
    """[(nume, fisiere, teste_care_ating, calib_poz, calib_neg)]"""
    out = []
    for inst in instrumente():
        modul = inst.stem
        fisiere, nt, poz, neg = [], 0, 0, 0
        for cale, nume in garzile_unui_instrument(modul):
            try:
                arb = ast.parse(cale.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            atins = False
            for fn in ast.walk(arb):
                if not (isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and fn.name.startswith("test_")):
                    continue
                if not _atinge(fn, nume):
                    continue
                atins = True
                nt += 1
                p, ng = _clasifica(fn)
                poz += p
                neg += ng
            if atins:
                fisiere.append(cale.name)
        out.append((inst.name, fisiere, nt, poz, neg))
    return out


def garzi_vacuabile():
    """DELEGA la core.scan_garzi.fara_existenta - NU reimplementeaza.

    Prima forma avea propria masuratoare (255 din 2.131). Instrumentul pentru interdictia 19 EXISTA
    din 22.08 si da 175 din 730 CARE CULEG - mai bine fundamentat: restrange la testele care isi
    culeg subiectul, si tine cont de un control pozitiv in acelasi modul. Doua instrumente pentru
    aceeasi clasa = logica paralela. Retras.

    ORBIREA COMUNA, declarata: niciunul nu prinde o garda care se apara cu `return` devreme - exact
    cele doua teste de secventa din R18. Instrumentul interdictiei 19 nu prinde cea mai ascutita
    instanta a interdictiei 19 pe care o avem.
    """
    import sys
    if RAD_REPO not in sys.path:
        sys.path.insert(0, RAD_REPO)
    from core import scan_garzi as _sg
    garzi = _sg.fisiere_garda(RAD_REPO)
    return _sg.fara_existenta(RAD_REPO, garzi)


if __name__ == "__main__":
    print("%-30s %6s %6s %6s %6s  %s"
          % ("instrument", "fisiere", "teste", "calib+", "calib-", "unde"))
    for _n, _fis, _nt, _poz, _neg in instrumente_si_calibrare():
        print("%-30s %6d %6d %6d %6d  %s"
              % (_n, len(_fis), _nt, _poz, _neg, ", ".join(f.replace("test_", "") for f in _fis[:3])))
    _rele, _tot, _culeg, _ctrl = garzi_vacuabile()
    print("")
    print("garzi cu asertiuni: %d | care CULEG: %d | vid posibil: %d | control pozitiv: %d"
          % (_tot, _culeg, len(_rele), _ctrl))
