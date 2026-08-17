# -*- coding: utf-8 -*-
"""core/test_diacritice_afisate.py — GARD DE DIACRITICE PE TEXTUL AFIȘAT (#4, criteriul lui Costin).

CRITERIUL (aceeași distincție ca marker ASCII vs. text afișat):
  • text care ajunge pe ECRAN  -> cu diacritice (ă/â/î/ș/ț);
  • log, assert de test, marker/cod -> ASCII.

Gardul flaghează un șir DOAR dacă e simultan:
  (1) USER-FACING prin ROL sintactic (nu prin ghicit) — un Constant str aflat în:
        - argumentul-mesaj al `HTTPException(<cod>, "MSG")` (poziția `detail` sau kw `detail`);
        - valoarea de string a unei CHEI DE AFIȘARE dintr-un dict (returnat/ridicat):
          mesaj, eroare, cauza, actiune, motiv, temei, limita, avertisment, titlu, remediu, detail;
        - un literal (ne-docstring) din corpul unei EXCEPȚII DE BUSINESS (subclasă de
          ValueError/Exception/RuntimeError) — ex. PerioadaNeconfirmata din core/perioada.py,
          al cărei mesaj ajunge la UI prin handler-ul global (main.py -> 423).
     NU se uită la: `logging.*`/`getLogger().*`, mesaje de `assert`, docstring-uri/comentarii,
     fișiere `test_*.py`. Astea rămân ASCII prin construcție (nu sunt în rolurile de mai sus).
  (2) PROZĂ ROMÂNEASCĂ FĂRĂ DIACRITICE: are spațiu (mai multe cuvinte), are litere mici,
     și NU conține nicio diacritică.
  (3) DATORIE DE DIACRITICE dovedită: conține cel puțin un cuvânt din `_TRIGGERE` — o listă
     CURATĂ de forme ASCII a căror scriere corectă are OBLIGATORIU diacritică (ex. „fara”->fără,
     „invalida”->invalidă, „sterge”->șterge, „pana”->până, „sa”->să, „si”->și). Lista e
     ținută HIGH-PRECISION: cuvinte care ca formă ASCII sunt (aproape) mereu greșite. Formele
     ambigue (infinitiv valid: „verifica”; plural fără diacritică: „invalide”, „emise”; articulat
     valid: „luna”/„factura”/„perioada”) au fost SCOASE ca să nu dea fals-pozitive. Codurile
     (D300, CUI, 4111), acronimele și engleza NU se flaghează. Cuvintele lipite de identificatori
     (`platitor_tva`, `cont_stoc_nou`) sunt ignorate (nu sunt proză, sunt nume de câmp/cod).

Scop: gard UTIL, nu zgomotos. Odată ce un șir e identificat ca având datorie, reparația (cap.6)
adaugă TOATE diacriticele corecte, nu doar cuvântul-declanșator; codurile/câmpurile rămân ASCII.

BASELINE: gol. La 2026-08-15, după diacriticizare, suita e la 0 flagate. Orice mesaj NOU user-facing
fără diacritice va PICA gardul (clichet anti-regresie). Dacă vreodată e nevoie de o excepție
temporară, adaug-o explicit în `_BASELINE` cu motiv — nu relaxa criteriul.
"""
import ast
import glob
import re

import pytest

_DISPLAY_KEYS = {"mesaj", "eroare", "cauza", "actiune", "motiv", "temei",
                 "limita", "avertisment", "titlu", "remediu", "detail"}

_DIAC = set("ăâîșțĂÂÎȘȚşţŞŢ")

