# -*- coding: utf-8 -*-
"""Garda: coloanele referite in SQL EXISTA in schema reala a tabelelor tenant.

DE CE (13.08.2026): au fost reparate generatoare care faceau `SELECT COALESCE(den, nume)
FROM firma_profil` (coloana `den` inexistenta -> firma_profil are `nume`), `salariati WHERE activ`
(coloana `activ` retrasa) si `plan_conturi ... cont` (coloana e `simbol`, nu `cont`). Clasa NU
era pazita: un SELECT pe o coloana inexistenta trece TACUT la scriere si crapa abia la runtime cu
UndefinedColumn (sau e inghitit de un `except`) -> declaratia iese goala / firma pare fara nume.

CE FACE:
  1. Extrage schema REALA a tabelelor tenant din tenant_template.sql: nume tabel -> set de coloane,
     inclusiv coloanele adaugate prin `ALTER TABLE ... ADD COLUMN` din acelasi template.
  2. Scaneaza core/*.py + main.py, reconstruieste literalii SQL (tokenize: string-uri implicit
     concatenate + f-string-uri, cu `{schema}` pastrat) si, pentru fiecare STATEMENT care atinge
     EXACT UN tabel tenant NEALIASAT (fara JOIN, fara alt tabel, fara public./information_schema.),
     extrage coloanele referite si verifica ca EXISTA in schema tabelului.
  3. ALLOWLIST mic (jos) pentru fals-pozitive inevitabile - azi GOL (euristica e curata).

DE CE DOAR "un tabel, nealiasat": exact clasa bug-ului reparat (coloana necalificata pe un tabel).
Statement-urile cu JOIN/alias folosesc mereu prefix (f., l., i.) -> maparea alias->tabel ar aduce
zgomot fara sa acopere clasa vizata. Restrangerea da 0 fals-pozitive pe ~4000 de referinte reale,
deci garda e utila, nu zgomotoasa. Compromisul: o coloana gresita scrisa CALIFICAT (s.activ) sau
intr-un JOIN nu e prinsa - dar clasa documentata (necalificata, un tabel) e acoperita, dovada in
test_garda_prinde_coloana_inexistenta (den/activ/cont sintetice -> TREBUIE prinse).

Euristica extractiei de coloane (necalificate, dintr-un statement cu un singur tabel):
  - ignora `*`, apeluri de functii (identificator urmat de `(`), keyword-uri SQL, tipuri, alias-uri
    `AS x` (si reutilizarea lor in GROUP/ORDER BY), literali string `'...'`, parametri %s/%%s/%(x)s,
    interpolari python `{...}`, cast-uri `::tip`.
"""
import csv  # noqa: F401  (simetrie cu celelalte garzi ale registrului)
import glob
import pathlib
import re
import tokenize

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_TEMPLATE = _ROOT / "tenant_template.sql"

# Coloane care par referite dar nu exista in schema tabelului tenant, si sunt fals-pozitive
# documentate (CTE-uri, coloane din tabele public/ne-tenant citite ca tenant, artefacte de parsare).
# Format: {(tabel, coloana), ...}. AZI GOL - orice adaugare cere o justificare in comentariu.
_ALLOWLIST = set()

# Fisierul asta contine SQL sintetic gresit (fixture-ul de auto-test) -> nu se scaneaza pe sine.
_SELF = pathlib.Path(__file__).name


