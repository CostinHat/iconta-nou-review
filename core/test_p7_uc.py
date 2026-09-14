# -*- coding: utf-8 -*-
"""core/test_p7_uc.py — CONTRACTUL HTTP al valului use-case, confruntat cu starea de dinainte.

Valul a mutat 312 corpuri de ruta si 59 de helperi din `main.py` in stratul use-case, traducand pe
drum fiecare `HTTPException(cod, mesaj)` in `_erori.<Clasa>(mesaj)`. Afirmatia care tine tot valul e
una singura: **codul si mesajul care ies din aplicatie sunt neschimbate.**

Proba nu o crede pe cuvant. Ia `main.py` **de la commitul dinainte de val** (`git show
43fd2197:main.py`), aduna pentru fiecare ruta si fiecare helper multimea perechilor
`(cod HTTP, mesaj)` pe care le ridica, si o compara cu multimea de acum — citita din functia
use-case unde a ajuns corpul, cu clasa tradusa inapoi in cod prin **aceeasi harta** pe care o
foloseste `main._http_din`.

DE CE MERGE ASA, si nu pe text: mesajul se compara ca **ARBORE** (`ast.dump`), nu ca sir. Corpul a
fost dedentat cand a plecat, deci un `"...' \\n '..."` scris pe doua randuri isi schimba sursa fara
sa-si schimbe valoarea; arborele nu se lasa pacalit nici intr-o directie, nici in cealalta.

CE NU ACOPERA: perechile pe care le ridica functii chemate DIN corp (ele se confrunta la randul lor,
ca helperi), si rutele care n-au plecat inca — acelea se compara cu ele insele, deci proba spune
despre ele doar ca n-au fost atinse.
"""
import ast
import copy
import io
import os
import subprocess

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: ultimul commit publicat INAINTE de valul use-case. Nu se schimba: e reperul confruntarii.
BAZA = "43fd2197"
METODE = ("get", "post", "put", "patch", "delete", "head", "options")

#: singura abatere acceptata de la „mesaj neschimbat", cu motivul ei. Orice alta abatere pica.
ABATERI = {
    ("vanzare_aur_investitii", "suma invalida"): (
        "G5 (`core/test_g1_cod_mesaj.py`): un input-guard telegrafic primeste constrangerea in "
        "mesaj. Codul ramane 422. Cazul a intrat in domeniul lui G5 odata cu mutarea corpului "
        "rutei din `main.py` in `core/uc_tenants.py` — regula nu s-a slabit, s-a aplicat."),
}


def _sursa_veche():
    r = subprocess.run(["git", "show", "%s:main.py" % BAZA], cwd=RAD,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("commitul de baza %s nu e in arborele asta: %s" % (BAZA, r.stderr[:120]))
    return r.stdout


def _harta_cod():
    """clasa de domeniu -> cod HTTP, CITITA din stratul HTTP, nu rescrisa aici."""
    import main
    return {c.__name__: cod for c, cod in main._COD_EROARE}


def _intregi(arb):
    """Numele care ÎNSEAMNĂ un cod HTTP: constante întregi de modul, scrise aici sau importate.

    Șase refuzuri scriu codul ca nume (`COD_FARA_ACCES_TENANT`), importat din `core.mesaje`. Citit
    doar din fișier, el ar rămâne necunoscut, iar comparația ar raporta o „schimbare" între un cod
    nerezolvat și unul rezolvat — despre aceeași linie."""
    out = {}
    for n in arb.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name) and isinstance(n.value, ast.Constant) \
                and isinstance(n.value.value, int) and not isinstance(n.value.value, bool):
            out[n.targets[0].id] = n.value.value
        elif isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
            try:
                import importlib
                mod = importlib.import_module(n.module)
            except Exception:
                continue
            for a in n.names:
                v = getattr(mod, a.name, None)
                if isinstance(v, int) and not isinstance(v, bool):
                    out[a.asname or a.name] = v
    return out


