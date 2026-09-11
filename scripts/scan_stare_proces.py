# -*- coding: utf-8 -*-
"""P6 — inventarul STARII care traieste in memoria procesului, intre cereri.

DEFINITIA CANONICA de la care porneste instrumentul (PLAN_HARDENING.md:696-722, citata, nu
rezumata): *«Nicio stare business autoritativa doar in memoria unui proces.»* Plus: *«Cache local
admis, dar numai DECLARAT»*, cu cinci lucruri scrise langa el — rol, sursa autoritativa, motiv,
invalidare, dovada de reconstructie identica.

Instrumentul NU porneste de la o lista de fisiere sau de familii. Porneste de la propozitia de mai
sus si o desface in trei intrebari mecanice:

  (1) CE e «memoria unui proces»?  -> numele legate la nivel de modul, in modulele pe care le
      incarca procesul web. Un nume local unei functii moare cu cererea; unul de modul nu.
  (2) CE inseamna «stare», adica se SCHIMBA?  -> exista cel putin un loc, in corpul unei functii,
      unde valoarea acelui nume se schimba dupa import. O constanta legata o data la import NU e
      stare — de-aia legarea din corpul modulului e exclusa explicit, si numarata.
  (3) CE e «business» / «autoritativa»?  -> NU e mecanic. Instrumentul se opreste aici si spune
      ca se opreste: el livreaza populatia MUTABILA, exhaustiv; impartirea business / cache /
      infrastructura e o citire de om, cu clichet, si se vede ca atare in raport.

UNITATILE (P6_*_DEFINITION), scrise inainte de a masura:

  P6_ENTRYPOINT_DEFINITION = un MODUL incarcat de procesul de productie: `main.py` plus inchiderea
      tranzitiva a importurilor lui, intersectata cu fisierele .py ale repo-ului. Nu «tot repo-ul»:
      un scanner sau un test are si el nume de modul, dar nu traieste in procesul care serveste
      cereri, deci nu poate purta stare intre doua cereri.
  P6_RAW_ITEM_DEFINITION = o pereche (modul, nume) legata la nivel de modul: `Assign`, `AnnAssign`,
      `AugAssign`, `FunctionDef`, `AsyncFunctionDef`, `ClassDef`, `Import`/`ImportFrom` — tot ce
      pune un nume in `__dict__`-ul modulului.
  P6_PATH_DEFINITION = un triplet (modul, nume, loc-de-mutatie): UN loc concret, cu linie, unde
      numele acela isi schimba valoarea DUPA import. Un nume cu >=1 astfel de loc e MUTABIL. Se
      numara caile, nu doar numele: doua locuri care scriu acelasi cache sunt doua cai.
  P6_EXCLUSION_DEFINITION = patru clase, fiecare cu motiv si fiecare NUMARATA (nu tacuta):
      E1 fisier in afara procesului (test, scanner, script) — nu traieste intre cereri;
      E2 mutatie doar in corpul modulului — e initializare la import, nu schimbare la rulare;
      E3 nume importat (`Import`/`ImportFrom`) — starea apartine modulului care il defineste, si
         e numarata acolo; altfel acelasi obiect s-ar numara de N ori;
      E4 nume legat, dar niciodata schimbat — constanta; e raw item, nu cale.

CELE CINCI DETECTOARE, separate ca sa poata fi calibrate separat (METODA §22 — fiecare instrument
primeste mutatie pe PROPRIUL mod de esec, si in ambele directii):

  S1 REBIND     `global N` intr-o functie + atribuire la N acolo. Forma clasica a contorului.
  S2 CONTAINER  `N[k] = v`, `del N[k]`, sau `N.<mutator>(...)` cu mutator dintr-o lista inchisa.
                Obiectul ramane acelasi; continutul lui e starea.
  S3 ATTR       `N.attr = v` intr-o functie — starea sta pe un obiect de modul, nu intr-un dict.
  S4 MEMO       memoizare in proces: `@lru_cache`, `@cache`, `@cached_property`. E cache prin
                DEFINITIE, deci intra in «cache local admis, dar numai DECLARAT». Un instrument
                care nu-l vede rateaza exact clasa pe care textul canonic o numeste.
  S5 CLASSATTR  `Cls.attr = v` unde `Cls` e o clasa de modul — `__dict__`-ul clasei e tot memorie
                de proces, doar ca ascunsa sub un nume de tip.

CE NU VEDE, prin constructie (formele de orbire; fiecare e MASURATA, nu doar declarata — o limita
fara cifra nu se poate compara intre ture):

  O1 ALIAS        `d = _CACHE` urmat de `d[k] = v`. Numele mutat e local; legatura e prin obiect.
  O2 PRIN-APEL    `f(_CACHE)` unde `f` muteaza argumentul. Ar cere analiza inter-procedurala.
  O3 SETATTR      `setattr(sys.modules[__name__], ...)` sau scriere prin `globals()`.
  O4 INTERIOR     `_pool = ThreadPool()` — starea e in obiect, nu in numele nostru; nicio linie
                  din repo nu o scrie.
  O5 STRAIN       stare in biblioteci terte incarcate de proces (sesiuni `requests`, pool psycopg2).
"""
import ast
import collections
import io
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import perimetru  # noqa: E402