# forme ASCII a căror scriere corectă are OBLIGATORIU diacritică (high-precision)
_TRIGGERE = {
    "sa", "fara", "daca", "poti", "intai", "afara", "si", "pana",
    "exista", "sterge", "stergere", "aiba", "adauga", "adaugat", "adaugati",
    "ramas", "ramasa", "reincearca", "reincercati", "incearca", "incercati",
    "completeaza", "corecteaza",
    "inexistenta", "invalida", "negativa", "primita", "rupta", "validata",
    "aleasa", "emisa", "necunoscuta", "necesara", "valabila", "gresita", "gresit",
    "semnatura", "semnaturi", "lipsa", "putin", "putina", "fiecarei", "pret",
    "numar", "numarul", "platitor", "platitorul",
    "gasit", "gasita", "negasit", "gaseste", "lipseste",
    "inregistrat", "inregistrare", "incarcat", "incarcare", "inchis", "inchisa",
    "inceput", "intarziere", "intarziat",
    "cladire", "cladirea", "judet", "judetul",
    "tranzactie", "tranzactia", "tranzactii", "obligatia", "obligatie", "obligatii",
    "cheltuiala", "scadenta", "tara", "societatii",
    "declaratie", "declaratia", "declaratii", "declaratiile",
    "depaseste", "depasit", "depasita", "aceeasi",
    # audit tenant_005 (17.08): mesaje validatori de import
    "gasesc", "tine", "insumeaza", "asociatilor", "asteptat", "depusa", "inainte",
    "raportata", "intelege", "angajarii", "legala", "negasit", "invalida", "inca",
}

# excepții temporare acceptate (șir user-facing lăsat ASCII, cu motiv). Gol = clichet la 0.
_BASELINE = set()


def _files():
    fs = [f for f in glob.glob("core/*.py") if not f.split("/")[-1].startswith("test_")]
    fs.append("main.py")
    return sorted(f for f in fs if __import__("os").path.exists(f))


def _str_lits(node):
    return [(n.lineno, n.value) for n in ast.walk(node)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _is_http(call):
    f = call.func
    return (isinstance(f, ast.Name) and f.id == "HTTPException") or \
           (isinstance(f, ast.Attribute) and f.attr == "HTTPException")


def _cuvinte(s):
    """Cuvinte-proză lowercase din șir. Exclude tokenii lipiți de identificatori (_ sau .)
    — acolo e nume de câmp/cod, nu proză. NB: `x in ("_", ".")`, NU `x in "_."` (șirul gol
    e substring al oricui -> ar sări PRIMUL și ULTIMUL cuvânt)."""
    out = []
    for m in re.finditer(r"[a-z]+", s.lower()):
        before = s[m.start() - 1] if m.start() > 0 else ""
        after = s[m.end()] if m.end() < len(s) else ""
        if before in ("_", ".") or after in ("_", "."):
            continue
        out.append(m.group())
    return out


def flag(s):
    """Întoarce lista sortată de triggere dacă `s` are datorie de diacritice, altfel None."""
    if " " not in s.strip():
        return None
    if not any(c.islower() for c in s):
        return None
    if any(c in _DIAC for c in s):
        return None
    hit = set(_cuvinte(s)) & _TRIGGERE
    return sorted(hit) if hit else None


def _candidati():
    """Toate șirurile USER-FACING (fn, linie, text) din core/ + main.py, după rolul sintactic."""
    cands = []
    import os
    for fn in _files():
        try:
            tree = ast.parse(open(fn, encoding="utf-8").read())
        except (SyntaxError, OSError):
            continue
        exc = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef):
                for b in n.bases:
                    bn = b.id if isinstance(b, ast.Name) else (b.attr if isinstance(b, ast.Attribute) else "")
                    if bn in ("ValueError", "Exception", "RuntimeError"):
                        exc.add(n.name)
        expr_ids = {id(x.value) for x in ast.walk(tree)
                    if isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant)
                    and isinstance(x.value.value, str)}
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and _is_http(n):
                det = n.args[1] if len(n.args) >= 2 else None
                for kw in n.keywords:
                    if kw.arg == "detail":
                        det = kw.value
                if det is not None:
                    for ln, s in _str_lits(det):
                        cands.append((fn, ln, s))
            if isinstance(n, ast.Dict):
                for k, v in zip(n.keys, n.values):
                    if isinstance(k, ast.Constant) and k.value in _DISPLAY_KEYS:
                        for ln, s in _str_lits(v):
                            cands.append((fn, ln, s))
            if isinstance(n, ast.ClassDef) and n.name in exc:
                for sub in ast.walk(n):
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str) and id(sub) not in expr_ids:
                        cands.append((fn, sub.lineno, sub.value))
    return cands


def _flagate():
    out = []
    for fn, ln, s in _candidati():
        h = flag(s)
        if h and s not in _BASELINE:
            out.append((fn, ln, s, h))
    return out


