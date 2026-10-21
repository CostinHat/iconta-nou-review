# -*- coding: utf-8 -*-
"""[lotul 10, comanda 10.1 pct.3 — „eroarea 500 intermitentă din /eu/ciorne se repară în acest lot”] GARDA.

Defectul (văzut în curățenia e2e a lotului 9, `uvicorn.log`): `GET /eu/ciorne` citește lista firmelor utilizatorului, apoi
interoghează schema fiecăreia. O firmă ștearsă între cele două pași (schema ei a dispărut) dădea
`psycopg2.errors.UndefinedTable: relation "inregistrari" does not exist` -> 500 pe toată lista.

Clasa: o buclă dintr-o cerere care deschide schema fiecărei firme dintr-o listă citită înainte. Drumurile găsite (scanul AST de
mai jos, pe `core/uc_*.py` și `main.py`): `uc_eu.eu_ciorne`, `uc_migrare.terti_in_balanta_firme`,
`uc_coada.reia_declaratiile_in_asteptare` — toate trec acum prin `db.pe_firma_existenta`.
"""
import ast
import glob
import os

import pytest


def _db():
    cale = os.path.expanduser("~/.iconta/db.env")
    if not os.path.exists(cale):
        return None
    for l in open(cale, encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, v = l.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    try:
        from core import db
        db.init_pool()
        return db
    except Exception:
        return None


SCH = "_t_firma_stearsa_%d" % os.getpid()


def _apeluri_get_conn_in_bucla(fn):
    """(linie, text) pentru fiecare `*.get_conn(<schemă>)` din corpul unei bucle `for` a fișierului."""
    out = []
    for nod in ast.walk(ast.parse(open(fn, encoding="utf-8").read())):
        if isinstance(nod, (ast.For, ast.AsyncFor)):
            for sub in ast.walk(nod):
                if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "get_conn"
                        and sub.args and not (isinstance(sub.args[0], ast.Constant) and sub.args[0].value is None)):
                    out.append((sub.lineno, ast.unparse(sub)))
    return out


def test_nicio_bucla_din_cerere_nu_deschide_schema_unei_firme_direct():
    """Structural: în use-case-uri și în `main.py`, o buclă nu deschide schema unei firme cu `db.get_conn(schema)`, ci prin
    `db.pe_firma_existenta` — altfel o firmă ștearsă în timpul cererii o face 500."""
    fisiere = sorted(f for f in glob.glob("core/uc_*.py") if "/test_" not in f) + ["main.py"]
    assert len(fisiere) > 20, "premisa: use-case-urile există (scanul nu e vid)"
    gasite = {f: _apeluri_get_conn_in_bucla(f) for f in fisiere}
    gasite = {f: v for f, v in gasite.items() if v}
    assert gasite == {}, "buclă care deschide schema unei firme direct (folosește db.pe_firma_existenta): %r" % gasite


def test_scanul_vede_forma_veche():
    """Anti-vacuu: scanul de mai sus recunoaște exact forma care dădea 500."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write("def f(firme):\n    for t in firme:\n        with db.get_conn(t['schema_name']) as conn:\n            pass\n")
    try:
        assert len(_apeluri_get_conn_in_bucla(f.name)) == 1
    finally:
        os.unlink(f.name)


@pytest.fixture
def db_cu_schema():
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)
            c.execute('CREATE SCHEMA "%s"' % SCH)
            c.execute('CREATE TABLE "%s".inregistrari (id int)' % SCH)
    try:
        yield db
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


def _numara(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari")
        return cur.fetchone()[0]


def test_firma_stearsa_in_timpul_cererii_iese_din_lista(db_cu_schema):
    db = db_cu_schema
    assert db.pe_firma_existenta(SCH, _numara) == (True, 0)
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA "%s" CASCADE' % SCH)          # firma ștearsă după citirea listei
    assert db.pe_firma_existenta(SCH, _numara) == (False, None)


def test_tabela_lipsa_pe_o_firma_care_exista_nu_se_ascunde(db_cu_schema):
    """Aceeași eroare pe o schemă care ÎNCĂ există e un defect real (tabelă lipsă, migrare nerulată): se ridică."""
    import psycopg2.errors as pe
    db = db_cu_schema
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP TABLE "%s".inregistrari' % SCH)
    with pytest.raises(pe.UndefinedTable):
        db.pe_firma_existenta(SCH, _numara)