def _e_ruta(n):
    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    for d in n.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        if isinstance(f, ast.Attribute) and f.attr in METODE:
            return True
    return False


class _FaraCalificare(ast.NodeTransformer):
    """`_uc_comun._mesaj_intrare(e)` și `_mesaj_intrare(e)` sunt ACELAȘI apel.

    Învelișul din `main.py` cheamă funcția din `core/uc_comun.py` și-i întoarce rezultatul neatins,
    deci mesajul produs e identic. Ce s-a schimbat e unde locuiește funcția, nu ce spune. Calificarea
    se scoate înainte de comparație — altfel proba ar raporta 40 de „schimbări de contract" care
    sunt, toate, același nume scris cu adresa lui."""

    #: ce citea ruta din obiectul HTTP → cum se numește valoarea aceea în use-case. Învelișul o
    #: citește și o pasează, deci e ACEEAȘI valoare, sub alt nume.
    DIN_FISIER = {"filename": "nume_fisier", "content_type": "tip_continut"}

    def visit_Attribute(self, nod):
        self.generic_visit(nod)
        if isinstance(nod.value, ast.Name) and nod.value.id in ("_uc_comun", "_erori"):
            return ast.copy_location(ast.Name(id=nod.attr, ctx=ast.Load()), nod)
        if nod.attr in self.DIN_FISIER and isinstance(nod.value, ast.Name):
            return ast.copy_location(ast.Name(id=self.DIN_FISIER[nod.attr], ctx=ast.Load()), nod)
        return nod

    def visit_Call(self, nod):
        self.generic_visit(nod)
        if isinstance(nod.func, ast.Name) and nod.func.id == "_octetii":
            return ast.copy_location(ast.Name(id="continut", ctx=ast.Load()), nod)
        return nod


def _dump(nod):
    if nod is None:
        return ""
    return ast.dump(_FaraCalificare().visit(copy.deepcopy(nod)))


def _mesaj(apel):
    if len(apel.args) > 1:
        return apel.args[1]
    for kw in apel.keywords:
        if kw.arg == "detail":
            return kw.value
    return None


