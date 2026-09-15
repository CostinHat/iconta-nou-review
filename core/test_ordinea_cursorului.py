# -*- coding: utf-8 -*-
"""GARDĂ (15.09.2026): `cur.description` nu se citește ÎNAINTE de interogarea care îl umple.

DE UNDE VINE, cu instanța ei. `GET /tenants/{id}/d406-active` a răspuns **`500` la orice cerere**
din **13.09.2026**, de la valul V1 al lui P7 (`8d182afa`), și nimeni n-a aflat. Codul era:

    with conn.cursor() as cur:
        cols = [d[0] for d in cur.description]                    # <- `description` e None aici
        lista = [dict(zip(cols, r)) for r in repo.active_...(cur, schema, an)]

Înainte de val, `cur.execute(...)` era **chiar acolo**, deasupra liniei de coloane. Valul a mutat
`execute` în depozit — corect — și a lăsat linia unde era. `cur.description` descrie ultima
interogare **executată**; fără una, e `None`, iar `[d[0] for d in None]` ridică `TypeError`.

**De ce n-a prins-o nicio gardă:** ruta n-are apelant (`[api_intern_v1] … fara UI inca, pastrat
deliberat`) — exact clasa pe care **R70** o numește: *„o rută poate fi scrisă, gardată și verde, fără
ca nimic s-o cheme."* Prima apăsare pe ea a fost proba de lanț a etapei 2, lotul I.

**De ce o GARDĂ și nu doar o reparație:** clasa e a valurilor de mutare, nu a unui fișier. Un val
viitor care scoate un `execute` dintr-o funcție lasă exact aceeași urmă, iar singurul lucru care o
deosebește de cod bun e **ORDINEA** — deci se poate verifica mecanic.

CE VERIFICĂ, structural: în fiecare bloc `with … .cursor() as cur:`, prima instrucțiune care
citește `cur.description` nu are voie să stea înaintea primei instrucțiuni care **execută** ceva pe
`cur` (`cur.execute` / `cur.executemany`, sau un apel care primește `cur` ca argument — adică un
depozit).

CE NU VERIFICĂ, declarat: (1) când citirea și execuția stau în **aceeași** instrucțiune, ordinea e a
evaluării expresiei, nu a liniilor — se sare, ca să nu acuzăm pe nedrept o comprehensiune corectă;
(2) cursoarele obținute altfel decât din `with … .cursor()`; (3) execuții făcute prin funcții care
primesc conexiunea, nu cursorul.
"""
import ast
import io
import os
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Podeaua de anti-vacuu: atâtea blocuri de cursor trebuie văzute. Măsurat la scriere pe repo-ul
#: real; o scădere sub prag înseamnă că scanul a orbit, nu că repo-ul s-a curățat.
PODEA_BLOCURI = 150


def _fisiere():
    out = ["main.py"]
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if f.endswith(".py") and not f.startswith("test_"):
            out.append("core/%s" % f)
    return [c for c in out if os.path.exists(os.path.join(RAD, c))]


def _numele_cursorului(w):
    """Numele legat de `with … .cursor(…) as NUME`, sau None dacă blocul nu e de cursor."""
    for item in w.items:
        c = item.context_expr
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) \
                and c.func.attr == "cursor" and isinstance(item.optional_vars, ast.Name):
            return item.optional_vars.id
    return None


def _citeste_description(nod, cur):
    for n in ast.walk(nod):
        if isinstance(n, ast.Attribute) and n.attr == "description" \
                and isinstance(n.value, ast.Name) and n.value.id == cur:
            return True
    return False


def _executa(nod, cur):
    """Instrucțiunea execută ceva pe cursor: direct, sau prin apel care primește cursorul."""
    for n in ast.walk(nod):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        if isinstance(f, ast.Attribute) and f.attr in ("execute", "executemany") \
                and isinstance(f.value, ast.Name) and f.value.id == cur:
            return True
        for a in list(n.args) + [k.value for k in n.keywords]:
            if isinstance(a, ast.Name) and a.id == cur:
                return True
    return False


