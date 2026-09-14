# -*- coding: utf-8 -*-
"""SQL-ul EFECTIV al unei funcții — cel scris în ea plus cel chemat din depozitul ei.

DE CE EXISTĂ (13.09.2026, valul D4 al lui P7). Până azi, întrebarea *„ce SQL execută funcția asta?"*
se răspundea citind literalele din corpul ei. Valul D4 a mutat **215 instrucțiuni** din 37 de module
în `core/repo_*.py`, iar toate instrumentele care puneau întrebarea au început, în aceeași clipă, să
răspundă **„niciunul"** — nu greșit, ci despre altă lume. Șase gărzi au căzut la prima rulare a
suitei, printre ele una care întreabă *«din câte locuri se naște o factură»* și una care verifică
*«rândul de audit nu mai produce orfani»*.

*Când o fază mută codul, instrumentele care îl citeau trebuie să se mute cu el — altfel măsoară
stratul greșit și o spun cu convingere.* Aceeași clasă cu `scan_trasee`, care a tăcut de două ori în
două valuri, și cu [[gard-care-nu-se-verifica-pe-sine]].

CONTRACTUL, îngust dinadins:
  · se urmărește **un singur pas**, și numai către DEPOZITUL NOMINAL al modulului
    (`core/X.py` → `core/repo_X.py`). Nu e o închidere tranzitivă: un modul nu capătă prin ea decât
    ce și-a dat singur;
  · SQL-ul se ia din **argumentul apelului**, ca nod, nu prin căutare de șiruri în fișier;
  · atribuirea e la funcția APELANTĂ. Întrebarea *„cine face X"* e despre aplicație, nu despre
    stratul în care a ajuns instrucțiunea.

CE NU FACE, declarat: nu urmărește apeluri prin variabile, nu rezolvă depozite chemate sub alt alias
decât `_repo`, și nu coboară în alte module. Ce nu poate rezolva, nu inventează.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: aliasul sub care valul D4 a legat fiecare modul de depozitul lui
ALIAS = "_repo"


def perechea(cale_rel):
    """`core/d406.py` → `core/repo_d406.py`, dacă există; altfel None."""
    baza = os.path.basename(cale_rel)
    if baza.startswith("repo_"):
        return None
    # 1. ALIASUL, citit din chiar modulul intrebat: `from core import repo_X as _repo`. E adevarul,
    #    fiindca valul use-case muta corpuri intre module si conventia de nume nu-i mai tine pasul.
    try:
        sursa = io.open(os.path.join(RAD, cale_rel), encoding="utf-8").read()
    except OSError:
        sursa = ""
    for n in ast.walk(ast.parse(sursa)) if sursa else ():
        if isinstance(n, ast.ImportFrom) and (n.module or "") == "core":
            for a in n.names:
                if (a.asname or a.name) == ALIAS:
                    pereche = "core/%s.py" % a.name
                    if os.path.exists(os.path.join(RAD, pereche)):
                        return pereche
    # 2. perechea NOMINALA, ca reper: depozitul unui modul din radacina (`main.py`) sta tot in `core/`.
    dosar = os.path.dirname(cale_rel) or "core"
    pereche = os.path.join(dosar, "repo_" + baza).replace(os.sep, "/")
    return pereche if os.path.exists(os.path.join(RAD, pereche)) else None


def _arbore(cale_rel):
    return ast.parse(io.open(os.path.join(RAD, cale_rel), encoding="utf-8").read())


def litera(nod):
    """Litera SQL a unui argument de `execute`, ca text. `{…}` rămâne `{}` — nu se inventează."""
    a = nod
    while isinstance(a, ast.BinOp):
        a = a.left
    if isinstance(a, ast.Constant) and isinstance(a.value, str):
        return a.value
    if isinstance(a, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "{}" for v in a.values)
    if isinstance(a, ast.Call):
        f = a.func
        if isinstance(f, ast.Attribute) and f.attr == "format" and a.args is not None:
            return litera(f.value)
    return ""


def _executii_directe(nod):
    return [litera(n.args[0]) for n in ast.walk(nod)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr in ("execute", "executemany") and n.args]


def _functii_depozit(cale_repo):
    """{nume: nod} pentru funcțiile depozitului."""
    return {f.name: f for f in ast.walk(_arbore(cale_repo))
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _apeluri_depozit(nod):
    """Numele funcțiilor de depozit chemate în `nod`, în ordinea apariției."""
    out = []
    for n in ast.walk(nod):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name) and n.func.value.id == ALIAS):
            out.append(n.func.attr)
    return out


def sql_din_nod(cale_rel, nod):
    """SQL-ul efectiv al unui nod din modulul `cale_rel`: direct + prin depozitul nominal."""
    out = list(_executii_directe(nod))
    repo = perechea(cale_rel)
    if repo:
        fn_repo = _functii_depozit(repo)
        for nume in _apeluri_depozit(nod):
            f = fn_repo.get(nume)
            if f is not None:
                out += _executii_directe(f)
    return out


def sql_functie(cale_rel, nume_functie):
    for f in ast.walk(_arbore(cale_rel)):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == nume_functie:
            return sql_din_nod(cale_rel, f)
    raise LookupError("%s n-are functia %s" % (cale_rel, nume_functie))


def sql_modul(cale_rel):
    return sql_din_nod(cale_rel, _arbore(cale_rel))


def executii_pe_functie(cale_rel):
    """[(nume_functie, sql)] — fiecare instrucțiune, atribuită funcției APELANTE."""
    arb = _arbore(cale_rel)
    repo = perechea(cale_rel)
    fn_repo = _functii_depozit(repo) if repo else {}
    linie_fn = {}
    for f in ast.walk(arb):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for ln in range(f.lineno, (f.end_lineno or f.lineno) + 1):
                linie_fn.setdefault(ln, f.name)
    out = []
    for n in ast.walk(arb):
        if not isinstance(n, ast.Call):
            continue
        gazda = linie_fn.get(n.lineno, "<modul>")
        if isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executemany") and n.args:
            out.append((gazda, litera(n.args[0])))
        elif (isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
                and n.func.value.id == ALIAS):
            f = fn_repo.get(n.func.attr)
            if f is not None:
                out += [(gazda, s) for s in _executii_directe(f)]
    return out


def straturi_aplicatie():
    """Fisierele stratului de aplicatie, in ordinea in care se cauta: HTTP intai, apoi use-case.

    Lista se DERIVA (`main.py` + `core/uc_*.py`), nu se scrie: un modul de use-case nou intra singur,
    iar o garda nu poate ramane in urma fiindca cineva a uitat s-o adauge intr-o lista.
    """
    cai = ["main.py"]
    dosar = os.path.join(RAD, "core")
    if os.path.isdir(dosar):
        cai += ["core/%s" % f for f in sorted(os.listdir(dosar))
                if f.startswith("uc_") and f.endswith(".py")]
    return [c for c in cai if os.path.exists(os.path.join(RAD, c))]


def _fara_docstring(f):
    return [s for s in f.body
            if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]


def _delegarea(st):
    """Apelul `_uc_x.f(…)` dintr-un `try` care traduce refuzul inapoi in `HTTPException`, sau None."""
    if not isinstance(st, ast.Try) or not st.body:
        return None
    traduce = any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name)
                  and x.func.id == "_http_din"
                  for h in st.handlers for x in ast.walk(h))
    if not traduce:
        return None
    for x in ast.walk(ast.Module(body=st.body, type_ignores=[])):
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) \
                and isinstance(x.func.value, ast.Name) and x.func.value.id.startswith("_uc"):
            return x
    return None


def e_inveli(f):
    """Functia e doar POARTA catre stratul use-case, nu munca.

    TREI forme, toate din valul use-case:
      · `return _http(fn, …)` — prima forma, cu apel indirect (abandonata: rupea graful de apeluri);
      · `try: return _uc_x.f(…) except EroareDeDomeniu as e: raise _http_din(e)` — forma obisnuita;
      · aceeasi delegare, dar cu **raspunsul construit deasupra ei** (`date = _uc_x.f(…)` urmat de
        `return Response(…)`) sau cu o **garda de protocol** inaintea lui `try` (rate-limit pe IP).
        Cele 27 de rute care nu pot pleca intregi arata asa.

    *Ce face dintr-o ruta un invelis e DELEGAREA, nu forma lui `return`.* Cerand prima forma,
    accesorul raspundea „nu e invelis" despre 17 rute si lasa proiectia cu corpul gol al portii.
    """
    corp = _fara_docstring(f)
    if len(corp) == 1 and isinstance(corp[0], ast.Return) \
            and isinstance(corp[0].value, ast.Call) \
            and isinstance(corp[0].value.func, ast.Name) and corp[0].value.func.id == "_http":
        return True
    return any(_delegarea(s) is not None for s in corp)


def _imbina(inveli, uc):
    """Corpul PROIECTAT: ce e deasupra delegarii, apoi munca, apoi ce urmeaza delegarii.

    Pentru invelisul obisnuit (`try: return _uc_x.f(…)`) iese exact corpul use-case-ului — forma de
    pana acum. Pentru cele 27 de rute care n-au plecat intregi, iese si protocolul ramas sus: garda
    de ritm de deasupra lui `try`, construirea raspunsului de dupa apel. *Proiectia nu poate arunca
    nici munca, nici protocolul: intrebarile puse pe ea sunt si despre una, si despre cealalta.*
    """
    out = []
    for s in _fara_docstring(inveli):
        ap = _delegarea(s)
        if ap is None:
            out.append(s)
            continue
        out.extend(uc.body)
        for x in s.body:
            # instructiunea care CHEAMA use-case-ul se inlocuieste cu corpul lui, nu se pastreaza
            if (isinstance(x, ast.Return) and x.value is ap) or \
                    (isinstance(x, ast.Assign) and x.value is ap):
                continue
            out.append(x)
    return out or list(uc.body)


def arbore_aplicatie():
    """Un modul SINTETIC cu toate definitiile stratului de aplicatie, in ordinea straturilor.

    Pentru garzile care intreaba *„exista undeva in aplicatie un X"*. NU se da garzilor care cer ca
    X sa fie intr-o anumita functie: acolo raspunsul trebuie sa ramana despre o functie.
    """
    corp, vazute = [], {}
    for cale in straturi_aplicatie():
        for n in _arbore(cale).body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if n.name in vazute:
                    i = vazute[n.name]
                    vechi = corp[i]
                    if isinstance(vechi, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                            and e_inveli(vechi) and not e_inveli(n):
                        # IMBINARE: antetul portii (nume, parametri, DECORATORI — contractul HTTP)
                        # cu corpul muncii (din use-case). Alegand doar una, proiectia ar raspunde
                        # bine la o intrebare si prost la cealalta.
                        corp[i] = ast.fix_missing_locations(type(vechi)(
                            name=vechi.name, args=vechi.args,
                            body=_imbina(vechi, n),
                            decorator_list=vechi.decorator_list,
                            returns=getattr(vechi, "returns", None),
                            type_comment=None, lineno=vechi.lineno,
                            col_offset=vechi.col_offset))
                    continue
                vazute[n.name] = len(corp)
            corp.append(n)
    return ast.Module(body=corp, type_ignores=[])


def sursa_aplicatie(separator="\n"):
    """Sursa stratului de aplicatie, cap la cap — pentru garzile care cauta un SIR."""
    return separator.join(io.open(os.path.join(RAD, c), encoding="utf-8").read()
                          for c in straturi_aplicatie())


#: unde se cauta o functie de aplicatie, in ordinea straturilor. `main.py` ramane primul: dupa valul
#: use-case el pastreaza INVELISUL cu acelasi nume, iar invelisul nu mai are corp — deci cine
#: intreaba „ce face functia X" trebuie sa coboare in stratul urmator.
STRATURI_FUNCTII = None   # derivat la apel de `straturi_aplicatie()`


def functia(nume, cai=None):
    """(cale, nod) pentru prima definitie a functiei `nume`, cu CORP, in ordinea straturilor.

    Un invelis (corp de o singura instructiune `return _http(...)`) nu se ia drept raspuns: el e
    poarta, nu munca. Daca nu se gaseste nicaieri, se ridica — o absenta tacuta ar fi raportata de
    apelant ca „functia nu face nimic".
    """
    for cale in (cai or straturi_aplicatie()):
        if not os.path.exists(os.path.join(RAD, cale)):
            continue
        for f in ast.walk(_arbore(cale)):
            if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == nume:
                if not e_inveli(f):
                    return cale, f
    raise LookupError("functia %s nu s-a gasit cu corp in stratul de aplicatie" % nume)


def ruta_http(nume, cale="main.py"):
    """Nodul rutei din stratul HTTP — cel care poarta DECORATORUL, chiar daca e invelis.

    Pentru intrebarile despre protocol (cale, metoda, dependente de rol). Ridica daca nu exista:
    o absenta tacuta s-ar citi ca „ruta nu mai e montata".
    """
    for f in ast.walk(_arbore(cale)):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name == nume:
            return f
    raise LookupError("ruta %s nu e montata in %s" % (nume, cale))


def cod_http(nume_clasa, cale="main.py"):
    """Codul in care stratul HTTP traduce o clasa din `core/erori.py`, citit din `_COD_EROARE`.

    Ridica daca clasa nu e in harta: o clasa netradusa ar iesi din aplicatie ca `500`, si tocmai
    asta trebuie sa se vada, nu sa se intoarca `None`.
    """
    for n in ast.walk(_arbore(cale)):
        if not (isinstance(n, ast.Assign) and len(n.targets) == 1
                and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "_COD_EROARE"):
            continue
        for el in getattr(n.value, "elts", ()):
            perechi = getattr(el, "elts", ())
            if len(perechi) == 2 and isinstance(perechi[0], ast.Attribute) \
                    and isinstance(perechi[1], ast.Constant):
                if perechi[0].attr == nume_clasa:
                    return perechi[1].value
    raise LookupError("clasa %s nu are traducere in harta HTTP din %s" % (nume_clasa, cale))


def sursa_functiei(nume):
    """Sursa functiei cu CORP, ca text — pentru garzile care cauta un sir in corpul unei rute."""
    cale, f = functia(nume)
    text = io.open(os.path.join(RAD, cale), encoding="utf-8").read()
    return ast.get_source_segment(text, f) or ""
