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