def test_autotest_criteriu_are_dinti():
    """Dinți: proza RO fără diacritice + cuvânt-trigger PICĂ; cu diacritice / log ASCII / cod TREC."""
    # TREBUIE flagate:
    assert flag("luna invalida"), "proza RO fara diacritice cu trigger trebuie flagata"
    assert flag("factura inexistenta"), "regresie: 2 cuvinte (primul/ultimul) NU trebuie sarite"
    assert flag("nota trebuie sa aiba cel putin o linie")
    assert flag("pana atunci calculul e blocat")
    # NU trebuie flagate:
    assert flag("lună invalidă") is None, "are diacritice -> corect"
    assert flag("cannot open socket, retrying now") is None, "engleza / log ASCII"
    assert flag("PERIOADA_BLOCATA") is None, "marker un-cuvant, nu proza"
    assert flag("D300") is None, "cod"
    assert flag("platitor_tva vs snapshot") is None, "trigger lipit de identificator -> ignorat"


def test_niciun_mesaj_user_facing_fara_diacritice():
    if not glob.glob("core/*.py"):
        pytest.skip("core/*.py absent (rulare in afara radacinii)")
    fl = _flagate()
    raport = "\n".join("  %s:%d  %r  <- lipsesc diacritice pe [%s]" % (fn, ln, s, ",".join(h))
                       for fn, ln, s, h in fl)
    assert not fl, (
        "Mesaj(e) USER-FACING fara diacritice (text pe ecran -> cu diacritice; log/assert -> ASCII). "
        "Adauga diacriticele corecte pe proza (codurile/campurile raman ASCII):\n" + raport)


# ==========================================================================
_VALIDATORI_IMPORT = (
    "core/solduri_api.py", "core/solduri_parteneri_api.py", "core/asociati_import_api.py",
    "core/mijloace_fixe_import_api.py", "core/istoric_declaratii_import_api.py",
    "core/articole_import_api.py", "core/salariati_import_api.py", "core/retete_import_api.py",
)


def _flagate_import():
    """TOATE mesajele din validatorii de import - fisiere integral user-facing (fiecare mesaj ajunge
    in .caseta-atentie / #mig-eroare / avertismente per rand), scanate INTEGRAL: prinde raise brut,
    det+=, f-string, avertismente.append(...), structuri pe care _candidati() nu le vede. Se exclud:
    docstring-uri; argumentele lui _gaseste_col (SINONIME DE COLOANA = antetul CSV al utilizatorului,
    poate fi ASCII); string-urile SQL (execute, nu mesaj)."""
    import os
    import re as _re2
    _SQL = _re2.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|VALUES)\b")
    out = []
    for fn in _VALIDATORI_IMPORT:
        if not os.path.exists(fn):
            continue
        tree = ast.parse(open(fn, encoding="utf-8").read())
        doc_ids = {id(x.value) for x in ast.walk(tree)
                   if isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant)
                   and isinstance(x.value.value, str)}
        col_ids = set()
        for c in ast.walk(tree):
            if isinstance(c, ast.Call):
                f = c.func
                nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
                if nm == "_gaseste_col":
                    for a in c.args:
                        for lit in ast.walk(a):
                            if isinstance(lit, ast.Constant) and isinstance(lit.value, str):
                                col_ids.add(id(lit))
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                    and id(n) not in doc_ids and id(n) not in col_ids:
                if _SQL.search(n.value):
                    continue
                h = flag(n.value)
                if h and n.value not in _BASELINE:
                    out.append((fn, n.lineno, n.value, h))
    return out


def test_validatori_import_cu_diacritice():
    """Validatorii de import produc DOAR mesaje afisate contabilului. Orice mesaj-proza fara diacritice
    de aici PICA - indiferent de structura (cheie de afisare / raise brut / det+= / f-string). Audit
    tenant_005, straturile de migrare (17.08.2026)."""
    if not glob.glob("core/*.py"):
        pytest.skip("core/*.py absent")
    fl = _flagate_import()
    raport = "\n".join("  %s:%d  %r  <- lipsesc diacritice pe [%s]" % (fn, ln, s, ",".join(h))
                       for fn, ln, s, h in fl)
    assert not fl, ("Mesaj(e) de validator import fara diacritice (text afisat -> cu diacritice):\n" + raport)


