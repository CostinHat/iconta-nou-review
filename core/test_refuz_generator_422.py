# -*- coding: utf-8 -*-
"""GARD (D6, 20.08.2026): un generator care REFUZĂ motivat nu are voie să ajungă la contabil ca 500 gol.

CLASA, nu cazul. `core/*.py` scriu refuzuri în limba contabilului și le ridică drept `ValueError`
(ex. `bilant_api.genereaza` l.107: „Nr. registrul comerțului lipsește — … Se completează la Date firmă").
`main.py` are un `@app.exception_handler(Exception)` care tratează special DOAR `PERIOADA_BLOCATA`;
orice alt `ValueError` necaptat devine **500 „Internal Server Error"** — oprire generică, interzisă de
DESIGN_SYSTEM (clasa „oprire tăcută/generică", 09.08.2026). Mesajul bun există și e aruncat de transport.

Găsit pe tenant_001 (F9): `POST /s1005-valideaza` și `GET /s1005-xml` → 500. Sweep-ul a scos încă două
(S1003), pe care interacțiunea nu le atinsese.

REGULA GARDATĂ, auto-întreținută (fără listă de rute scrisă de mână):
  pentru orice rută din `main.py` care cheamă `X.genereaza*(...)`, unde `X` e alias pentru un modul din
  `core/` a cărui funcție chemată conține `raise ValueError` → apelul TREBUIE să fie într-un
  `try` cu `except ValueError`.
Un generator NOU care refuză motivat intră automat sub gardă; unul care NU ridică `ValueError`
(ex. `api_public.genereaza`) rămâne în afara ei — deci gardul nu produce fals-pozitive (GĂRZI regula 3).

Mutație probată: `main.py` din backup-copie (fără cele 4 `except ValueError`) → gardul pică, numind rutele.
"""
import ast
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MAIN = os.path.join(_RAD, "main.py")
_DECORATORI = ("get", "post", "put", "delete", "patch")


def _e_ruta(fn):
    for d in fn.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Attribute) and f.attr in _DECORATORI \
                and isinstance(f.value, ast.Name) and f.value.id == "app":
            return True
    return False


def _aliasuri_core(fn, globale):
    """{alias: nume_modul} din importurile `from core import x as y`, locale funcției + globale."""
    ali = dict(globale)
    for n in ast.walk(fn):
        if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
            for a in n.names:
                ali[a.asname or a.name] = a.name
    return ali


def _ridica_valueerror(modul, functie):
    """True daca `core/<modul>.py::<functie>` contine un `raise ValueError` in corpul ei."""
    cale = os.path.join(_RAD, "core", modul + ".py")
    if not os.path.exists(cale):
        return False
    try:
        arb = ast.parse(open(cale, encoding="utf-8").read())
    except SyntaxError:
        return False
    for n in ast.walk(arb):
        if isinstance(n, ast.FunctionDef) and n.name == functie:
            for r in ast.walk(n):
                if isinstance(r, ast.Raise) and r.exc is not None:
                    e = r.exc.func if isinstance(r.exc, ast.Call) else r.exc
                    if isinstance(e, ast.Name) and e.id == "ValueError":
                        return True
    return False


def _prinde_valueerror(nod):
    """True daca `nod` (un ast.Try) are un handler pentru ValueError (simplu sau in tuplu)."""
    for h in nod.handlers:
        t = h.type
        if t is None:
            return True                                   # except: gol prinde tot
        tipuri = t.elts if isinstance(t, ast.Tuple) else [t]
        for x in tipuri:
            if isinstance(x, ast.Name) and x.id in ("ValueError", "Exception"):
                return True
    return False


def _neacoperite():
    src = open(_MAIN, encoding="utf-8").read()
    arb = ast.parse(src)
    globale = {}
    for n in arb.body:
        if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
            for a in n.names:
                globale[a.asname or a.name] = a.name

    gasite = []
    for fn in ast.walk(arb):
        if not isinstance(fn, ast.FunctionDef) or not _e_ruta(fn):
            continue
        ali = _aliasuri_core(fn, globale)
        # harta apel -> lista de Try care il contin
        for n in ast.walk(fn):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr.startswith("genereaza")
                    and isinstance(n.func.value, ast.Name)):
                continue
            modul = ali.get(n.func.value.id)
            if not modul or not _ridica_valueerror(modul, n.func.attr):
                continue
            acoperit = any(
                isinstance(t, ast.Try) and _prinde_valueerror(t)
                and t.lineno <= n.lineno <= (t.end_lineno or n.lineno)
                and any(n.lineno == c.lineno for b in t.body for c in ast.walk(b)
                        if isinstance(c, ast.Call))
                for t in ast.walk(fn))
            if not acoperit:
                gasite.append("%s (linia %d): %s.%s din core/%s.py ridica ValueError necaptat"
                              % (fn.name, n.lineno, n.func.value.id, n.func.attr, modul))
    return gasite


def test_generatoarele_care_refuza_nu_dau_500():
    rele = _neacoperite()
    assert not rele, (
        "Rute care lasa refuzul motivat al unui generator sa devina 500 gol "
        "(contabilul nu vede DE CE):\n  - " + "\n  - ".join(rele))


def test_gardul_chiar_gaseste_generatoarele_pazite():
    """Anti-gard-mort: daca euristica nu mai recunoaste NICIUN generator care ridica ValueError,
    testul de mai sus ar trece pe gol. Verifica pozitiv ca bilant_api.genereaza e vazut ca atare."""
    assert _ridica_valueerror("bilant_api", "genereaza"), \
        "bilant_api.genereaza nu mai e recunoscut ca generator care refuza -> gardul de mai sus e orb"
    assert _ridica_valueerror("bilant_api", "genereaza_s1003")
    assert not _ridica_valueerror("api_public", "genereaza"), \
        "api_public.genereaza nu ridica ValueError - daca apare aici, gardul face fals-pozitive"
