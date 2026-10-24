# -*- coding: utf-8 -*-
"""[lotul 11, dovada 451 pe copia F5] SQL-ul unei funcții care primește `schema` numește tabelul firmei CU schema.

Ce era: `stat_plata_api.stat_final(conn, schema, …)` citea `SELECT … FROM concedii_medicale` fără prefix, deși
restul modulului scrie `{schema}.tabel`. Pe o conexiune fără `search_path` pe firmă (`db.get_conn()`) cădea cu
*„UndefinedTable: relation "concedii_medicale" does not exist”* — așa cădea regenerarea pe uscat a ciornei salariilor
din `ciorne_depasite` (`_acum_salarii` -> `salarii_contare.propunere` -> … -> `stat_final`), iar contabilul vedea
ciorna „neregenerabilă”. Reprodus pe `tenant_9053`: cu `db.get_conn()` -> UndefinedTable; cu
`db.get_conn("tenant_9053")` -> ok.

CLASA: o funcție din `core/` (fără teste) care are parametrul `schema` și trimite la `execute` (și rudele lui:
`executemany`, `execute_values`, `execute_batch`, `mogrify`) un SQL cu un tabel al firmei — catalogul se CITEȘTE din
`tenant_template.sql` — fără prefixul schemei. Merge numai pe conexiunea deschisă pe schema firmei; pe oricare alta
cade sau, mai rău, citește alt tabel cu același nume. Scanarea vede șirurile constante din argumentul SQL (inclusiv
părțile constante ale unui f-string și constantele de modul / locale numite acolo, ex. `_GRUP_DOC`), după
`FROM | JOIN | INTO | UPDATE | TRUNCATE | TABLE [IF [NOT] EXISTS]` și `to_regclass('<tabel>')`. La 22.10.2026:
27 de apariții (25 + două `INSERT INTO <tabel> (coloane)`, pe care prima măsurătoare nu le vedea), 21 reparate
cu forma modulului (`{schema}.`, `%s.` sau `_q(schema)`), restul în `EXCEPTII`, cu motiv.

CE FACE IMPOSIBIL: o apariție nouă a clasei (o funcție cu `schema` care scrie `FROM <tabel_firmei>` fără prefix)
oprește testul; o excepție care nu mai corespunde codului (reparată sau mutată) oprește și ea testul, ca lista să
nu rămână loc gol pentru o regresie tăcută.

CE NU VEDE: SQL compus din bucăți care nu sunt constante (un parametru, rezultatul unei funcții); o funcție care
numește schema altfel decât `schema` (`sch`, `schema_name`); verificarea de existență făcută prin Python
(`_are_tabel(cur, "tabel")`) — acolo se vede doar dacă ajunge ca literal în `to_regclass('…')`.

MUTAȚIE (22.10.2026): prefixul `{schema}.` scos din `stat_plata_api.stat_final` (`FROM concedii_medicale`) ->
`test_nicio_functie_cu_schema_nu_numeste_tabelul_firmei_fara_ea` pică, numind
`stat_plata_api.py:stat_final.concedii_medicale`.
"""
import ast
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(RAD, "core")