# ==========================================================================
# GARD DE DIACRITICE PE GENERATOARELE DE DECLARATII (audit tenant_005, 17.08.2026)
# Mesajele de blocaj/avertisment ale generatoarelor (raise -> pasul 2 in rosu, res.avertismente ->
# warning) se AFISEAZA contabilului -> cu diacritice. Clasa e SISTEMICA (~50 fisiere d100-d710, ~330
# mesaje - backlog in GARZI); lista de mai jos creste pe masura ce se curata cate un fisier. d205
# curatat integral 17.08 (parcurgere Front D).
_GEN_DECLARATII = (
    "core/d205.py",
)


def _flagate_declaratii():
    import os, re as _re3
    _SQL = _re3.compile(r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|VALUES|WHERE|FROM|JOIN)\b")
    out = []
    for fn in _GEN_DECLARATII:
        if not os.path.exists(fn):
            continue
        tree = ast.parse(open(fn, encoding="utf-8").read())
        doc = {id(x.value) for x in ast.walk(tree)
               if isinstance(x, ast.Expr) and isinstance(x.value, ast.Constant)
               and isinstance(x.value.value, str)}
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc:
                v = n.value
                if "<" in v or ">" in v or "=\"" in v or _SQL.search(v):
                    continue  # tag/atribut XML sau SQL, nu mesaj afisat
                h = flag(v)
                if h and v not in _BASELINE:
                    out.append((fn, n.lineno, v, h))
    return out


def test_generatoare_declaratii_cu_diacritice():
    """Generatoarele de declaratii din _GEN_DECLARATII (curatate) nu mai au mesaje-proza fara diacritice.
    Clasa e sistemica (backlog GARZI); lista creste pe masura ce se curata. RED-probat pe d205."""
    if not glob.glob("core/*.py"):
        pytest.skip("core/*.py absent")
    fl = _flagate_declaratii()
    raport = "\n".join("  %s:%d  %r  <- lipsesc diacritice pe [%s]" % (fn, ln, s, ",".join(h))
                       for fn, ln, s, h in fl)
    assert not fl, ("Mesaj(e) de generator declaratii fara diacritice (text afisat -> cu diacritice):\n" + raport)


# ==========================================================================
# ==========================================================================
# GARD DE DIACRITICE PE FRONTEND (static/js/**/*.js) — extensie #4 (Costin).
# ==========================================================================
# Motiv: pana acum gardul scana DOAR core/*.py + main.py (roluri AST). Textul
# user-facing din JS nu era pazit deloc — carduri de meniu scrise ASCII
# („Incasari zilnice", „Operatiuni speciale", „solduri si rulaje").
#
# JS n-are AST in Python -> folosim REGEX + EURISTICI DE POZITIE. Aceleasi
# 3 porti ca la Python (spatiu = proza, minuscule, ZERO diacritice) + o lista
# HIGH-PRECISION separata `_TRIGGERE_JS`. Preferam FALSE NEGATIVE (ratam
# cateva) in loc de FALSE POSITIVE (semnalam ASCII legitim: clase, id-uri,
# cai API, chei, enum-uri).
#
# POZITII DE AFISARE scanate (doar aici cautam siruri):
#   1. chei de afisare dintr-un obiect: `titlu:`/`desc:`/`eticheta:`/`subtitlu:`
#      /`antet:`/`mesaj:`/`avertisment:`/`placeholder:`/`tooltip:`/`label:`
#      urmate imediat de un string literal (carduri, meniuri);
#   2. atribuiri la `.innerHTML`/`.textContent`/`.innerText`/`.title`
#      /`.placeholder` (RHS = string literal);
#   3. primul argument-string al `nav.deschide(`/`nav.mergi(`/`nav.inlocuieste(`
#      (titlu de ecran);
#   4. template-literale: NODURILE DE TEXT HTML (ce e intre `>` si `<`), DUPA ce
#      stergem interpolarile `${...}` (asa nu scapa enum-uri de tip
#      `o.status === "ciorna"` ca text afisat).
#
# EXCLUSE prin constructie (nu sunt in pozitiile de mai sus):
#   • `console.*`; `api.get/post/put/del(...)` (cai); `querySelector`/`classList`
#     /`getElementById`/`dataset` (selectoare); `import ... from`; `?v=`;
#   • atributele `class=`/`id=`/`data-*` din template-literale (traiesc INTRE
#     `<` si `>`, nu intre `>` si `<` -> nodurile de text le exclud automat);
#   • `semnAjutor("F005")` — argumentul e un COD de marker, nu text afisat;
#   • orice valoare de comparatie/enum din `${...}` (stearsa inainte de scan).
#
# `_decode_js` decodeaza `\\uXXXX`/`\\xXX` INAINTE de verificare: un sir scris
# cu escape (`"Declara\\u021bii"`) are diacritica dupa decode -> NU e flagat.
#
# `_TRIGGERE_JS`: forme ASCII a caror scriere corecta cere OBLIGATORIU o
# diacritica. Formele AMBIGUE (corecte ca ASCII) au fost SCOASE ca sa nu dea
# fals-pozitive: „note"/„notele" (plural corect), „sponsorizare" (nearticulat
# corect), „salariatul" (articulat corect), „scadent" (adj. corect),
# „perioada"/„luna"/„factura" (articulat corect), „aproba"/„aprobat" (participiu
# corect), „ciorna" (articulat corect), „generat" (participiu masc. corect).
# Raman doar formele pe care ASCII e (aproape) mereu gresit in text afisat.
# ==========================================================================

