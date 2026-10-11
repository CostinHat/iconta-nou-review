# -*- coding: utf-8 -*-
"""scripts/amprente_suita.py — R2b: amprenta fiecărui apel de generator din suită (comanda Costin 08.10.2026, verbatim în DECIZII; pasul
R2b din TESTE.md: „Suita: amprenta fiecărui apel de generator din `pytest` (formularele completate de teste), pe test, artefact.”).

De ce în afara porții: e un plugin pytest încărcat NUMAI la cerere (`-p amprente_suita`); suita obișnuită nu-l vede, deci poarta nu
se schimbă cu nimic. Cu el, fiecare funcție care EMITE un document XML (antetul `<?xml` în corpul ei — `build_xml` al fiecărei declarații,
`bilant.xml_s1005`, e-Factura, SAGA, e-Transport, REGES) e învelită înaintea colectării: întoarce exact ce întorcea, iar amprenta ieșirii
(SHA-256 pe XML-ul fără părțile care se schimbă la fiecare generare — `cifre_referinta._VOLATIL`, aceeași normalizare ca R2a) se
consemnează pe testul care a chemat-o, în ordinea apelurilor. Lista se DERIVĂ din sursă la fiecare rulare (`emitatoare`): un generator nou
intră singur, unul care dispare iese — fără listă scrisă de mână.

Ce se compară (măsurat la R2b, două rulări pe același cod): VERDICTUL e pe mulțimea amprentelor DISTINCTE (emițător, SHA) — o ieșire
schimbată dă un SHA care n-a existat înainte, una dispărută lasă un SHA fără pereche. Lista PE TEST e informativă, nu verdict: apelurile
unui fixture de modul se consemnează pe primul test care îl cere (ordinea de rulare decide care), iar recalculările condiționate de
starea bazei (`firma_rezumat.recalculeaza_lot` sare firmele proaspete) cheamă sau nu generatorul după ce au lăsat testele dinainte.
R8 rulează ambele părți în aceeași zi (suita commitului R2b dintr-un arbore separat și suita HEAD): ce depinde de ziua curentă și n-a
fost normalizat se vede ca diferență, nu ca regresie ascunsă.

Uz:  ICONTA_AMPRENTE_SUITA=<iesire.json> PYTHONPATH=scripts ./venv/bin/python -m pytest -q -p amprente_suita [teste…]
     python scripts/amprente_suita.py --compara <a.json> <b.json>   -> 0 aceleași amprente distincte / 1 diferă (listele tipărite)
"""
import ast
import datetime as _dt
import functools
import glob
import importlib
import json
import os
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

from cifre_referinta import _amprenta  # noqa: E402

VAR = "ICONTA_AMPRENTE_SUITA"
#: citesc XML (cititorul bonurilor AMEF), nu emit un document — nu sunt generatoare
NU_EMIT = {("core.amef_import", "extrage_xml"), ("core.amef_import", "_test")}
FARA_TEST = "(în afara unui test)"
STARE = {"test": FARA_TEST, "apeluri": {}, "invelite": []}


def emitatoare(rad=RAD):
    """[(modul, funcție)] — funcțiile de nivel modul din `core/` (fără teste) al căror corp conține antetul `<?xml`, minus `NU_EMIT`."""
    out = []
    for f in sorted(glob.glob(os.path.join(rad, "core", "*.py"))):
        if os.path.basename(f).startswith("test_"):
            continue
        src = open(f, encoding="utf-8").read()
        if "<?xml" not in src:
            continue
        mod = "core." + os.path.basename(f)[:-3]
        for n in ast.parse(src).body:
            if isinstance(n, ast.FunctionDef) and "<?xml" in (ast.get_source_segment(src, n) or "") and (mod, n.name) not in NU_EMIT:
                out.append((mod, n.name))
    return out


def amprenta(rez):
    """Amprenta ieșirii unui emițător: textul XML normalizat; altceva decât text -> numele tipului (se vede la comparare)."""
    if isinstance(rez, bytes):
        rez = rez.decode("utf-8", errors="replace")
    if isinstance(rez, str):
        return _amprenta(rez)
    return "tip:" + type(rez).__name__