def _schema():
    """tenant_template.sql -> {tabel: {coloane}}. Include ADD COLUMN din template."""
    txt = _TEMPLATE.read_text(encoding="utf-8")
    sch = {}
    for m in re.finditer(
        r"CREATE TABLE (?:IF NOT EXISTS )?TENANT_PLACEHOLDER\.(\w+)\s*\((.*?)\n\);", txt, re.S
    ):
        tbl, body = m.group(1), m.group(2)
        body = re.sub(r"--[^\n]*", "", body)  # comentarii SQL pot contine virgule/paranteze
        cols = set()
        # split pe virgule de nivel 0 (respecta paranteze: numeric(15,2), CHECK(...), UNIQUE(...))
        parts, depth, cur = [], 0, []
        for ch in body:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
            else:
                cur.append(ch)
        parts.append("".join(cur))
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if part.upper().startswith(
                ("CONSTRAINT", "PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "EXCLUDE")
            ):
                continue
            tok = part.split()[0].strip().strip('"')
            if re.fullmatch(r"\w+", tok):
                cols.add(tok.lower())
        sch.setdefault(tbl, set()).update(cols)
    for m in re.finditer(
        r"ALTER TABLE TENANT_PLACEHOLDER\.(\w+)\s+ADD COLUMN(?: IF NOT EXISTS)?\s+(\w+)", txt
    ):
        sch.setdefault(m.group(1), set()).add(m.group(2).lower())
    return sch


def _fragmente(path):
    """Literalii SQL dintr-un .py, reconstruiti: string-uri implicit-concatenate (+) unite,
    f-string-uri cu `{nume}` pastrat si `{expr}` complex -> placeholder."""
    frags, buf = [], []

    def flush():
        if buf:
            frags.append("".join(buf))
            buf.clear()

    try:
        with open(path, "rb") as f:
            toks = list(tokenize.tokenize(f.readline))
    except Exception:
        return frags
    conectori = {tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT}
    i, n = 0, len(toks)
    while i < n:
        t = toks[i]
        if t.type == tokenize.STRING:
            mm = re.match(r"^[a-zA-Z]*('''|\"\"\"|'|\")", t.string)
            if mm:
                q, inner = mm.group(1), t.string[mm.end():]
                if inner.endswith(q):
                    inner = inner[: -len(q)]
                buf.append(inner)
            i += 1
            continue
        if t.type == tokenize.FSTRING_START:
            i += 1
            while i < n and toks[i].type != tokenize.FSTRING_END:
                if toks[i].type == tokenize.FSTRING_MIDDLE:
                    buf.append(toks[i].string)
                    i += 1
                elif toks[i].type == tokenize.OP and toks[i].string == "{":
                    depth, j, names = 1, i + 1, []
                    while j < n and depth > 0:
                        if toks[j].type == tokenize.OP and toks[j].string == "{":
                            depth += 1
                        elif toks[j].type == tokenize.OP and toks[j].string == "}":
                            depth -= 1
                            if depth == 0:
                                break
                        else:
                            names.append(toks[j].string)
                        j += 1
                    buf.append("{%s}" % names[0] if len(names) == 1 and re.fullmatch(r"\w+", names[0]) else " @EXPR@ ")
                    i = j + 1
                else:
                    i += 1
            i += 1
            continue
        if t.type in conectori or (t.type == tokenize.OP and t.string == "+"):
            i += 1
            continue
        flush()
        i += 1
    flush()
    return frags


_KEYWORDS = set("""
select from where and or not in is null true false as on join inner left right outer full cross
group by order having limit offset distinct union all insert into values update set delete returning
conflict do nothing case when then else end asc desc nulls first last between like ilike similar
with recursive using natural exists any some cast coalesce over partition filter within
overriding system value default for share nowait skip locked only lateral fetch row rows
""".split())
_FUNCS = set("""
coalesce sum count min max avg nullif concat concat_ws trim lower upper round abs now
current_date current_timestamp date_trunc to_char to_date extract greatest least string_agg
array_agg json_agg jsonb_agg row_number rank dense_rank lag lead length substring position
generate_series unnest cardinality bool_or bool_and every char_length
""".split())
_TYPES = set("""
int integer bigint smallint numeric decimal real double precision text varchar char character
boolean bool date timestamp timestamptz time interval json jsonb uuid bytea serial money
""".split())
_STOP = _KEYWORDS | _FUNCS | _TYPES


def _referinte_tabele(sql):
    """[(nume, e_tenant, e_extern, alias)] pentru fiecare FROM/JOIN/INTO/UPDATE."""
    refs = []
    for m in re.finditer(
        r"\b(?:FROM|JOIN|INTO|UPDATE)\s+(?:(\{[a-z_]+\}|public|information_schema|pg_catalog|pg_temp)\.)?"
        r"([a-zA-Z_]\w*)(?:\s+(?:AS\s+)?([a-zA-Z_]\w*))?",
        sql,
        re.I,
    ):
        qual, name, alias = m.group(1), m.group(2), m.group(3)
        if alias and alias.lower() in _KEYWORDS:
            alias = None
        extern = bool(qual) and not qual.startswith("{")
        refs.append((name.lower(), (not extern) and name.lower() in _SCHEMA, extern, alias))
    return refs


def _coloane_candidate(sql, tabel):
    """Identificatori necalificati care arata a coloana intr-un statement cu un singur tabel."""
    alias_sel = {a.lower() for a in re.findall(r"\bAS\s+([a-zA-Z_]\w*)", sql, re.I)}
    sql = re.sub(r"\{[^}]*\}", " ", sql)          # interpolari python
    sql = re.sub(r"'(?:''|[^'])*'", " ", sql)     # literali string SQL
    sql = re.sub(r"%\([a-zA-Z_]\w*\)s", " ", sql)  # parametri numiti
    sql = re.sub(r"%+[sd]?", " ", sql)            # %s / %%s / %%
    sql = re.sub(r"@EXPR@", " ", sql)
    sql = re.sub(r"::\s*[a-zA-Z_]+", " ", sql)    # cast-uri
    sql = re.sub(r"\bAS\s+[a-zA-Z_]\w*", " ", sql, flags=re.I)
    cands = set()
    for m in re.finditer(r"(?<![\w.])([a-zA-Z_]\w*)", sql):
        ident = m.group(1)
        if sql[m.end():].lstrip().startswith("("):
            continue  # apel de functie
        il = ident.lower()
        if il in _STOP or il == tabel or il in alias_sel:
            continue
        cands.add(il)
    return cands


def _violari(fragmente_provider):
    """Ruleaza euristica; intoarce lista de (fisier, tabel, coloana, extras)."""
    viol = []
    for fp, frag in fragmente_provider():
        if not re.search(r"\b(SELECT|INSERT|UPDATE|DELETE)\b", frag, re.I):
            continue
        refs = _referinte_tabele(frag)
        if not any(r[1] for r in refs):
            continue
        if len(refs) == 1 and refs[0][1] and refs[0][3] is None:  # un tabel tenant, nealiasat
            tabel = refs[0][0]
            for c in _coloane_candidate(frag, tabel):
                if c not in _SCHEMA[tabel] and (tabel, c) not in _ALLOWLIST:
                    viol.append((fp, tabel, c, " ".join(frag.split())[:110]))
    return viol


_SCHEMA = _schema()


def test_schema_extrasa_e_plauzibila():
    """Sanity: extractia de schema a prins tabelele-cheie cu coloanele-cheie (altfel garda e oarba)."""
    assert "nume" in _SCHEMA["firma_profil"] and "den" not in _SCHEMA["firma_profil"]
    assert "activ" not in _SCHEMA["salariati"]
    assert "simbol" in _SCHEMA["plan_conturi"] and "cont" not in _SCHEMA["plan_conturi"]
    assert "luna" in _SCHEMA["d301_operatiuni"]  # coloane multi-per-linie parsate corect
    assert len(_SCHEMA) >= 40


def test_coloane_sql_exista_in_schema():
    def prov():
        for fp in sorted(glob.glob(str(_ROOT / "core" / "*.py"))) + [str(_ROOT / "main.py")]:
            if pathlib.Path(fp).name == _SELF:
                continue
            for frag in _fragmente(fp):
                yield fp, frag

    viol = _violari(prov)
    assert not viol, "Coloane referite in SQL care NU exista in schema tenant:\n" + "\n".join(
        "  %s: %s.%s  ->  %s" % (pathlib.Path(f).name, t, c, ex) for f, t, c, ex in viol
    ) + "\n-> repara coloana (ex. COALESCE(den,nume)->nume, activ->retras, cont->simbol) sau, daca " \
        "e fals-pozitiv real (CTE/tabel public/alias), adauga (tabel,coloana) in _ALLOWLIST cu motiv."


def test_garda_prinde_coloana_inexistenta():
    """Dovada ca garda are dinti: SQL sintetic cu clasa reparata (den/activ/cont) TREBUIE prins."""
    rele = [
        "SELECT COALESCE(den, nume) FROM firma_profil WHERE id = 1",   # den nu exista
        "SELECT id FROM salariati WHERE activ = true",                  # activ retras
        "SELECT cont, denumire FROM plan_conturi ORDER BY cont",        # cont -> simbol
    ]

    def prov():
        for s in rele:
            yield "sintetic", s

    prinse = {(t, c) for _, t, c, _ in _violari(prov)}
    assert ("firma_profil", "den") in prinse
    assert ("salariati", "activ") in prinse
    assert ("plan_conturi", "cont") in prinse

    # ...si un statement corect NU produce fals-pozitiv
    def prov_ok():
        yield "ok", "SELECT nume, cui FROM firma_profil WHERE id = 1"

    assert not _violari(prov_ok)
