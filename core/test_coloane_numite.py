# -*- coding: utf-8 -*-
"""[18.10.2026, comanda Costin 8.1 — găsit de e2e-ul 329] Rândul citit „ca tuplu din dict” (`tuple(x.values()) if isinstance(x, dict)`)
pierde coloanele cu ACELAȘI nume pe un cursor dict: două `COALESCE` fără alias se numesc amândouă „coalesce”, trei `(…)::int` „int4”,
două `EXTRACT(…)::int` „extract”; cheia se suprascrie, tuplul iese mai scurt sau cu pozițiile mutate. Pe 18.10 asta a dat 500 pe `GET /coada`
(`coada_api.note_nevalidate`), iar `coada_api.element_activ` și `mf_registru.luni_inregistrate` / `luni_in_ciorna` aveau aceeași
coliziune, latentă (apelanții lor de azi dau cursor tuplu).

Garda: în fiecare funcție din `core/` care face conversia dict -> tuplu, interogările SELECT nu au două coloane de ieșire cu același nume
(numele pe care i-l dă PostgreSQL: aliasul; coloana; tipul unui cast de expresie; funcția). LIMITA: interogările construite din bucăți
care nu sunt literale se citesc cu bucata necunoscută înlocuită; o coloană scrisă într-o variabilă nu se vede."""
import ast
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIPAR = re.compile(r"\.values\(\)\)?\s+if\s+isinstance\(")
_TIP = {"int": "int4", "integer": "int4", "bigint": "int8", "smallint": "int2", "float": "float8", "real": "float4"}


def _text(nod):
    """Șirul SQL al argumentului: literalele, cu orice altceva (schema, o variabilă) înlocuit de `x.`."""
    if isinstance(nod, ast.Constant) and isinstance(nod.value, str):
        return nod.value
    if isinstance(nod, ast.BinOp) and isinstance(nod.op, (ast.Add, ast.Mod)):
        return _text(nod.left) + (_text(nod.right) if isinstance(nod.op, ast.Add) else "")
    if isinstance(nod, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else "x." for v in nod.values)
    return "x."


def _bucati(lista):
    out, n, cur = [], 0, ""
    for c in lista:
        n += c == "("
        n -= c == ")"
        if c == "," and n == 0:
            out.append(cur)
            cur = ""
        else:
            cur += c
    return out + [cur]


def nume_coloane(sql):
    """Numele coloanelor de ieșire ale primului SELECT (cum le numește PostgreSQL), sau None."""
    m = re.search(r"\bSELECT\s+(?:DISTINCT\s+)?(.*)", sql, re.I | re.S)
    if not m:
        return None
    rest, n, i = m.group(1), 0, 0
    while i < len(rest):                     # FROM-ul de pe nivelul de sus
        n += rest[i] == "("
        n -= rest[i] == ")"
        if n == 0 and re.match(r"\s+FROM\s", rest[i:], re.I):
            break
        i += 1
    out = []
    for it in (x.strip() for x in _bucati(rest[:i])):
        a = re.search(r"\s+AS\s+\"?(\w+)\"?\s*$", it, re.I)
        if a:
            out.append(a.group(1).lower())
        elif re.match(r"\(\s*SELECT\b", it, re.I) and it.endswith(")"):   # subinterogarea: numele coloanei ei
            out.append((nume_coloane(it[1:-1]) or ["?column?"])[0])
        elif re.fullmatch(r"[\w.]+", it):
            out.append(it.split(".")[-1].lower())
        elif re.fullmatch(r"\(.*\)\s*::\s*(\w+)", it, re.S):
            t = re.fullmatch(r"\(.*\)\s*::\s*(\w+)", it, re.S).group(1).lower()
            out.append(_TIP.get(t, t))
        elif re.match(r"(\w+)\s*\(", it):
            out.append(re.match(r"(\w+)\s*\(", it).group(1).lower())
        else:
            out.append("?column?")
    return out


def coliziuni(sursa, cale="x.py"):
    rele = []
    arb = ast.parse(sursa)
    for fn in ast.walk(arb):
        if not isinstance(fn, ast.FunctionDef) or not TIPAR.search(ast.get_source_segment(sursa, fn) or ""):
            continue
        for c in ast.walk(fn):
            if isinstance(c, ast.Call) and getattr(c.func, "attr", None) == "execute" and c.args:
                col = nume_coloane(_text(c.args[0]))
                dubluri = sorted({x for x in col or [] if col.count(x) > 1})
                if dubluri:
                    rele.append((cale, c.lineno, fn.name, dubluri))   # (fișier, linie, funcție, numele care se repetă)
    return rele


def test_coloanele_citite_ca_tuplu_din_dict_au_nume_distincte():
    rele, vazute = [], 0
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if f.endswith(".py") and not f.startswith("test_"):
            s = open(os.path.join(RAD, "core", f), encoding="utf-8").read()
            if TIPAR.search(s):
                vazute += 1
                rele += coliziuni(s, "core/" + f)
    assert vazute >= 8, "anti-vacuu: conversiile dict -> tuplu nu mai sunt găsite (%d)" % vazute
    assert not rele, rele


def test_CALIBRARE_coliziunile_din_18_10_sunt_prinse():
    vechi = '''
def note_nevalidate(cur, schema, de_la, pana_la):
    q = schema
    cur.execute("SELECT i.id, i.data, " + q + "eticheta_nota(i.id), COALESCE(i.document_ref, i.descriere), "
                "COALESCE((SELECT SUM(l.suma) FROM " + q + "inregistrari_linii l WHERE l.inregistrare_id = i.id), 0) "
                "FROM " + q + "inregistrari i WHERE i.status <> 'validata'", (de_la,))
    return [tuple(x.values()) if isinstance(x, dict) else x for x in cur.fetchall()]


def element_activ(cur):
    cur.execute("SELECT c.id, c.stare, (c.payload->>'_an')::int, (c.payload->>'_luna')::int, (c.payload->>'_trim')::int, "
                "COALESCE(u.nume, u.email) FROM public.declaratii_coada c")
    r = cur.fetchone()
    return tuple(r.values()) if isinstance(r, dict) else tuple(r)


def luni(cur):
    cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM i.data)::int, EXTRACT(MONTH FROM i.data)::int FROM inregistrari i")
    return {tuple(x.values()) if isinstance(x, dict) else tuple(x) for x in cur.fetchall()}
'''
    r = [(fn, dubluri) for _c, _l, fn, dubluri in coliziuni(vechi)]
    assert r == [("note_nevalidate", ["coalesce"]), ("element_activ", ["int4"]), ("luni", ["extract"])], r