#: excepțiile, cu motivul scris: "fișier:funcție.tabel" -> motiv
EXCEPTII = {
    "migrare_diacritice_plan_conturi.py:aplica.plan_conturi":
        "migrare publicată, rulată; amprenta ei e înregistrată pe producție (public.migrari_rulate) — o modificare ar "
        "cere rerularea; rulează după `SET search_path TO <schema>` în aceeași funcție",
    "migrare_nota_corectie.py:retrimite_refaceri.inregistrari":
        "migrare publicată, rulată; amprenta ei e înregistrată pe producție (public.migrari_rulate) — o modificare ar "
        "cere rerularea; rulează după `SET LOCAL search_path TO <schema>` în aceeași funcție",
    "migrare_retest2.py:note_refacere_nir.inregistrari":
        "migrare publicată, rulată; amprenta ei e înregistrată pe producție (public.migrari_rulate) — o modificare ar "
        "cere rerularea; rulează după `SET LOCAL search_path TO <schema>` în aceeași funcție",
    "coada_api.py:ciornele_documentului.miscari_stoc":
        "fragmentul comun `_GRUP_DOC` (o singură definiție a cheii documentului, folosită și de elementele cozii și de "
        "migrarea publicată `migrare_grup_coada`) nu poartă schemă; funcția face `SET LOCAL search_path` pe schema "
        "firmei înaintea lui, iar tabelul principal (`inregistrari`) e prefixat",
    "coada_api.py:ciornele_documentului.nir":
        "fragmentul comun `_GRUP_DOC` (o singură definiție a cheii documentului, folosită și de elementele cozii și de "
        "migrarea publicată `migrare_grup_coada`) nu poartă schemă; funcția face `SET LOCAL search_path` pe schema "
        "firmei înaintea lui, iar tabelul principal (`inregistrari`) e prefixat",
    # [lotul 12, clasa deficienței 80] `notele_documentului` (validarea din Registrul jurnal validează documentul întreg) citește cheia
    # documentului prin același fragment comun, exact ca `ciornele_documentului` de deasupra
    "coada_api.py:notele_documentului.miscari_stoc":
        "fragmentul comun `_GRUP_DOC` (o singură definiție a cheii documentului, folosită și de elementele cozii și de "
        "migrarea publicată `migrare_grup_coada`) nu poartă schemă; funcția face `SET LOCAL search_path` pe schema "
        "firmei înaintea lui, iar tabelul principal (`inregistrari`) e prefixat",
    "coada_api.py:notele_documentului.nir":
        "fragmentul comun `_GRUP_DOC` (o singură definiție a cheii documentului, folosită și de elementele cozii și de "
        "migrarea publicată `migrare_grup_coada`) nu poartă schemă; funcția face `SET LOCAL search_path` pe schema "
        "firmei înaintea lui, iar tabelul principal (`inregistrari`) e prefixat",
    "solduri_parteneri_api.py:importa.solduri_parteneri":
        "`schema` e opțional (None = schema conexiunii) și tot modulul e construit pe search_path: `asigura_tabel(conn)`, "
        "`existent(conn)`, `rezumat(conn)` n-au schemă; prefixarea numai a DELETE/INSERT ar despărți scrierea de "
        "crearea tabelului. Apelantul (`uc_tenants`) deschide conexiunea pe schema firmei",
}

_RE_TABEL_TPL = re.compile(
    r"CREATE TABLE(?: IF NOT EXISTS)?\s+(?:\{schema\}\.|\"?\{?\w*\}?\"?\.)?\"?([a-z_0-9]+)\"?", re.I)
_RE_SQL = re.compile(
    r"\b(?:FROM|JOIN|INTO|UPDATE|TRUNCATE|TABLE(?:\s+IF(?:\s+NOT)?\s+EXISTS)?)\s+(?:ONLY\s+)?([a-z_][a-z_0-9]*)\b"
    r"|\bto_regclass\(\s*'([a-z_][a-z_0-9]*)'", re.I)
_EXECUTA = {"execute", "executemany", "execute_values", "execute_batch", "mogrify"}
_SQL_AL_DOILEA = {"execute_values", "execute_batch"}   # (cur, sql, …)


def tabele_firmei():
    tpl = io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    return {t.lower() for t in _RE_TABEL_TPL.findall(tpl)}


def _atribuiri(corp):
    """nume -> [expresii] pentru atribuirile simple `x = …` din `corp` (lista de noduri)."""
    out = {}
    for nod in corp:
        for n in ast.walk(nod):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                out.setdefault(n.targets[0].id, []).append(n.value)
    return out


def _constante(expr, nume):
    """Șirurile constante din `expr`, plus cele din constantele numite acolo (o singură trecere, fără recursie)."""
    noduri = [expr] + [v for x in ast.walk(expr) if isinstance(x, ast.Name) for v in nume.get(x.id, [])]
    return [c.value for nd in noduri for c in ast.walk(nd) if isinstance(c, ast.Constant) and isinstance(c.value, str)]


def scaneaza(sursa, fisier, tabele):
    """[(cheie "fișier:funcție.tabel", linie)] pentru fiecare tabel al firmei numit fără schemă."""
    arb = ast.parse(sursa)
    modul = _atribuiri([n for n in arb.body if isinstance(n, ast.Assign)])
    gasite = set()
    for fn in ast.walk(arb):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if "schema" not in [a.arg for a in fn.args.args + fn.args.kwonlyargs + fn.args.posonlyargs]:
            continue
        nume = dict(modul)
        for k, v in _atribuiri(fn.body).items():
            nume[k] = nume.get(k, []) + v
        for n in ast.walk(fn):
            if not isinstance(n, ast.Call) or not n.args:
                continue
            f = n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else "")
            if f not in _EXECUTA:
                continue
            sql = n.args[1] if f in _SQL_AL_DOILEA and len(n.args) > 1 else n.args[0]
            for text in _constante(sql, nume):
                for m in _RE_SQL.finditer(text):
                    grup = 1 if m.group(1) else 2
                    tabel = m.group(grup)
                    if tabel.lower() in tabele and text[max(0, m.start(grup) - 1):m.start(grup)] != ".":
                        gasite.add(("%s:%s.%s" % (fisier, fn.name, tabel.lower()), n.lineno))
    return sorted(gasite)