#: Radacina procesului de productie. E o singura valoare, si e scrisa o data: daca serviciul ar
#: porni alt modul, aici se schimba, nu in zece locuri.
RADACINA_PROCES = "main.py"

#: Metodele care schimba un container pe loc. Lista e INCHISA si scrisa explicit — una deschisa
#: (`orice apel de metoda pe un nume de modul`) ar numara `_RE.match(x)` drept mutatie.
MUTATORI = frozenset([
    "append", "extend", "insert", "remove", "pop", "clear", "sort", "reverse",
    "add", "discard", "update", "setdefault", "popitem", "appendleft", "extendleft",
    "rotate", "difference_update", "intersection_update", "symmetric_difference_update",
])

#: Decoratori care tin rezultate in memoria procesului. `cached_property` intra: tine pe instanta,
#: iar o instanta de modul traieste cat procesul.
MEMOIZATORI = frozenset(["lru_cache", "cache", "cached_property", "memoize"])

Cale = collections.namedtuple("Cale", "modul fisier nume clasa linie context dovada")


def _module_procesului():
    """Inchiderea tranzitiva a importurilor pornind din `main.py`, pe fisierele repo-ului.

    ANTI-VACUUM: daca inchiderea iese mai mica decat pragul, instrumentul NU raporteaza zero — se
    opreste. Un graf rupt (import care nu se rezolva la un fisier local) ar da un perimetru mic si
    un inventar curat, adica exact minciuna pe care o cauta garda.
    """
    fisiere = {c for c in perimetru._fisiere_py() if c.endswith(".py")}
    dupa_modul = {}
    for c in fisiere:
        m = perimetru._module_din_cale(c)
        if m:
            dupa_modul[m] = c

    seminte = [RADACINA_PROCES]
    vazute, coada = set(), list(seminte)
    while coada:
        cale = coada.pop()
        if cale in vazute or cale not in fisiere:
            continue
        vazute.add(cale)
        for m in perimetru.importurile(cale):
            c2 = dupa_modul.get(m)
            if c2 and c2 not in vazute:
                coada.append(c2)
    return sorted(vazute), dupa_modul


def _arbore(cale):
    try:
        return ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read(), filename=cale)
    except Exception:
        return None


def _nume_modul(arb):
    """Numele legate la nivel de modul, impartite dupa ORIGINE.

    Distinctia importat / propriu nu e cosmetica: e exclusia E3. Fara ea, `from core import db`
    repetat in 40 de module ar da 40 de «stari», toate acelasi obiect.
    """
    proprii, importate = {}, set()
    for nod in arb.body:
        if isinstance(nod, ast.Assign):
            for t in nod.targets:
                for n in _tinte(t):
                    proprii.setdefault(n, nod.lineno)
        elif isinstance(nod, (ast.AnnAssign, ast.AugAssign)):
            for n in _tinte(nod.target):
                proprii.setdefault(n, nod.lineno)
        elif isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            proprii.setdefault(nod.name, nod.lineno)
        elif isinstance(nod, (ast.Import, ast.ImportFrom)):
            for a in nod.names:
                importate.add((a.asname or a.name).split(".")[0])
        elif isinstance(nod, (ast.If, ast.Try, ast.With)):
            # `try: import X except ImportError: X = None` si `if TYPE_CHECKING:` — nume reale.
            #: `_fara_functii`, nu `ast.walk`: altfel localele unei functii definite intr-un
            #: `try:` de modul ar intra in numele modulului. Calibrarea a prins forma vecina
            #: (`d112::obligatii`) si ea vine din aceeasi radacina — coborarea oarba prin AST.
            for sub in _fara_functii(nod):
                if isinstance(sub, ast.Assign):
                    for t in sub.targets:
                        for n in _tinte(t):
                            proprii.setdefault(n, sub.lineno)
                elif isinstance(sub, (ast.Import, ast.ImportFrom)):
                    for a in sub.names:
                        importate.add((a.asname or a.name).split(".")[0])
    return proprii, importate


