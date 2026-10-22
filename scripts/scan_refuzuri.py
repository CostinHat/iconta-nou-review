# -*- coding: utf-8 -*-
"""scripts/scan_refuzuri.py — CE POARTA un refuz al aplicatiei, si ce nu poarta.

Cerut de Costin ca inventar al locurilor unde aplicatia refuza, inaintea normei de blocaj-cu-temei.

CE MASOARA, exact: fiecare `raise` din `main.py` si `core/` care OPRESTE un act, si **ce poarta
refuzul cu el** — temeiul, ca date sau ca proza, sau nimic.

DE CE NU E ACELASI LUCRU CU `core/scan_refuz_tacut.py`: acela intreaba daca refuzul **ajunge** la om
(are un `catch` care afiseaza ceva). Asta intreaba daca refuzul **spune pe ce se sprijina**. Un refuz
poate ajunge perfect la om si sa fie, tot asa, o afirmatie fara temei — «nu se poate», fara sa spuna
cine zice asta. Cele doua populatii se suprapun, dar niciuna n-o cuprinde pe cealalta.

CELE PATRU MODURI DE ESEC ALE ACESTUI INSTRUMENT, scrise INAINTE de prima masuratoare
(interdictia 76, si de data asta chiar inainte):

  1. **NU EXECUTA.** Un refuz construit de un ajutor (`_refuz(camp, temei)`) si ridicat in alta parte
     e numarat la locul lui `raise`, unde temeiul nu se vede. Deci clasa `FARA` e un **PLAFON
     SUPERIOR**: pot exista refuzuri care poarta temei printr-un drum pe care scanul nu-l urmeaza.
  2. **NU DEOSEBESTE NORMATIV DE FORMA.** Un 400 «lipseste campul` si un 400 «norma nu permite» sunt
     amandoua refuzuri, iar temeiul e cerut doar de al doilea. Scanul le numara la un loc si **spune
     asta**; nu incearca sa ghiceasca normativitatea din text, fiindca ar fi exact ancorarea pe
     cuvinte pe care clichetul 50 o interzice. Cifra `FARA` amesteca deci doua populatii.
  3. **VEDE DOAR PYTHON.** Refuzurile din ecran (validare in JS inainte de cerere) nu sunt aici.
     Alta populatie, alt instrument.
  4. **VEDE `raise` SI REFUZURILE ADUNATE, nu si corpurile intoarse.** O ruta care INTOARCE un corp
     de eroare fara sa ridice — `return {"eroare": ...}` — e invizibila. Numarate separat, ca sa se
     vada cat de mare e umbra.

REFUZUL ADUNAT (lotul 11, 22.10.2026, subagentul g2 — gard erodat gasit de W5 in campania 440). Campania
440 („toate erorile apar deodata”) a mutat zeci de refuzuri din `raise` in COLECTOARE: `core.erori.
ErorileFormularului` (`.camp(camp, mesaj)` / `.fara_camp(mesaj)`), liste ridicate la capat
(`motive.append(...)` + `raise RefuzuriSectiune(motive)` in d212, `_er.append(...)` + `raise
FacturaRefuzata(_er)`, `erori.append(...)` + `raise RefuzReevaluare(erori)`) si ajutorul
`uc_comun._campuri_lipsa`. Un scan care numara numai `raise` le pierdea: refuzul ramanea, temeiul nu-l
castigase, iar clichetul cobora (d212 38 -> 11, facturi_api 27 -> 18, stocuri 9 -> 6, reevaluare_valuta
4 -> 0). De atunci, **unitatea e LOCUL UNDE SE SCRIE MOTIVUL refuzului**, oricum pleaca el: un `raise`,
o adaugare intr-un colector, un apel al ajutorului. Aceeasi regula de temei (`_poarta_temei_structurat`,
apoi `_SEMNE_ACT`), pe nodul adaugarii. Ridicarea care doar duce lista (`raise X(lista)`) NU se mai
numara: motivele ei sunt numarate unde se scriu, iar a o numara si pe ea ar dubla.

  5. **REFUZUL ADUNAT se urmareste STRUCTURAL, in modul, nu peste module.** O lista e „de refuz” daca
     ajunge intreaga intr-un `raise X(lista)`, intr-o bucla care o varsa intr-un colector, intr-un
     ajutor din acelasi modul a carui lista-parametru e de refuz, sau e intoarsa unui apelant care o
     ridica (propagare pana la punct fix). O lista primita dintr-un ALT modul si ridicata aici nu se
     urmareste pana la sursa ei: motivele ei se numara acolo numai daca sursa le ridica / le aduna
     ea insasi. O adaugare care doar RETRANSMITE (textul unei exceptii prinse, `str(e)`; elementele
     altei liste de refuz; parametrii unui RELEU — o functie care varsa parametrii ei intr-un colector,
     ca `_ErorileNotei.adauga`) nu e un refuz nou: se numara la sursa, iar pentru releu la fiecare
     apel al lui din modul.

CE NU MASOARA, declarat: daca temeiul e CORECT. Doar daca exista si sub ce forma.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Clasele de refuz, dupa CE OPRESTE refuzul. Nomenclator INCHIS.
CLASE = ("acces", "negasit", "refuz")

#: Cum poarta refuzul temeiul. Ordinea e de la tare la slab; un refuz primeste prima care se potriveste.
PURTATOR = ("structurat", "proza", "fara")

#: 401/403 = cine esti, nu ce ai cerut. Un temei legal n-ar avea ce cauta acolo — refuzul nu se
#: sprijina pe o norma fiscala, ci pe faptul ca nu ai acces. Declarate in afara clasei masurate.
_ACCES = (401, 403)
#: 404 e AMESTECAT prin constructie: si «tenant inexistent», si «fel necunoscut» (nomenclator inchis).
#: Se numara separat tocmai ca sa nu se topeasca in niciuna dintre celelalte doua.
_NEGASIT = (404,)

#: Semne ca proza refuzului trimite la un act. Lista supraevalueaza deliberat (prinde si `art.` dintr-un
#: `articol` de stoc), deci `proza` e plafon SUPERIOR si `fara` plafon INFERIOR. Directia se scrie.
_SEMNE_ACT = ("art.", "art ", "alin", "pct.", "OMFP", "OPANAF", "HG ", "Legea", "Cod fiscal",
              "Codul fiscal", "norma", "normele", "L227", "227/2015", "82/1991")


def _fisiere():
    out = [os.path.join(RAD, "main.py")]
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if f.endswith(".py") and not f.startswith(("test_", "scan_")):
            out.append(os.path.join(RAD, "core", f))
    return out


def _siruri(nod):
    """Toate sirurile literale din subarborele unui nod."""
    return [n.value for n in ast.walk(nod)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _poarta_temei_structurat(nod):
    """Temeiul ca DATE: un `temei=` cu nume, o cheie `"temei"` intr-un dict, un `Temei(...)`, sau un
    nume care incepe cu TEMEI. Se decide pe STRUCTURA, nu pe text."""
    for n in ast.walk(nod):
        if isinstance(n, ast.keyword) and n.arg == "temei":
            return True
        if isinstance(n, ast.Constant) and n.value == "temei":
            return True
        if isinstance(n, ast.Name) and (n.id == "Temei" or n.id.startswith("TEMEI")):
            return True
        if isinstance(n, ast.Attribute) and (n.attr == "temei" or n.attr.startswith("TEMEI")):
            return True
    return False


def _vocabular():
    """{nume_clasa: cod HTTP} — vocabularul de refuz al stratului use-case, CITIT, nu rescris.

    [P7 · valul use-case] Cele 599 de `HTTPException` din corpurile rutelor au devenit
    `_erori.<Clasa>`, iar codul se pune la loc in stratul HTTP. Fara ele in nomenclator, inventarul
    a scazut de la peste 800 la 635 — o curatenie care nu s-a intamplat. Se citeste din
    `core/erori.py` si din harta `main._COD_EROARE`, ca o clasa noua sa intre in aceeasi zi.
    """
    if not hasattr(_vocabular, "_h"):
        import importlib
        import sys as _sys
        if RAD not in _sys.path:
            _sys.path.insert(0, RAD)
        try:
            erori = importlib.import_module("core.erori")
            harta = {c.__name__: None for c in erori.TOATE}
            try:
                m = importlib.import_module("main")
                harta.update({c.__name__: cod for c, cod in m._COD_EROARE})
            except Exception:
                pass
        except Exception:
            harta = {}
        _vocabular._h = harta
    return _vocabular._h


def _clasa_si_stare(nod):
    """(clasa, stare_http|None) pentru un `raise`. `None` daca nu e un refuz."""
    exc = nod.exc
    if exc is None:
        return None, None
    tinta = exc.func if isinstance(exc, ast.Call) else exc
    nume = tinta.id if isinstance(tinta, ast.Name) else getattr(tinta, "attr", None)
    voc = _vocabular()
    if nume in voc:
        stare = voc[nume]
        if stare in _ACCES:
            return "acces", stare
        if stare in _NEGASIT:
            return "negasit", stare
        return "refuz", stare
    if nume == "HTTPException":
        stare = None
        if isinstance(exc, ast.Call) and exc.args and isinstance(exc.args[0], ast.Constant):
            stare = exc.args[0].value
        if stare in _ACCES:
            return "acces", stare
        if stare in _NEGASIT:
            return "negasit", stare
        return "refuz", stare
    # exceptiile aplicatiei: orice nume care se termina in una din formele de refuz, plus ValueError
    if nume and (nume.endswith(("Incompleta", "IncompletaPF", "Neconstruibil", "Neconfirmata",
                                "Invalid", "Invalida", "Ratata", "Refuzat"))
                 or nume == "ValueError"):
        return "refuz", None
    return None, None


#: Metodele colectorului unic al formularelor (`core.erori.ErorileFormularului`) care ADAUGA un refuz. Citite pe structura in
#: `core/test_refuzuri.py` (o metoda noua de adaugare a colectorului, nenumita aici, pica garda), nu presupuse.
METODE_COLECTOR = ("camp", "fara_camp")
#: Ajutoarele de refuz adunat chemate din ALTE module: un apel = un refuz al apelantului (lista campurilor obligatorii e a lui,
#: textul e generic, in ajutor). Corpul ajutorului nu se numara (altfel s-ar numara o data in plus, in modulul ajutorului).
AJUTOARE_ADUNATE = ("_campuri_lipsa",)
#: Cum se adauga intr-o lista de refuz.
_ADAUGARI_LISTA = ("append", "extend", "insert")

_FN = (ast.FunctionDef, ast.AsyncFunctionDef)


def _noduri_proprii(fn):
    """Nodurile corpului lui `fn`, fara cele ale functiilor imbricate (au analiza lor)."""
    out, stiva = [], list(ast.iter_child_nodes(fn))
    while stiva:
        n = stiva.pop()
        out.append(n)
        if not isinstance(n, _FN + (ast.ClassDef,)):
            stiva.extend(ast.iter_child_nodes(n))
    return out


def _parametri(fn):
    a = fn.args
    return [p.arg for p in (a.posonlyargs + a.args + a.kwonlyargs)]


def _nume(nod):
    return {n.id for n in ast.walk(nod) if isinstance(n, ast.Name)}


def _e_lista_noua(v):
    return (isinstance(v, (ast.List, ast.ListComp))
            or (isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "list"))


def _tinta_apelului(c):
    f = c.func
    return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)


def _adaugare_in_lista(n, R):
    """(lista, [argumentele adaugate]) daca `n` adauga intr-o lista de refuz din `R`; altfel None."""
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in _ADAUGARI_LISTA
            and isinstance(n.func.value, ast.Name) and n.func.value.id in R and n.args):
        return n.func.value.id, [n.args[-1]]
    if (isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add) and isinstance(n.target, ast.Name)
            and n.target.id in R):
        return n.target.id, [n.value]
    return None


def _apel_colector(n):
    return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in METODE_COLECTOR
            and len(n.args) + len(n.keywords) in ((1,) if n.func.attr == "fara_camp" else (2,)))


def _liste_de_refuz(arb):
    """{id(fn): set(nume)} — listele de refuz ale fiecarei functii a modulului, propagate pana la punct fix (modul de esec 5)."""
    fns = [f for f in ast.walk(arb) if isinstance(f, _FN)]
    pe_nume = {}
    for f in fns:
        pe_nume.setdefault(f.name, []).append(f)
    proprii = {id(f): _noduri_proprii(f) for f in fns}
    ref = {id(f): set() for f in fns}
    create, liste = {}, {}
    for f in fns:
        # `create` = numele legate de o lista NOUA in functie (`[]`, `list(...)`, o lista in comprehensiune): numai ele pot porni o
        # lista de refuz (S1, S5) — un `raise ValueError(motiv)` cu `motiv` un text intors de un ajutor nu e o lista
        c = set()
        for n in proprii[id(f)]:
            if isinstance(n, ast.Assign) and _e_lista_noua(n.value):
                c |= {t.id for t in n.targets if isinstance(t, ast.Name)}
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Tuple):
                for t in n.targets:
                    if isinstance(t, ast.Tuple):
                        c |= {e.id for e, v in zip(t.elts, n.value.elts) if isinstance(e, ast.Name) and _e_lista_noua(v)}
        # `liste` = in plus parametrii si rezultatele apelurilor: pot DUCE o lista de refuz pornita in alta parte (S2, S3, S4)
        s = c | set(_parametri(f))
        for n in proprii[id(f)]:
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                for t in n.targets:   # rezultatul unui apel: lista intoarsa de un ajutor
                    s |= {e.id for e in ([t] if isinstance(t, ast.Name) else getattr(t, "elts", [])) if isinstance(e, ast.Name)}
        create[id(f)], liste[id(f)] = c, s

    def _poz_param(g, i, kw):
        p = _parametri(g)
        if kw is not None:
            return kw if kw in p else None
        p = p[1:] if (p and p[0] in ("self", "cls")) else p
        return p[i] if i < len(p) else None

    schimbat = True
    while schimbat:
        schimbat = False

        def _pune(fid, nume):
            nonlocal schimbat
            if nume and nume not in ref[fid]:
                ref[fid].add(nume)
                schimbat = True

        for f in fns:
            R, L, C = ref[id(f)], liste[id(f)], create[id(f)]
            for n in proprii[id(f)]:
                # S1: lista NOUA dusa intreaga de un `raise X(lista)`
                if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call):
                    for a in list(n.exc.args) + [k.value for k in n.exc.keywords]:
                        if isinstance(a, ast.Name) and a.id in C:
                            _pune(id(f), a.id)
                # S2: bucla care varsa lista intr-un colector
                if isinstance(n, ast.For) and isinstance(n.iter, ast.Name) and n.iter.id in L:
                    if any(_apel_colector(m) for m in ast.walk(n)):
                        _pune(id(f), n.iter.id)
                # S3: lista data unui ajutor din modul (in jos si in sus, pe pozitie / nume)
                if isinstance(n, ast.Call) and _tinta_apelului(n) in pe_nume:
                    for g in pe_nume[_tinta_apelului(n)]:
                        perechi = [(a, _poz_param(g, i, None)) for i, a in enumerate(n.args)]
                        perechi += [(k.value, _poz_param(g, 0, k.arg)) for k in n.keywords if k.arg]
                        for a, p in perechi:
                            if not (isinstance(a, ast.Name) and p):
                                continue
                            if a.id in R:
                                _pune(id(g), p)
                            if p in ref[id(g)] and a.id in L:
                                _pune(id(f), a.id)
                # S4: lista intoarsa de un ajutor din modul, pe care apelantul o trateaza ca refuz
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and _tinta_apelului(n.value) in pe_nume:
                    for t in n.targets:
                        poz = [(None, t)] if isinstance(t, ast.Name) else list(enumerate(getattr(t, "elts", [])))
                        for i, e in poz:
                            if not (isinstance(e, ast.Name) and e.id in R):
                                continue
                            for g in pe_nume[_tinta_apelului(n.value)]:
                                for r in proprii[id(g)]:
                                    if not (isinstance(r, ast.Return) and r.value is not None):
                                        continue
                                    v = r.value if i is None else (r.value.elts[i] if isinstance(r.value, ast.Tuple)
                                                                    and i < len(r.value.elts) else None)
                                    if isinstance(v, ast.Name) and v.id in liste[id(g)]:
                                        _pune(id(g), v.id)
                # S5: o lista NOUA ale carei elemente curg intr-o lista de refuz e si ea de refuz
                ad = _adaugare_in_lista(n, R)
                if ad:
                    for nm in _nume(ad[1][0]) & C:
                        _pune(id(f), nm)
    return fns, proprii, ref, pe_nume, create


def _retransmise(fn, noduri, R):
    """Numele care, intr-o adaugare, inseamna RETRANSMITERE: exceptia prinsa, listele de refuz, variabilele buclelor peste ele."""
    s = set(R)
    for n in noduri:
        if isinstance(n, ast.ExceptHandler) and n.name:
            s.add(n.name)
    for _ in range(2):
        for n in noduri:
            if isinstance(n, (ast.For, ast.comprehension)) and _nume(n.iter) & s:
                s |= _nume(n.target)
    return s


def _e_releu(fn, noduri):
    """O functie care doar varsa PARAMETRII ei intr-un colector (`_ErorileNotei.adauga`): refuzurile se numara la apelurile ei."""
    p = set(_parametri(fn))
    apeluri = [n for n in noduri if _apel_colector(n)]
    return bool(apeluri) and all(not _siruri(n) and _nume(n) - {"self"} <= p | {"self"} for n in apeluri)


def _purtator(nod):
    if _poarta_temei_structurat(nod):
        return "structurat"
    txt = " ".join(_siruri(nod))
    return "proza" if any(s in txt for s in _SEMNE_ACT) else "fara"


def _adunate(arb):
    """[(nod, functie)] — refuzurile ADUNATE ale modulului, cate unul pe locul unde se scrie motivul (docstringul, „REFUZUL ADUNAT”)."""
    fns, proprii, ref, pe_nume, create = _liste_de_refuz(arb)
    relee = {f.name for f in fns if _e_releu(f, proprii[id(f)])}
    out = []
    for f in fns:
        if f.name in AJUTOARE_ADUNATE:
            continue
        noduri, R = proprii[id(f)], ref[id(f)]
        retr = _retransmise(f, noduri, R)
        releu = f.name in relee
        for n in noduri:
            ad = _adaugare_in_lista(n, R)
            if ad:
                if not (_nume(ad[1][0]) & retr) and not (releu and _nume(ad[1][0]) <= set(_parametri(f))):
                    out.append((n, f.name))
                continue
            if _apel_colector(n):
                argumente = set().union(*[_nume(a) for a in list(n.args) + [k.value for k in n.keywords]])
                if releu or argumente & retr:
                    continue
                out.append((n, f.name))
                continue
            if isinstance(n, ast.Call) and _tinta_apelului(n) in AJUTOARE_ADUNATE:
                out.append((n, f.name))
                continue
            if isinstance(n, ast.Call) and _tinta_apelului(n) in relee and _tinta_apelului(n) != f.name:
                out.append((n, f.name))
    return out, {k: ref[k] & create[k] for k in ref}


def inventar():
    """[{fisier, linia, functie, clasa, stare, purtator, forma}] — un rand per refuz care opreste un act: `raise` (forma „raise”)
    sau refuz ADUNAT intr-un colector (forma „adunat”, docstringul de modul)."""
    out = []
    for cale in _fisiere():
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
        parinte = {}
        for fn in ast.walk(arb):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(fn):
                    parinte.setdefault(id(n), fn.name)
        adunate, ref = _adunate(arb)
        # `raise X(lista_de_refuz)` doar DUCE motivele numarate la locul lor: nu se numara a doua oara
        duc = set()
        for fn in ast.walk(arb):
            if isinstance(fn, _FN):
                for n in _noduri_proprii(fn):
                    if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call) and any(
                            isinstance(a, ast.Name) and a.id in ref[id(fn)] for a in n.exc.args):
                        duc.add(id(n))
        for n in ast.walk(arb):
            if not isinstance(n, ast.Raise) or id(n) in duc:
                continue
            clasa, stare = _clasa_si_stare(n)
            if clasa is None:
                continue
            out.append({"fisier": rel, "linia": n.lineno,
                        "functie": parinte.get(id(n), "(modul)"),
                        "clasa": clasa, "stare": stare, "purtator": _purtator(n),
                        "citeaza": modul_citeaza_legea(cale), "forma": "raise"})
        for n, fnume in adunate:
            out.append({"fisier": rel, "linia": n.lineno, "functie": fnume,
                        "clasa": "refuz", "stare": 400, "purtator": _purtator(n),
                        "citeaza": modul_citeaza_legea(cale), "forma": "adunat"})
    return out


def refuzuri_care_INTORC():
    """Modul de esec 4, numarat: `return {"eroare": ...}` — refuz care nu trece prin `raise`."""
    out = []
    for cale in _fisiere():
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
        for n in ast.walk(arb):
            if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict):
                chei = {k.value for k in n.value.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                if chei & {"eroare", "erori", "erori_campuri"}:
                    out.append({"fisier": rel, "linia": n.lineno})
    return out


_CITARE = None


def modul_citeaza_legea(cale):
    """Fisierul contine un `Temei(...)` sau un nume `TEMEI*`? Pe AST, nu pe text."""
    global _CITARE
    if _CITARE is None:
        _CITARE = {}
    if cale in _CITARE:
        return _CITARE[cale]
    try:
        arb = ast.parse(io.open(cale, encoding="utf-8").read())
    except SyntaxError:
        _CITARE[cale] = False
        return False
    gasit = False
    for n in ast.walk(arb):
        if isinstance(n, ast.Name) and (n.id == "Temei" or n.id.startswith("TEMEI")):
            gasit = True
            break
        if isinstance(n, ast.Attribute) and (n.attr == "Temei" or n.attr.startswith("TEMEI")):
            gasit = True
            break
    _CITARE[cale] = gasit
    return gasit


def datorie(inv=None):
    """{fisier: n} — refuzuri intr-un modul care CITEAZA legea, dar care nu poarta temeiul.

    Unitatea clichetului. Vezi docstringul de modul pentru de ce nu e `fara` brut.
    """
    inv = inventar() if inv is None else inv
    d = {}
    for r in inv:
        if r["clasa"] == "refuz" and r["purtator"] == "fara" and r["citeaza"]:
            d[r["fisier"]] = d.get(r["fisier"], 0) + 1
    return d


def umbra(inv=None):
    """{fisier: n} — module care REFUZA si nu citeaza legea nicaieri. Nu e datorie; e nemasurat."""
    inv = inventar() if inv is None else inv
    d = {}
    for r in inv:
        if r["clasa"] == "refuz" and not r["citeaza"]:
            d[r["fisier"]] = d.get(r["fisier"], 0) + 1
    return d


def pe_clasa(inv=None):
    inv = inventar() if inv is None else inv
    d = {c: {p: 0 for p in PURTATOR} for c in CLASE}
    for r in inv:
        d[r["clasa"]][r["purtator"]] += 1
    return d


def pe_fisier_fara_temei(inv=None):
    """{fisier: cate refuzuri din clasa `refuz` n-au niciun temei} — unitatea clichetului."""
    inv = inventar() if inv is None else inv
    d = {}
    for r in inv:
        if r["clasa"] == "refuz" and r["purtator"] == "fara":
            d[r["fisier"]] = d.get(r["fisier"], 0) + 1
    return d


def _main():
    import json
    import sys
    inv = inventar()
    if "--json" in sys.argv:
        print(json.dumps({"inventar": inv, "pe_fisier_fara_temei": pe_fisier_fara_temei(inv)},
                         ensure_ascii=False, indent=1, sort_keys=True))
        return 0
    d = pe_clasa(inv)
    print("REFUZURI: %d (`raise` care opresc un act)\n" % len(inv))
    print("%-10s %12s %8s %8s   %s" % ("clasa", "structurat", "proza", "fara", "ce opreste"))
    ce = {"acces": "cine esti (401/403) — temeiul legal n-ar avea ce cauta",
          "negasit": "404 — AMESTECAT: resursa inexistenta + nomenclator inchis",
          "refuz": "ce ai cerut (400/409/422 + exceptiile producatorilor)"}
    for c in CLASE:
        print("%-10s %12d %8d %8d   %s" % (c, d[c]["structurat"], d[c]["proza"], d[c]["fara"], ce[c]))
    fara = pe_fisier_fara_temei(inv)
    dat, umb = datorie(inv), umbra(inv)
    print("\nFARA TEMEI in clasa `refuz`: %d, in %d fisiere." % (sum(fara.values()), len(fara)))
    print("  din care DATORIE (modulul CITEAZA legea, refuzul nu poarta temeiul): %d, in %d fisiere"
          % (sum(dat.values()), len(dat)))
    print("  restul e in module care nu citeaza legea nicaieri — vezi UMBRA")
    for f, n in sorted(dat.items(), key=lambda x: -x[1])[:12]:
        print("   %-46s %d" % (f, n))
    print("\n[umbra] refuzuri in module care NU citeaza legea nicaieri: %d, in %d fisiere"
          % (sum(umb.values()), len(umb)))
    print("   ori sunt generice (si atunci e in regula), ori aplica o regula pe care n-o pot numi")
    ir = refuzuri_care_INTORC()
    print("\n[umbra] refuzuri care INTORC in loc sa ridice (modul de esec 4): %d" % len(ir))
    print("[anti-vacuu] fisiere citite: %d" % len(_fisiere()))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
