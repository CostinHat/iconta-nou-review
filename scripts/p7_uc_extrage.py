# -*- coding: utf-8 -*-
"""P7 · valul USE_CASE — muta PROPRIETATEA TRANZACTIEI din rute in stratul use-case.

DE CE UN INSTRUMENT. Universul e de **385 de rute / 7248 de linii**, cu **599 de `HTTPException`**
in corpuri. O mutare cu mana pe atatea locuri are un mod de esec propriu — un parametru pasat in
alta ordine, un `raise` tradus la alt cod, o linie ramasa in urma — si niciunul nu se vede la
citire. Instrumentul muta CORPUL INTREG al rutei, nu bucati: asa nu trebuie sa stie ce variabile
traverseaza blocul de tranzactie, fiindca nu taie nimic.

REGULA DE MUTARE, si de ce e sigura:
  · corpul rutei pleaca VERBATIM in `core/uc_<grup>.py`, cu aceiasi parametri, in aceeasi ordine;
  · `raise HTTPException(cod, mesaj)` devine `raise _erori.<Clasa>(mesaj)` — harta cod->clasa e
    fixa si se traduce inapoi in stratul HTTP, deci codul si mesajul ies neschimbate. Se poate
    face fiindca **nimeni nu prinde `HTTPException`** (masurat: zero `except HTTPException`);
  · ruta ramane cu semnatura ei (FastAPI valideaza pe ea) si devine o singura linie:
    `return _http(_uc_<grup>.<nume>, <parametri>)`;
  · hotarele tranzactiei nu se ating: aceleasi blocuri `with db.get_conn()`, in aceeasi ordine,
    in aceeasi functie — doar ca functia aia sta acum in stratul use-case.

CE REFUZA SA FACA, si raporteaza in loc sa ghiceasca:
  · rute care construiesc obiecte de raspuns (`Response`, `FileResponse`) — use-case-ul ar vorbi HTTP;
  · rute care primesc `Request`/`UploadFile` si le folosesc in corp — la fel;
  · rute cu cod HTTP calculat (`409 if ... else 404`) — traducerea ar cere o judecata, nu o harta;
  · rute care folosesc un nume din `main.py` pe care mutarea nu-l poate rezolva.
*Un instrument care ghiceste pe restul e mai rau decat unul care se opreste.*
"""
import ast
import builtins
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILTINS = set(dir(builtins))
METODE = ("get", "post", "put", "patch", "delete", "head", "options")
RASPUNS = ("Response", "StreamingResponse", "FileResponse", "JSONResponse",
           "RedirectResponse", "HTMLResponse", "PlainTextResponse", "BackgroundTasks")

#: harta COD -> clasa de domeniu. Singura din tot valul; inversa ei traieste in stratul HTTP.
CLASA = {400: "CerereGresita", 401: "Neautentificat", 403: "FaraDrept", 404: "Inexistent",
         409: "Conflict", 422: "DateInvalide", 423: "Blocat",
         # [lotul 2] Sase conditii pe care aplicatia le deosebea deja prin cod, dar nu le numea.
         # Harta ramane UNA singura, iar inversa ei traieste in `main._COD_EROARE`.
         413: "IntrarePreaMare", 415: "FormatNeacceptat", 429: "PreaDes",
         500: "EsecIntern", 502: "ServiciuStrainCazut", 503: "ServiciuIndisponibil"}


def _sursa():
    return io.open(os.path.join(RAD, "main.py"), encoding="utf-8").read()