def inveleste(fn, nume):
    """Același rezultat, plus consemnarea amprentei pe testul curent. MUTAȚIE: amprenta consemnată fără normalizare -> pică garda."""
    @functools.wraps(fn)
    def w(*a, **k):
        rez = fn(*a, **k)
        STARE["apeluri"].setdefault(STARE["test"], []).append([nume, amprenta(rez)])
        return rez
    w.__amprente_suita__ = True
    return w


def activeaza(rad=RAD):
    """Învelește fiecare emițător pe modulul lui (înaintea colectării: testele care îl importă pe nume primesc învelișul)."""
    for mod, fn in emitatoare(rad):
        m = importlib.import_module(mod)
        f = getattr(m, fn)
        if not getattr(f, "__amprente_suita__", False):
            setattr(m, fn, inveleste(f, "%s.%s" % (mod, fn)))
            STARE["invelite"].append("%s.%s" % (mod, fn))
    return len(STARE["invelite"])


def compara(a, b):
    """[(test, înainte, după)] — fiecare test al cărui șir de amprente diferă, lipsește sau e nou (informativ, v. antetul)."""
    ta, tb = a.get("teste") or {}, b.get("teste") or {}
    return [(t, ta.get(t), tb.get(t)) for t in sorted(set(ta) | set(tb)) if ta.get(t) != tb.get(t)]


def distincte(d):
    """Mulțimea amprentelor (emițător, SHA) produse în rulare, oricare ar fi testul pe care s-au consemnat."""
    return {(x[0], x[1]) for v in (d.get("teste") or {}).values() for x in v}


def compara_distincte(a, b):
    """(numai înainte, numai după) — VERDICTUL: amândouă goale = aceleași ieșiri. MUTAȚIE: o parte ignorată -> pică garda."""
    da, db = distincte(a), distincte(b)
    return sorted(da - db), sorted(db - da)


# --- plugin pytest (activ numai cu -p amprente_suita ȘI variabila de mediu) ---------------------------------------------------------
def pytest_configure(config):
    if os.environ.get(VAR):
        n = activeaza()
        print("[amprente_suita] %d emițătoare învelite -> %s" % (n, os.environ[VAR]), flush=True)


def pytest_runtest_setup(item):
    STARE["test"] = item.nodeid


def pytest_runtest_teardown(item):
    STARE["test"] = FARA_TEST


def pytest_sessionfinish(session, exitstatus):
    cale = os.environ.get(VAR)
    if not cale:
        return
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    apeluri = STARE["apeluri"]
    json.dump({"commit": commit, "generat": _dt.datetime.now().isoformat(timespec="seconds"), "exit": int(exitstatus),
               "emitatoare": STARE["invelite"], "teste": apeluri,
               "n_teste": len(apeluri), "n_apeluri": sum(len(v) for v in apeluri.values())},
              open(cale, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print("\n[amprente_suita] %d teste, %d apeluri -> %s" % (len(apeluri), sum(len(v) for v in apeluri.values()), cale), flush=True)


def main(argv):
    if argv[:1] == ["--compara"] and len(argv) == 3:
        a, b = (json.load(open(f, encoding="utf-8")) for f in argv[1:3])
        dif = compara(a, b)
        for t, x, y in dif[:60]:
            print("  pe test (informativ) %s: %s -> %s" % (t, x, y))
        doar_a, doar_b = compara_distincte(a, b)
        for e, s in doar_a:
            print("  NUMAI ÎNAINTE %s %s" % (e, s))
        for e, s in doar_b:
            print("  NUMAI DUPĂ    %s %s" % (e, s))
        print("[amprente_suita] pe test: %d diferă; distincte: %d / %d -> %s" % (
            len(dif), len(distincte(a)), len(distincte(b)), "aceleași" if not (doar_a or doar_b) else "DIFERĂ"))
        return 1 if (doar_a or doar_b) else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