def _frunze_cod(expr, intregi, locale):
    """Codurile pe care le poate lua expresia — un `409 if ... else 404` da {409, 404}.

    Se accepta si un NUME: o constanta de modul, sau o variabila locala legata o singura data de
    un `IfExp` de intregi (`http = 409 if ... else 404`), fiindca atunci valorile sunt tot fixe."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, int):
        return frozenset([expr.value])
    if isinstance(expr, ast.IfExp):
        return _frunze_cod(expr.body, intregi, locale) | _frunze_cod(expr.orelse, intregi, locale)
    if isinstance(expr, ast.Name):
        if expr.id in intregi:
            return frozenset([intregi[expr.id]])
        if expr.id in locale:
            return _frunze_cod(locale[expr.id], intregi, {})
    return frozenset()


def _frunze_clasa(expr, harta):
    """Codurile in care se traduce expresia de CLASA din use-case, prin harta stratului HTTP."""
    if isinstance(expr, ast.Attribute) and expr.attr in harta:
        return frozenset([harta[expr.attr]])
    if isinstance(expr, ast.Name) and expr.id in harta:
        return frozenset([harta[expr.id]])
    if isinstance(expr, ast.IfExp):
        return _frunze_clasa(expr.body, harta) | _frunze_clasa(expr.orelse, harta)
    return frozenset()


def _locale(fn):
    """Variabilele locale legate O SINGURA data — doar alea se pot citi ca valori fixe."""
    cate, val = {}, {}
    for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
        if isinstance(x, ast.Assign) and len(x.targets) == 1 and isinstance(x.targets[0], ast.Name):
            n = x.targets[0].id
            cate[n] = cate.get(n, 0) + 1
            val[n] = x.value
    return {n: v for n, v in val.items() if cate[n] == 1}


def perechi_vechi(fn, intregi):
    """`(coduri, arborele mesajului)` pentru fiecare `raise HTTPException(...)` din corp."""
    out, loc = [], _locale(fn)
    for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
        if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call) \
                and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException":
            a = x.exc.args[0] if x.exc.args else None
            if a is None:
                for kw in x.exc.keywords:
                    if kw.arg == "status_code":
                        a = kw.value
            m = _mesaj(x.exc)
            out.append((_frunze_cod(a, intregi, loc), _dump(m)))
    return out


def perechi_noi(fn, harta):
    """La fel, dar din use-case: clasa de domeniu tradusa inapoi in cod."""
    out, loc = [], _locale(fn)
    for x in ast.walk(ast.Module(body=fn.body, type_ignores=[])):
        if not isinstance(x, ast.Raise) or not isinstance(x.exc, ast.Call):
            continue
        coduri = _frunze_clasa(x.exc.func, harta)
        if not coduri and isinstance(x.exc.func, ast.Name) and x.exc.func.id in loc:
            coduri = _frunze_clasa(loc[x.exc.func.id], harta)
        if not coduri:
            continue
        m = x.exc.args[0] if x.exc.args else None
        out.append((coduri, _dump(m)))
    return out


def _module_uc():
    """{(modul, nume): nod} pentru tot stratul use-case."""
    out = {}
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.startswith("uc_") or not f.endswith(".py"):
            continue
        arb = ast.parse(io.open(os.path.join(RAD, "core", f), encoding="utf-8").read())
        for n in arb.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out[(f[:-3], n.name)] = n
    return out


def _tinta_invelisului(nod):
    """`(modul, nume)` pe care îl îmbracă funcția din `main.py`, sau None dacă nu e înveliș.

    Forma nu e una singură: cele mai multe învelișuri sunt `try: return _uc_X.f(...)`, dar cele care
    construiesc un răspuns au înăuntru `a, b = _uc_X.f(...)` urmat de `return Response(...)`, iar
    cele care primesc un fișier citesc octeții înainte. Ce le face înveliș e **delegarea din `try`**,
    nu forma lui `return`."""
    if not isinstance(nod, ast.FunctionDef) or not nod.body:
        return None
    t = nod.body[-1]
    if not isinstance(t, ast.Try) or not t.body:
        return None
    for x in ast.walk(ast.Module(body=t.body, type_ignores=[])):
        if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) \
                and isinstance(x.func.value, ast.Name) and x.func.value.id.startswith("_uc"):
            alias = x.func.value.id
            return (alias[1:] if alias.startswith("_") else alias, x.func.attr)
    return None


def confrunta(vechi_src, nou_src, uc, harta):
    """Nucleul probei, scos afara ca sa poata fi chemat si pe un univers FABRICAT.

    Intoarce `(diferente, numar_de_functii_confruntate, numar_de_perechi)`."""
    av, an = ast.parse(vechi_src), ast.parse(nou_src)
    iv, inn = _intregi(av), _intregi(an)
    vechi = {n.name: n for n in av.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    nou = {n.name: n for n in an.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    dif, confruntate, perechi = [], 0, 0
    for nume, vfn in sorted(vechi.items()):
        nfn = nou.get(nume)
        if nfn is None:
            continue
        tinta = _tinta_invelisului(nfn)
        if tinta is not None:
            corp = uc.get(tinta)
            if corp is None:
                dif.append("%s: invelisul trimite la %s, care nu exista" % (nume, tinta))
                continue
            acum = perechi_noi(corp, harta)
        else:
            acum = perechi_vechi(nfn, inn)          # n-a plecat inca: se compara cu el insusi
        inainte = perechi_vechi(vfn, iv)
        confruntate += 1
        perechi += len(inainte)
        if sorted(inainte) != sorted(acum):
            ramase_v = [p for p in inainte if p not in acum]
            ramase_n = [p for p in acum if p not in inainte]
            ramase_v, ramase_n = _fara_abateri(nume, ramase_v, ramase_n)
            if ramase_v or ramase_n:
                dif.append("%s:\n      inainte, fara pereche: %s\n      acum, fara pereche:     %s"
                           % (nume, ramase_v[:3], ramase_n[:3]))
    return dif, confruntate, perechi


def _fara_abateri(nume, ramase_v, ramase_n):
    """Scoate abaterile DECLARATE — fiecare cu motivul ei, sus in fisier."""
    for (rut, mesaj), _motiv in ABATERI.items():
        if rut != nume:
            continue
        tinta = ast.dump(ast.Constant(value=mesaj))
        v = [p for p in ramase_v if p[1] == tinta]
        if v and len(ramase_n) == len(v):
            ramase_v = [p for p in ramase_v if p not in v]
            ramase_n = [p for p in ramase_n if p[0] != v[0][0]]
    return ramase_v, ramase_n


# =================================================================================================
# PROBELE
# =================================================================================================

def test_harta_acopera_tot_vocabularul():
    """O clasa de domeniu fara traducere ar iesi din aplicatie ca `500` — tacut, si cu alt mesaj."""
    from core import erori
    harta = _harta_cod()
    lipsa = [c.__name__ for c in erori.TOATE if c.__name__ not in harta]
    assert not lipsa, "clase fara cod HTTP in `main._COD_EROARE`: %s" % lipsa


def test_niciun_HTTPException_in_stratul_use_case():
    """Criteriul canonic: *un use-case nu construieste `HTTPException`* (PLAN_HARDENING.md:832)."""
    gasit = []
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if not f.startswith("uc_") or not f.endswith(".py"):
            continue
        arb = ast.parse(io.open(os.path.join(RAD, "core", f), encoding="utf-8").read())
        for x in ast.walk(arb):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) \
                    and x.func.id == "HTTPException":
                gasit.append("core/%s:%d" % (f, x.lineno))
    assert not gasit, "`HTTPException` construit in stratul use-case: %s" % gasit[:10]


def test_perechile_cod_mesaj_sunt_NESCHIMBATE():
    """Afirmatia care tine tot valul, confruntata functie cu functie cu starea de dinainte."""
    nou = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    dif, confruntate, perechi = confrunta(_sursa_veche(), nou, _module_uc(), _harta_cod())
    assert not dif, ("contractul HTTP s-a schimbat in %d locuri:\n    %s"
                     % (len(dif), "\n    ".join(dif[:8])))


def _apeluri(nod, harta):
    """Ce CHEAMĂ o funcție, ca multiset de nume — normalizat peste traducerea valului.

    `_uc_comun._cere_perioada(...)` și `_cere_perioada(...)` sunt același apel (se ia `.attr`), iar
    `_erori.<Clasa>(...)` se numără ca `HTTPException`, fiindcă asta a înlocuit. Apelurile pe care
    valul le ADAUGĂ prin construcție — delegarea către use-case și `_http_din` — se scad."""
    c, loc = {}, _locale(nod)
    for x in ast.walk(ast.Module(body=nod.body, type_ignores=[])):
        if not isinstance(x, ast.Call):
            continue
        f = x.func
        nume = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)
        if nume is None:
            # `raise (_erori.Conflict if ... else _erori.Inexistent)(mesaj)`: clasa se alege în chiar
            # expresia de apel. E tot vocabularul, deci tot ce a înlocuit `HTTPException`.
            if _frunze_clasa(f, harta):
                c["HTTPException"] = c.get("HTTPException", 0) + 1
            continue
        # `cod = _erori.Conflict if ... else _erori.Inexistent` apoi `raise cod(mesaj)`: ridicarea se
        # face printr-un NUME LOCAL, dar clasa tot din vocabular vine. Se numără ca `HTTPException`,
        # fiindcă exact asta a înlocuit — altfel cele patru rute de coadă ar arăta ca apeluri pierdute.
        if nume in harta or (nume in loc and _frunze_clasa(loc[nume], harta)):
            nume = "HTTPException"
        c[nume] = c.get(nume, 0) + 1
    return c


def test_NICIUN_APEL_nu_s_a_pierdut_pe_drum():
    """Conservarea apelurilor: ce chema ruta înainte, cheamă și acum — învelișul plus use-case-ul.

    **De ce e nevoie de proba asta pe lângă cea de mai sus.** Perechile `(cod, mesaj)` spun ce se
    întâmplă când operațiunea REFUZĂ; nu spun nimic despre o instrucțiune care a dispărut tăcut.
    Instanța care a cerut-o: mutatorul a lăsat pe dinafară `_rate_limit_reset(request)` și
    `_rate_limit_email(_magic_rate, request)` — două gărzi anti-spam —, iar contractul de refuz a
    rămas identic, suita verde, ruff verde. *Un apel care nu se mai face nu strigă; se vede numai
    numărându-l.*
    """
    harta = _harta_cod()
    uc = _module_uc()
    nou_src = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    av, an = ast.parse(_sursa_veche()), ast.parse(nou_src)
    vechi = {n.name: n for n in av.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    nou = {n.name: n for n in an.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    dif, confruntate = [], 0
    for nume, vfn in sorted(vechi.items()):
        nfn = nou.get(nume)
        if nfn is None:
            continue
        tinta = _tinta_invelisului(nfn)
        if tinta is None:
            continue                      # n-a plecat: se compară cu el însuși, n-are ce spune
        corp = uc.get(tinta)
        if corp is None:
            dif.append("%s: învelișul trimite la %s, care nu există" % (nume, tinta))
            continue
        confruntate += 1
        inainte = _apeluri(vfn, harta)
        acum = _apeluri(nfn, harta)
        for k, v in _apeluri(corp, harta).items():
            acum[k] = acum.get(k, 0) + v
        acum.pop("_http_din", None)
        acum[tinta[1]] = acum.get(tinta[1], 0) - 1          # delegarea, adăugată de val
        if acum.get(tinta[1]) == 0:
            acum.pop(tinta[1])
        lipsa = {k: inainte[k] - acum.get(k, 0) for k in inainte if inainte[k] > acum.get(k, 0)}
        if lipsa:
            dif.append("%s: apeluri pierdute %s" % (nume, lipsa))
    assert confruntate >= 300, "doar %d funcții confruntate — universul s-a golit" % confruntate
    assert not dif, ("apeluri care nu se mai fac, în %d funcții:\n    %s"
                     % (len(dif), "\n    ".join(dif[:10])))


def test_DECORATORII_rutelor_sunt_NEATINSI():
    """Textul de deasupra lui `def`, literă cu literă — decoratorii **cu comentariile lor**.

    **De ce e o probă și nu o presupunere.** Mutatorul reconstruia decoratorii din AST, iar AST-ul
    n-are comentarii: 27 de rute și-au pierdut comentariul de pe linia decoratorului. Printre ele,
    cinci purtau marcajul `[api_intern_v1]` — o **declarație citită de cod**: `core/test_ruta_fara_
    apelant` citește exact linia aia ca să știe care rute își declară singure lipsa unui ecran. Cele
    cinci au trecut din EXCLUS în ROȘU la verificator, deși declarația fusese scrisă acolo de mult.

    *Un comentariu nu e decorativ când un instrument îl citește.*
    """
    metode = METODE

    def decoratori(src):
        arb = ast.parse(src)
        linii = src.splitlines(True)
        out = {}
        for n in ast.walk(arb):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or not n.decorator_list:
                continue
            if not any(isinstance(d, ast.Call) and getattr(d.func, "attr", None) in metode
                       for d in n.decorator_list):
                continue
            out[n.name] = "".join(linii[n.decorator_list[0].lineno - 1:n.lineno - 1])
        return out

    vechi = decoratori(_sursa_veche())
    acum = decoratori(io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read())
    comune = sorted(set(vechi) & set(acum))
    assert len(comune) >= 400, "doar %d rute comune — universul s-a golit" % len(comune)
    dif = [n for n in comune if vechi[n] != acum[n]]
    assert not dif, ("decoratori schimbați la %d rute (primele: %s). Un comentariu de pe linia "
                     "decoratorului poate fi o declarație pe care o citește un instrument."
                     % (len(dif), dif[:6]))


def test_CE_CERE_ALTCINEVA_de_la_main_exista():
    """Fiecare `main.<nume>` cerut din `core/` sau `scripts/` există — a patra pierdere tăcută.

    `core/firma_rezumat.py` cheamă `_main.pastila_firma(...)`: un nume pe care `main.py` îl importa
    pentru alții, fără să-l folosească el însuși. După ce cele 385 de corpuri au plecat, o curățenie
    automată de importuri l-a văzut „nefolosit" și l-a scos — iar lucrătorul modelului de citire a
    început să dea `AttributeError`, cu șase firme ajunse cu `control_fiscal` în stare de eroare.

    *Într-un modul care e citit din afară, «nefolosit aici» nu înseamnă «nefolosit».* Proba citește
    ACCESELE din cod, nu o listă scrisă de mână: un nume nou cerut de altcineva intră singur.
    """
    import re
    import main
    ceruti = set()
    for rad, _d, fisiere in os.walk(RAD):
        if any(x in rad for x in (".git", "venv", "__pycache__", "node_modules")):
            continue
        if os.path.basename(rad) not in ("core", "scripts"):
            continue
        for f in fisiere:
            if not f.endswith(".py") or f.startswith("test_"):
                continue
            s = io.open(os.path.join(rad, f), encoding="utf-8", errors="ignore").read()
            if not re.search(r"\bimport main\b", s):
                continue
            for m in re.finditer(r"\b_main\d*\.([A-Za-z_][A-Za-z0-9_]*)", s):
                ceruti.add((os.path.join(os.path.basename(rad), f), m.group(1)))
    assert len(ceruti) >= 3, "anti-vacuu: doar %d accese gasite — cautarea s-a rupt" % len(ceruti)
    lipsa = sorted("%s -> main.%s" % (f, n) for f, n in ceruti if not hasattr(main, n))
    assert not lipsa, ("nume cerute de la `main` care nu mai exista:\n    %s"
                       % "\n    ".join(lipsa))


def test_MUTATIE_o_garda_pierduta_la_mutare_e_prinsa():
    """Calibrarea probei de mai sus, pe propriul ei mod de eșec — și pe instanța care a cerut-o.

    Universul e fabricat: o rută care cheamă o gardă și apoi face treaba, și un înveliș care a uitat
    garda. *Exact ce s-a întâmplat cu `_rate_limit_reset`: contract de refuz identic, suită verde,
    ruff verde, și o gardă anti-spam dispărută.*"""
    harta = _harta_cod()
    vechi = ast.parse("def r(a, request):\n    garda(request)\n    return lucru(a)\n").body[0]
    corp = ast.parse("def r(a):\n    return lucru(a)\n").body[0]
    inv_bun = ast.parse("def r(a, request):\n    garda(request)\n    try:\n"
                        "        return _uc_z.r(a)\n    except E as e:\n"
                        "        raise _http_din(e)\n").body[0]
    inv_rau = ast.parse("def r(a, request):\n    try:\n"
                        "        return _uc_z.r(a)\n    except E as e:\n"
                        "        raise _http_din(e)\n").body[0]

    def lipsa(inv):
        inainte = _apeluri(vechi, harta)
        acum = _apeluri(inv, harta)
        for k, v in _apeluri(corp, harta).items():
            acum[k] = acum.get(k, 0) + v
        acum.pop("_http_din", None)
        acum["r"] = acum.get("r", 0) - 1
        return {k: inainte[k] - acum.get(k, 0) for k in inainte if inainte[k] > acum.get(k, 0)}

    assert lipsa(inv_rau) == {"garda": 1}, "garda pierdută a trecut nevăzută"
    assert not lipsa(inv_bun), "învelișul corect e raportat ca pierzând ceva: %s" % lipsa(inv_bun)


def test_ANTIVACUU_chiar_confrunta_ceva():
    """Daca `git show` da gol, daca invelisurile nu se recunosc sau daca perechile nu se citesc,
    proba de sus ar trece pe gol — verde despre o lume pe care n-o vede."""
    nou = io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()
    _dif, confruntate, perechi = confrunta(_sursa_veche(), nou, _module_uc(), _harta_cod())
    assert confruntate >= 300, "doar %d functii confruntate — universul s-a golit" % confruntate
    assert perechi >= 400, "doar %d perechi (cod, mesaj) citite — citirea s-a rupt" % perechi


def test_MUTATIE_un_cod_schimbat_e_prins():
    """Calibrare pe propriul mod de esec: daca traducerea ar da alt cod, proba o spune?

    Universul e FABRICAT — o ruta care refuza cu 404, si un use-case care refuza cu 409. Asa
    calibrarea nu cere ca aplicatia adevarata sa fie stricata ca sa se poata masura."""
    vechi = ("from fastapi import HTTPException\n"
             "@app.get('/x')\n"
             "def ruta_x(a):\n"
             "    raise HTTPException(404, 'nu exista')\n")
    nou = ("@app.get('/x')\n"
           "def ruta_x(a):\n"
           "    try:\n"
           "        return _uc_z.ruta_x(a)\n"
           "    except _erori.EroareDeDomeniu as e:\n"
           "        raise _http_din(e)\n")
    corp = ast.parse("def ruta_x(a):\n    raise _erori.Conflict('nu exista')\n").body[0]
    dif, confruntate, _p = confrunta(vechi, nou, {("uc_z", "ruta_x"): corp}, _harta_cod())
    assert confruntate == 1, "universul fabricat nu s-a confruntat deloc"
    assert dif, "un 404 devenit 409 a trecut nevazut — comparatia nu compara"


def test_MUTATIE_un_mesaj_schimbat_e_prins():
    """A doua directie: acelasi cod, alt mesaj."""
    vechi = ("@app.get('/x')\n"
             "def ruta_x(a):\n"
             "    raise HTTPException(404, 'nu exista')\n")
    nou = ("@app.get('/x')\n"
           "def ruta_x(a):\n"
           "    try:\n"
           "        return _uc_z.ruta_x(a)\n"
           "    except _erori.EroareDeDomeniu as e:\n"
           "        raise _http_din(e)\n")
    corp = ast.parse("def ruta_x(a):\n    raise _erori.Inexistent('nu mai exista')\n").body[0]
    dif, _c, _p = confrunta(vechi, nou, {("uc_z", "ruta_x"): corp}, _harta_cod())
    assert dif, "un mesaj schimbat a trecut nevazut"


def test_MUTATIE_identitatea_nu_da_fals_pozitiv():
    """A treia directie, cea care lipseste de obicei: pe un univers NESCHIMBAT, zero diferente.
    Un comparator care striga mereu e la fel de inutil ca unul care tace mereu."""
    vechi = ("@app.get('/x')\n"
             "def ruta_x(a):\n"
             "    raise HTTPException(404, 'nu exista')\n")
    nou = vechi
    dif, confruntate, _p = confrunta(vechi, nou, {}, _harta_cod())
    assert confruntate == 1 and not dif, "comparatia vede o diferenta acolo unde nu e: %s" % dif