class Main(object):
    def __init__(self):
        self.text = _sursa()
        self.arb = ast.parse(self.text)
        self.importuri = {}      # nume -> linia de import
        self.intregi = {}        # constante intregi de modul (coduri HTTP scrise ca nume)
        self.definite = set()    # nume definite la nivel de modul (functii/clase/variabile)
        for n in self.arb.body:
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                linie = ast.get_source_segment(self.text, n)
                for a in n.names:
                    self.importuri[a.asname or a.name.split(".")[0]] = linie
                # o constanta intreaga importata dintr-un modul al casei (`core.mesaje`) e la fel
                # de fixa ca una scrisa aici: se CITESTE din modul, nu se ghiceste.
                if isinstance(n, ast.ImportFrom) and (n.module or "").startswith("core"):
                    try:
                        import importlib
                        mod = importlib.import_module(n.module)
                    except Exception:
                        mod = None
                    if mod is not None:
                        for a in n.names:
                            v = getattr(mod, a.name, None)
                            if isinstance(v, int) and not isinstance(v, bool):
                                self.intregi[a.asname or a.name] = v
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.definite.add(n.name)
            elif isinstance(n, ast.Assign):
                for t in n.targets:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name):
                            self.definite.add(x.id)
                # constantele intregi de modul: un cod HTTP poate fi scris ca nume
                # (`COD_FARA_ACCES_TENANT`), iar valoarea lui e fixa, deci se poate citi.
                if isinstance(n.value, ast.Constant) and isinstance(n.value.value, int) \
                        and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                    self.intregi[n.targets[0].id] = n.value.value

    def rute(self):
        out = []
        for n in ast.walk(self.arb):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for d in n.decorator_list:
                f = d.func if isinstance(d, ast.Call) else d
                if isinstance(f, ast.Attribute) and f.attr in METODE:
                    out.append(n)
                    break
        return out

    def cale(self, fn):
        for d in fn.decorator_list:
            if isinstance(d, ast.Call) and d.args and isinstance(d.args[0], ast.Constant):
                return d.args[0].value
        return ""


def _legate(fn):
    """Numele legate in corpul functiei (parametri, atribuiri, importuri locale, tinte)."""
    legate = {a.arg for a in fn.args.args}
    for x in (fn.args.vararg, fn.args.kwarg):
        if x is not None:
            legate.add(x.arg)
    corp = ast.Module(body=fn.body, type_ignores=[])
    for x in ast.walk(corp):
        if isinstance(x, (ast.Import, ast.ImportFrom)):
            for a in x.names:
                legate.add(a.asname or a.name.split(".")[0])
        elif isinstance(x, ast.Assign):
            for t in x.targets:
                for y in ast.walk(t):
                    if isinstance(y, ast.Name):
                        legate.add(y.id)
        elif isinstance(x, (ast.AugAssign, ast.AnnAssign, ast.For, ast.AsyncFor)):
            for y in ast.walk(x.target):
                if isinstance(y, ast.Name):
                    legate.add(y.id)
        elif isinstance(x, (ast.With, ast.AsyncWith)):
            for it in x.items:
                if it.optional_vars is not None:
                    for y in ast.walk(it.optional_vars):
                        if isinstance(y, ast.Name):
                            legate.add(y.id)
        elif isinstance(x, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for g in x.generators:
                for y in ast.walk(g.target):
                    if isinstance(y, ast.Name):
                        legate.add(y.id)
        elif isinstance(x, ast.ExceptHandler) and x.name:
            legate.add(x.name)
        elif isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            legate.add(x.name)
        # o functie imbricata isi leaga si ea parametrii: `def fmt(r)` inauntru inseamna ca `r` NU
        # vine din afara. Fara asta, `intrastat_praguri` se refuza pentru un nume care e al ei.
        if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            a = x.args
            for p in list(a.args) + list(a.posonlyargs) + list(a.kwonlyargs):
                legate.add(p.arg)
            for p in (a.vararg, a.kwarg):
                if p is not None:
                    legate.add(p.arg)
    return legate


def externe(fn):
    legate = _legate(fn)
    corp = ast.Module(body=fn.body, type_ignores=[])
    out = []
    for x in ast.walk(corp):
        if isinstance(x, ast.Name) and isinstance(x.ctx, ast.Load):
            if x.id not in legate and x.id not in BUILTINS and x.id not in out:
                out.append(x.id)
    return out


def piedici(m, fn):
    """De ce NU se poate muta ruta asta mecanic — lista, nu un bool."""
    p = []
    if isinstance(fn, ast.AsyncFunctionDef):
        p.append("ruta e `async`")
    corp = ast.Module(body=fn.body, type_ignores=[])
    if any(isinstance(x, (ast.Yield, ast.YieldFrom)) for x in ast.walk(corp)):
        p.append("corpul are `yield`")
    nume = {x.id for x in ast.walk(corp) if isinstance(x, ast.Name)}
    atinse = sorted(nume & set(RASPUNS))
    if atinse:
        p.append("construieste raspuns HTTP: %s" % ",".join(atinse))
    for a in fn.args.args:
        adn = ast.get_source_segment(m.text, a.annotation) if a.annotation else ""
        if adn and ("UploadFile" in adn or "Request" in adn):
            if a.arg in nume:
                p.append("foloseste in corp un obiect HTTP (`%s: %s`)" % (a.arg, adn))
    for x in ast.walk(corp):
        if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call) \
                and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException":
            cod = _cod_din(x.exc, m)
            if cod is None:
                p.append("cod HTTP calculat la linia %d" % x.lineno)
            elif cod not in CLASA:
                p.append("cod HTTP %r fara clasa de domeniu" % (cod,))
    nerezolvate = [n for n in externe(fn)
                   if n not in m.importuri and n in m.definite]
    if nerezolvate:
        p.append("nume din main.py: %s" % ",".join(sorted(nerezolvate)))
    necunoscute = [n for n in externe(fn) if n not in m.importuri and n not in m.definite]
    if necunoscute:
        p.append("nume necunoscute: %s" % ",".join(sorted(necunoscute)))
    return p