def _fara_functii(nod):
    """Nodurile din corpul lui `nod`, FARA a cobori in functiile si clasele imbricate.

    [calibrare, directia a doua] `ast.walk` coboara oriunde, si asta a produs un fals pozitiv
    exact de forma pe care P6 o cauta: `core/d112.py::obligatii` e si nume de modul (o functie,
    l.913) si local al lui `_d112_genereaza` (l.606). Nepotul `add_oblig` scrie `obligatii.append`,
    adica LOCALUL bunicului — nu numele de modul. Un instrument care nu cunoaste domeniile
    intermediare raporteaza stare de proces acolo unde nu e.
    """
    for sub in ast.iter_child_nodes(nod):
        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        yield sub
        for x in _fara_functii(sub):
            yield x


def _legate_direct(fn):
    """Numele legate CHIAR in corpul functiei (nu in cele imbricate): atribuiri, parametri, `for`,
    `with ... as`, `except ... as`, import local."""
    legate = set()
    for nod in _fara_functii(fn):
        if isinstance(nod, ast.Name) and isinstance(nod.ctx, ast.Store):
            legate.add(nod.id)
        elif isinstance(nod, (ast.Import, ast.ImportFrom)):
            for a in nod.names:
                legate.add((a.asname or a.name).split(".")[0])
        elif isinstance(nod, ast.ExceptHandler) and nod.name:
            legate.add(nod.name)
    if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for a in list(fn.args.args) + list(fn.args.kwonlyargs) + list(fn.args.posonlyargs):
            legate.add(a.arg)
        if fn.args.vararg:
            legate.add(fn.args.vararg.arg)
        if fn.args.kwarg:
            legate.add(fn.args.kwarg.arg)
    return legate


def _tinte(t):
    if isinstance(t, ast.Name):
        return [t.id]
    if isinstance(t, (ast.Tuple, ast.List)):
        out = []
        for e in t.elts:
            out += _tinte(e)
        return out
    return []


def _clase_modul(arb):
    return {n.name for n in arb.body if isinstance(n, ast.ClassDef)}


def _functii(arb):
    """Fiecare functie/metoda din modul, cu numele ei calificat SI cu numele legate in domeniile
    care o inconjoara. Doar ce e INAUNTRUL lor conteaza: corpul modulului ruleaza o data, la
    import (exclusia E2).

    `umbrite` poarta inchiderea lexicala. Fara ea, o functie imbricata pare ca atinge modulul ori
    de cate ori bunicul ei are un local cu acelasi nume."""
    out = []

    def coboara(nod, prefix, umbrite):
        for sub in nod.body:
            if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nume = (prefix + "." + sub.name) if prefix else sub.name
                out.append((nume, sub, frozenset(umbrite)))
                coboara(sub, nume, umbrite | _legate_direct(sub))
            elif isinstance(sub, ast.ClassDef):
                coboara(sub, (prefix + "." + sub.name) if prefix else sub.name, umbrite)
    coboara(arb, "", frozenset())
    return out