_TRIGGERE_JS = {
    # substantive/actiuni de UI, ASCII = mereu gresit
    "incasari", "incasare", "incasarile", "incasarea",
    "operatiuni", "operatiune", "operatiunile",
    "plati", "plateste", "platesti", "platit", "platita",
    "marja", "sponsorizari",
    "simpla", "fisa",
    "adauga", "adaugat", "adaugati", "adaugare",
    "sterge", "stergere", "stersa", "sters",
    "inregistrare", "inregistrari", "inregistrat", "inregistreaza",
    "salariati", "salariatii",
    "valideaza",
    "cautare", "cauta", "cautati",
    "urmatoarea", "urmatorul", "urmatoare",
    "inchide", "inchisa", "inchidere",
    "atentie", "scadenta", "scadente",
    "ruleaza", "reporneste", "pregatit", "pregateste", "pregatire",
    "greseli", "greseala", "greseste",
    "descarcat", "descarca", "descarcare",
    "generata", "iesire", "reincarca", "incearca",
    # conjunctii/prepozitii/verbe scurte, ASCII = mereu gresit
    "si", "fara", "pana", "dupa", "tara", "daca", "exista", "lipseste",
    "gasit", "gasita", "societatii",
    "declaratie", "declaratia", "declaratii", "declaratiile",
}

# excepcii temporare acceptate (sir user-facing lasat ASCII, cu motiv). Gol = clichet la 0.
_BASELINE_JS = set()

_JS_STR = r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')"
_JS_TMPL_RE = re.compile(r"`(?:[^`\\]|\\.)*`", re.S)
_JS_KEY_RE = re.compile(
    r"\b(titlu|desc|eticheta|subtitlu|antet|mesaj|avertisment|placeholder|tooltip|label)"
    r"\s*:\s*" + _JS_STR)
_JS_ASSIGN_RE = re.compile(
    r"\.(innerHTML|textContent|innerText|title|placeholder)\s*\+?=\s*" + _JS_STR)
_JS_NAV_RE = re.compile(r"nav\.(?:deschide|mergi|inlocuieste)\s*\(\s*" + _JS_STR)
_JS_INTERP_RE = re.compile(r"\$\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}")
_JS_TEXTNODE_RE = re.compile(r">([^<>]+)<")


def _decode_js(s):
    """Decodeaza escape-urile JS (\\uXXXX, \\xXX, \\n...) ca diacriticele scrise
    cu escape sa conteze drept diacritice (nu drept ASCII)."""
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)
    s = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), s)
    for a, b in [("\\n", " "), ("\\t", " "), ("\\r", " "), ("\\'", "'"),
                 ('\\"', '"'), ("\\`", "`"), ("\\\\", "\\")]:
        s = s.replace(a, b)
    return s


def _flag_js(s):
    """Ca `flag`, dar cu `_TRIGGERE_JS`. Intoarce lista triggere sau None.
    Aceleasi 3 porti: proza (spatiu), minuscule, ZERO diacritice."""
    if " " not in s.strip():
        return None
    if not any(c.islower() for c in s):
        return None
    if any(c in _DIAC for c in s):
        return None
    hit = set(_cuvinte(s)) & _TRIGGERE_JS
    return sorted(hit) if hit else None