def _cod_din(apel, m=None):
    """Codul HTTP al unui `HTTPException(...)`, ca int, sau None daca nu se poate sti.

    Se accepta si un NUME de constanta de modul: `COD_FARA_ACCES_TENANT` are o valoare fixa, iar a-l
    refuza ar lasa pe dinafara sase rute pentru un motiv de forma, nu de fond."""
    a = apel.args[0] if apel.args else None
    if a is None:
        for kw in apel.keywords:
            if kw.arg == "status_code":
                a = kw.value
    if isinstance(a, ast.Constant) and isinstance(a.value, int):
        return a.value
    if m is not None and isinstance(a, ast.Name) and a.id in m.intregi:
        return m.intregi[a.id]
    return None


def _mesaj_din(m, apel):
    """Expresia mesajului, ca SURSA — se muta verbatim."""
    if len(apel.args) > 1:
        return ast.get_source_segment(m.text, apel.args[1])
    for kw in apel.keywords:
        if kw.arg == "detail":
            return ast.get_source_segment(m.text, kw.value)
    return '""'


def corp_tradus(m, fn):
    """Sursa corpului rutei, cu `HTTPException(...)` inlocuit prin excepția de domeniu."""
    editari = []
    corp = ast.Module(body=fn.body, type_ignores=[])
    for x in ast.walk(corp):
        if isinstance(x, ast.Raise) and isinstance(x.exc, ast.Call) \
                and isinstance(x.exc.func, ast.Name) and x.exc.func.id == "HTTPException":
            vechi = ast.get_source_segment(m.text, x.exc)
            cod = _cod_din(x.exc, m)
            nou = "_erori.%s(%s)" % (CLASA[cod], _mesaj_din(m, x.exc))
            editari.append((vechi, nou))
    bucati = [ast.get_source_segment(m.text, s) for s in fn.body]
    text = "\n".join(b for b in bucati if b is not None)
    for vechi, nou in editari:
        if vechi and vechi in text:
            text = text.replace(vechi, nou, 1)
    return text