def _cai_din_functie(modul, cale, nume_fn, fn, umbrite, proprii, importate, clase):
    """Locurile, in corpul unei functii, unde un nume de modul isi schimba valoarea.

    Se parcurge numai corpul PROPRIU (`_fara_functii`): fiecare functie imbricata e vizitata
    separat de `_functii`, iar o coborare oarba ar numara acelasi loc de doua ori — o cale
    dublata umfla clichetul fara sa existe.
    """
    gasit = []
    globale = set()
    for nod in _fara_functii(fn):
        if isinstance(nod, ast.Global):
            globale.update(nod.names)

    #: Numele legate local SAU intr-un domeniu inconjurator umbresc modulul. `global` bate
    #: umbrirea, de-aia e testat intai.
    locale = _legate_direct(fn) | umbrite

    def e_de_modul(n):
        return n in proprii and n not in importate and (n in globale or n not in locale)

    for nod in _fara_functii(fn):
        # S1 — rebind sub `global`
        if isinstance(nod, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            tinte = nod.targets if isinstance(nod, ast.Assign) else [nod.target]
            for t in tinte:
                for n in _tinte(t):
                    if n in globale and n in proprii and n not in importate:
                        gasit.append(Cale(modul, cale, n, "S1", nod.lineno, nume_fn,
                                          "global %s; %s = ..." % (n, n)))
                # S3/S5 — atribut pe un nume de modul
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                    n = t.value.id
                    if e_de_modul(n):
                        clasa = "S5" if n in clase else "S3"
                        gasit.append(Cale(modul, cale, n, clasa, nod.lineno, nume_fn,
                                          "%s.%s = ..." % (n, t.attr)))
        # S2 — subscript store / del
        if isinstance(nod, ast.Assign):
            for t in nod.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                    if e_de_modul(t.value.id):
                        gasit.append(Cale(modul, cale, t.value.id, "S2", nod.lineno, nume_fn,
                                          "%s[...] = ..." % t.value.id))
        if isinstance(nod, ast.Delete):
            for t in nod.targets:
                if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                    if e_de_modul(t.value.id):
                        gasit.append(Cale(modul, cale, t.value.id, "S2", nod.lineno, nume_fn,
                                          "del %s[...]" % t.value.id))
        # S2 — metoda mutatoare
        if isinstance(nod, ast.Call) and isinstance(nod.func, ast.Attribute):
            f = nod.func
            if isinstance(f.value, ast.Name) and f.attr in MUTATORI and e_de_modul(f.value.id):
                gasit.append(Cale(modul, cale, f.value.id, "S2", nod.lineno, nume_fn,
                                  "%s.%s(...)" % (f.value.id, f.attr)))
    return gasit


def _memo(modul, cale, arb):
    """S4 — memoizare in proces. Se cauta decoratorul, oriunde e definita functia (si pe metode:
    `@lru_cache` pe o metoda a unei clase de modul tine la fel de mult)."""
    gasit = []

    def nume_dec(d):
        t = d.func if isinstance(d, ast.Call) else d
        if isinstance(t, ast.Attribute):
            return t.attr
        if isinstance(t, ast.Name):
            return t.id
        return None

    for nod in ast.walk(arb):
        if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in nod.decorator_list:
                if nume_dec(d) in MEMOIZATORI:
                    gasit.append(Cale(modul, cale, nod.name, "S4", nod.lineno, nod.name,
                                      "@%s" % nume_dec(d)))
    return gasit


def _orbire(modul, cale, arb, proprii, importate):
    """Masoara O1 si O2 — cate locuri ar putea ascunde o mutatie pe care detectorul n-o vede.

    Nu e o lista de defecte: e marimea petei oarbe. O limita fara cifra nu se poate compara intre
    doua ture, si se citeste ca «mica»."""
    alias, prin_apel = [], []
    for nume_fn, fn, _umbrite in _functii(arb):
        locale_din_modul = {}
        for nod in _fara_functii(fn):
            # O1: `x = NUME_DE_MODUL` — alias pe un obiect de modul
            if isinstance(nod, ast.Assign) and isinstance(nod.value, ast.Name):
                n = nod.value.id
                if n in proprii and n not in importate:
                    for t in nod.targets:
                        for loc in _tinte(t):
                            locale_din_modul[loc] = n
                            alias.append((cale, nume_fn, nod.lineno, loc, n))
            # O2: `f(NUME_DE_MODUL)` — obiectul pleaca din modul
            if isinstance(nod, ast.Call):
                for a in nod.args:
                    if isinstance(a, ast.Name) and a.id in proprii and a.id not in importate:
                        prin_apel.append((cale, nume_fn, nod.lineno, a.id))
    return alias, prin_apel


def analizeaza_sursa(sursa, modul="sintetic", cale="sintetic.py"):
    """Caile dintr-o BUCATA de sursa, nu dintr-un fisier. Exista pentru calibrare.

    Fara ea, singura cale de a proba detectorul ar fi corpusul real — iar corpusul nu contine
    exemple din clasele S3/S4/S5, deci un zero de la ele n-ar putea fi deosebit de orbire.
    """
    arb = ast.parse(sursa)
    proprii, importate = _nume_modul(arb)
    clase = _clase_modul(arb)
    cai = []
    for nume_fn, fn, umbrite in _functii(arb):
        cai += _cai_din_functie(modul, cale, nume_fn, fn, umbrite, proprii, importate, clase)
    cai += _memo(modul, cale, arb)
    return cai


def inventar():
    fisiere, _ = _module_procesului()
    if len(fisiere) < 20:
        raise SystemExit("[scan_stare_proces] ANTI-VACUUM: inchiderea din %s are %d fisiere; "
                         "graful de import e rupt, iar un inventar gol ar fi o minciuna"
                         % (RADACINA_PROCES, len(fisiere)))

    raw, cai, excluse = [], [], collections.Counter()
    alias_tot, apel_tot = [], []
    for cale in fisiere:
        arb = _arbore(cale)
        if arb is None:
            excluse["E0_nesintactic"] += 1
            continue
        modul = perimetru._module_din_cale(cale)
        proprii, importate = _nume_modul(arb)
        clase = _clase_modul(arb)
        excluse["E3_nume_importat"] += len(importate)
        for n, ln in proprii.items():
            raw.append((modul, cale, n, ln))
        for nume_fn, fn, umbrite in _functii(arb):
            cai += _cai_din_functie(modul, cale, nume_fn, fn, umbrite, proprii, importate, clase)
        cai += _memo(modul, cale, arb)
        a, p = _orbire(modul, cale, arb, proprii, importate)
        alias_tot += a
        apel_tot += p

    nume_mutabile = {(c.modul, c.nume) for c in cai}
    excluse["E4_legat_dar_neschimbat"] = len({(m, n) for m, _, n, _ in raw}) - len(nume_mutabile)
    return {
        "fisiere_in_proces": fisiere,
        "raw": raw,
        "cai": cai,
        "nume_mutabile": sorted(nume_mutabile),
        "excluse": dict(excluse),
        "orbire_alias": alias_tot,
        "orbire_prin_apel": apel_tot,
    }


def main(argv):
    inv = inventar()
    pe_clasa = collections.Counter(c.clasa for c in inv["cai"])
    if "--json" in argv:
        print(json.dumps({
            "fisiere": len(inv["fisiere_in_proces"]),
            "raw": len({(m, n) for m, _, n, _ in inv["raw"]}),
            "nume_mutabile": ["%s::%s" % (m, n) for m, n in inv["nume_mutabile"]],
            "cai": [c._asdict() for c in inv["cai"]],
            "excluse": inv["excluse"],
            "orbire": {"alias": len(inv["orbire_alias"]),
                       "prin_apel": len(inv["orbire_prin_apel"])},
        }, ensure_ascii=False, indent=1))
        return 0

    print("PERIMETRU (P6_ENTRYPOINT_DEFINITION: %s + inchiderea importurilor)" % RADACINA_PROCES)
    print("  fisiere in procesul de productie : %d" % len(inv["fisiere_in_proces"]))
    print("  nume legate la nivel de modul    : %d  (P6_RAW_ITEM)"
          % len({(m, n) for m, _, n, _ in inv["raw"]}))
    print()
    print("CAI DE MUTATIE (P6_PATH: modul::nume @ linie)")
    for cl in sorted(pe_clasa):
        print("  %-4s %4d" % (cl, pe_clasa[cl]))
    print("  %-4s %4d  TOTAL cai" % ("", len(inv["cai"])))
    print("  nume distincte mutabile la rulare: %d" % len(inv["nume_mutabile"]))
    print()
    print("EXCLUSE, numarate (P6_EXCLUSION_DEFINITION)")
    for k in sorted(inv["excluse"]):
        print("  %-28s %d" % (k, inv["excluse"][k]))
    print()
    print("PATA OARBA, masurata")
    print("  O1 alias    (x = NUME_MODUL)  : %d locuri" % len(inv["orbire_alias"]))
    print("  O2 prin apel (f(NUME_MODUL))  : %d locuri" % len(inv["orbire_prin_apel"]))
    print()
    print("NUME MUTABILE, cu caile lor")
    dupa_nume = collections.defaultdict(list)
    for c in inv["cai"]:
        dupa_nume[(c.modul, c.nume)].append(c)
    for m, n in inv["nume_mutabile"]:
        cc = dupa_nume[(m, n)]
        clase = ",".join(sorted({x.clasa for x in cc}))
        print("  %-46s %-8s %d cai" % ("%s::%s" % (m, n), clase, len(cc)))
        for x in sorted(cc, key=lambda y: y.linie)[:6]:
            print("        %s:%d  %s  [%s]" % (x.fisier, x.linie, x.dovada, x.context))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