def _lineno(text, pos):
    return text.count("\n", 0, pos) + 1


def scan_js_text(text):
    """Intoarce [(linie, rol, text_decodat, [triggere])] pentru un sursa JS.
    Extras DOAR din pozitiile de afisare (chei, atribuiri, nav.*, noduri-text)."""
    out = []

    def emit(pos, rol, raw):
        d = _decode_js(raw[1:-1])  # scoate ghilimelele/backtick-urile
        h = _flag_js(d)
        if h:
            out.append((_lineno(text, pos), rol, d.strip(), h))

    for m in _JS_KEY_RE.finditer(text):
        emit(m.start(2), "cheie:" + m.group(1), m.group(2))
    for m in _JS_ASSIGN_RE.finditer(text):
        emit(m.start(2), "atribuire:" + m.group(1), m.group(2))
    for m in _JS_NAV_RE.finditer(text):
        emit(m.start(1), "nav", m.group(1))
    for m in _JS_TMPL_RE.finditer(text):
        base = m.start() + 1
        # sterge ${...} (1 nivel de acolade), pastrand lungimea -> offset->linie valid
        body = _JS_INTERP_RE.sub(lambda mm: " " * len(mm.group(0)), m.group(0)[1:-1])
        for tm in _JS_TEXTNODE_RE.finditer(body):
            d = _decode_js(tm.group(1))
            h = _flag_js(d)
            if h:
                out.append((_lineno(text, base + tm.start(1)), "text-html", d.strip(), h))
    return out


def _js_files():
    return sorted(glob.glob("static/js/**/*.js", recursive=True))


def _flagate_js():
    out = []
    for fn in _js_files():
        try:
            text = open(fn, encoding="utf-8").read()
        except OSError:
            continue
        for ln, rol, s, h in scan_js_text(text):
            if s not in _BASELINE_JS:
                out.append((fn, ln, rol, s, h))
    return out


def test_autotest_js_criteriu_are_dinti():
    """Dinti pe euristica JS: text afisat ASCII PICA; selectoare/cai/enum/diacritice TREC."""
    # TREBUIE flagate (text afisat, pozitie de afisare, ASCII + trigger):
    assert scan_js_text('nav.deschide("Adauga firma", (c) => {})'), "titlu nav ASCII"
    assert scan_js_text('x.innerHTML = `<div>Sterge randul si gata</div>`;'), "nod-text HTML ASCII"
    assert scan_js_text('const c = { titlu: "Operatiuni speciale" };'), "cheie de afisare ASCII"
    assert _flag_js("Incasari zilnice"), "trigger direct"
    # NU trebuie flagate:
    assert not scan_js_text('api.get("/tenants/adauga/lista")'), "cale API, nu afisare"
    assert not scan_js_text('el.classList.add("adauga-activ")'), "selector CSS, nu afisare"
    assert not scan_js_text('x.innerHTML = `<div class="adauga-btn"></div>`;'), "atribut, nu nod-text"
    assert not scan_js_text('t = `${o.status === "adauga" ? "a" : "b"}`;'), "enum in ${...}"
    assert not scan_js_text('console.log("nu am gasit inregistrarea")'), "console, nu afisare"
    assert _flag_js("Adaugă firmă") is None, "are diacritice -> corect"
    assert _flag_js(_decode_js("Declara\\u021bii lucrate")) is None, "escape diacritic -> corect"
    assert _flag_js("firme-optiune-titlu") is None, "un-cuvant (fara spatiu) -> nu e proza"


def test_niciun_text_afisat_js_fara_diacritice():
    fs = _js_files()
    if not fs:
        pytest.skip("static/js/**/*.js absent (rulare in afara radacinii)")
    print("\n[gard-diacritice-JS] fisiere JS scanate: %d" % len(fs))
    assert len(fs) > 0, "0 fisiere scanate -> gardul nu ruleaza"
    fl = _flagate_js()
    raport = "\n".join("  %s:%d  [%s]  %r  <- lipsesc diacritice pe [%s]"
                       % (fn, ln, rol, s, ",".join(h)) for fn, ln, rol, s, h in fl)
    assert not fl, (
        "Text AFISAT in JS fara diacritice (pe ecran -> cu diacritice; cod/cai/selectoare -> ASCII). "
        "Adauga diacriticele corecte pe proza:\n" + raport)