def scaneaza_core():
    tabele = tabele_firmei()
    out = {}
    for f in sorted(os.listdir(CORE)):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        for cheie, linie in scaneaza(io.open(os.path.join(CORE, f), encoding="utf-8").read(), f, tabele):
            out.setdefault(cheie, []).append(linie)
    return out


# ── gardul ───────────────────────────────────────────────────────────────────
def test_nicio_functie_cu_schema_nu_numeste_tabelul_firmei_fara_ea():
    noi = ["  %s (linia %s)" % (k, ", ".join(map(str, v))) for k, v in sorted(scaneaza_core().items())
           if k not in EXCEPTII]
    assert not noi, (
        "SQL cu tabelul firmei FĂRĂ schemă, într-o funcție care primește `schema`:\n%s\n\nPe o conexiune fără "
        "search_path pe firmă (`db.get_conn()`) cade cu UndefinedTable (dovada 451: ciorna salariilor „neregenerabilă”). "
        "Prefixează cu forma modulului (`{schema}.tabel`, `%%s.tabel`, `_q(schema)`), sau pune cheia în EXCEPTII cu "
        "motivul." % "\n".join(noi))


def test_exceptiile_corespund_codului():
    """O excepție reparată sau mutată iese din listă — altfel devine loc gol pentru o regresie tăcută."""
    gasite = scaneaza_core()
    moarte = sorted(k for k in EXCEPTII if k not in gasite)
    assert moarte == [], "excepții care nu mai corespund codului (scoate-le din EXCEPTII): %s" % moarte
    fara_motiv = sorted(k for k, v in EXCEPTII.items() if len(v.strip()) < 40)
    assert fara_motiv == [], "excepții fără motiv scris: %s" % fara_motiv


# ── anti-vacuu: scanerul prinde ce trebuie și nu prinde ce nu trebuie ───────────
_TAB = {"firma_profil", "pontaj", "salariati", "inregistrari"}

_RAU = '''
_FRAG = "SELECT 1 FROM inregistrari i"

def rau_from(conn, schema):
    cur.execute("SELECT nume FROM firma_profil WHERE id = 1")

def rau_insert(conn, schema):
    cur.execute("INSERT INTO pontaj (salariat_id, zi) VALUES (%s, %s)", (1, 2))

def rau_fstring(conn, schema, an):
    cur.execute(f"SELECT * FROM salariati WHERE an = {an}")

def rau_constanta(cur, schema):
    cur.execute("SELECT x FROM (" + _FRAG + ") q")

def rau_regclass(cur, *, schema):
    cur.execute("SELECT to_regclass('salariati')")
'''

_BUN = '''
def _q(schema):
    return '"%s".' % schema

def bun_fstring(conn, schema):
    cur.execute(f"SELECT nume FROM {schema}.firma_profil WHERE id = 1")

def bun_procent(conn, schema):
    cur.execute("SELECT count(*) FROM %s.salariati" % schema)

def bun_q(conn, schema):
    cur.execute("INSERT INTO " + _q(schema) + "pontaj (salariat_id) VALUES (1)")

def bun_public(conn, schema):
    cur.execute("SELECT 1 FROM public.declaratii_depuse, unnest(%s) AS u", ([1],))

def fara_schema(conn):
    cur.execute("SELECT nume FROM firma_profil")   # pe search_path, fără parametrul `schema`: în afara clasei
'''


def test_scanerul_prinde_fragmentele_rele():
    chei = [k for k, _l in scaneaza(_RAU, "sintetic.py", _TAB)]
    assert chei == ["sintetic.py:rau_constanta.inregistrari", "sintetic.py:rau_from.firma_profil",
                    "sintetic.py:rau_fstring.salariati", "sintetic.py:rau_insert.pontaj",
                    "sintetic.py:rau_regclass.salariati"]


def test_scanerul_nu_prinde_formele_bune():
    assert scaneaza(_BUN, "sintetic.py", _TAB) == []


def test_catalogul_tabelelor_firmei_e_citit():
    tabele = tabele_firmei()
    assert len(tabele) > 50
    assert {"firma_profil", "salariati", "pontaj", "concedii_medicale", "plan_conturi", "inregistrari"} <= tabele