def _abateri(arbore):
    """[(linia, cursor)] pentru blocurile în care `description` se citește înaintea execuției."""
    rele, blocuri = [], 0
    for w in ast.walk(arbore):
        if not isinstance(w, ast.With):
            continue
        cur = _numele_cursorului(w)
        if not cur:
            continue
        blocuri += 1
        for st in w.body:
            citeste, executa = _citeste_description(st, cur), _executa(st, cur)
            if citeste and executa:
                break        # aceeași instrucțiune: ordinea e a evaluării — limită declarată
            if citeste:
                rele.append((getattr(st, "lineno", 0), cur))
                break
            if executa:
                break
    return rele, blocuri


@pytest.fixture(scope="module")
def scanat():
    rele, blocuri = [], 0
    for cale in _fisiere():
        try:
            arb = ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read())
        except SyntaxError:
            continue
        r, b = _abateri(arb)
        blocuri += b
        rele += [(cale, ln, cur) for ln, cur in r]
    return rele, blocuri


def test_description_nu_se_citeste_inaintea_interogarii(scanat):
    rele, _blocuri = scanat
    assert not rele, (
        "`cur.description` citit ÎNAINTE de interogarea care îl umple — ruta va da `500` la ORICE "
        "cerere (instanța care a produs garda: `d406-active`, rupt din 13.09 până pe 15.09):\n  "
        + "\n  ".join("%s:%d (cursor %r)" % x for x in rele))


def test_scanul_nu_e_orb(scanat):
    """ANTI-VACUU: un scan care nu vede niciun bloc de cursor trece proba de mai sus triumfător."""
    _rele, blocuri = scanat
    assert blocuri >= PODEA_BLOCURI, (
        "numai %d blocuri `with … .cursor()` văzute (podea %d): scanul a orbit, nu repo-ul s-a "
        "curățat" % (blocuri, PODEA_BLOCURI))


def test_CALIBRARE_prinde_exact_forma_care_a_produs_defectul():
    """MUTAȚIE pe instanța reală: codul de dinainte de reparație trebuie să cadă."""
    rupt = ("def f(conn, schema, an):\n"
            "    with conn.cursor() as cur:\n"
            "        cols = [d[0] for d in cur.description]\n"
            "        lista = [dict(zip(cols, r)) for r in repo.active_pentru_d406(cur, schema, an)]\n"
            "    return lista\n")
    rele, blocuri = _abateri(ast.parse(rupt))
    assert blocuri == 1, "calibrarea n-a văzut blocul de cursor"
    assert len(rele) == 1, "forma care a produs un `500` de două zile NU e prinsă: %s" % rele


def test_CALIBRARE_tace_pe_cele_trei_forme_CORECTE():
    """Direcția «acuză pe nedrept», pe toate trei formele bune care există în repo."""
    bune = [
        # 1. execute direct, apoi description
        ("def f(conn):\n"
         "    with conn.cursor() as cur:\n"
         "        cur.execute('SELECT 1')\n"
         "        cols = [d[0] for d in cur.description]\n"
         "        return cols\n"),
        # 2. apel la depozit (care execută), apoi description
        ("def f(conn, schema):\n"
         "    with conn.cursor() as cur:\n"
         "        randuri = repo.ceva(cur, schema)\n"
         "        cols = [d[0] for d in cur.description]\n"
         "        return cols, randuri\n"),
        # 3. amândouă în ACEEAȘI instrucțiune: ordinea e a evaluării, nu a liniilor — se sare
        ("def f(conn, schema):\n"
         "    with conn.cursor() as cur:\n"
         "        return [dict(zip([d[0] for d in cur.description], r))\n"
         "                for r in repo.ceva(cur, schema)]\n"),
    ]
    for i, src in enumerate(bune, 1):
        rele, blocuri = _abateri(ast.parse(src))
        assert blocuri == 1, "forma %d: blocul nu s-a văzut" % i
        assert not rele, "forma %d, CORECTĂ, e acuzată pe nedrept: %s" % (i, rele)


def test_CALIBRARE_nu_confunda_alt_cursor_cu_al_nostru():
    """Un `description` al ALTUI cursor nu e al blocului ăsta."""
    src = ("def f(conn):\n"
           "    with conn.cursor() as cur:\n"
           "        cols = [d[0] for d in alt_cur.description]\n"
           "        cur.execute('SELECT 1')\n"
           "        return cols\n")
    rele, _b = _abateri(ast.parse(src))
    assert not rele, "s-a acuzat blocul pentru `description`-ul altui cursor: %s" % rele


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
