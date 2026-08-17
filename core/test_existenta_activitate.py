# -*- coding: utf-8 -*-
"""[Regula 13 + Regula 6] GARDA: existenta_firma_an numara TOATA activitatea reala datata.

Bug (audit tenant_006, 18.08.2026): existenta_firma_an decidea "firma a fost activa in an" DOAR din
facturi / salariati / inregistrari. O firma NEPLATITOARE cu achizitii intracomunitare isi inregistreaza
activitatea in d301_operatiuni (din care se naste CHIAR restanta D301), iar casa/banca sunt tot operatiuni
datate. Fara ele, semaforul afisa simultan, pe ACELASI ecran (Regula 14 pct.2):
  - "operatiuni intracomunitare inregistrate in iun 2026" (restanta D301, din d301_operatiuni), SI
  - "nu pot demonstra ca firma era activa in 2026" (D100/D406, din existenta_firma_an).
Contradictie: aceeasi operatiune, doua verdicte opuse. Acest test cade pe codul vechi (existenta ignora
d301_operatiuni / casa_operatiuni / extras_linii) si trece dupa reparatie. Nomenclatoarele si soldurile
initiale (pot preceda existenta) NU sunt activitate -> raman excluse (testul le lasa neatinse).
"""
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


SCH = "_t_exist_%d" % os.getpid()


@pytest.fixture
def schema_gol():
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)
            c.execute('CREATE SCHEMA "%s"' % SCH)
    try:
        yield db
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


def _creaza(db, ddl, insert=None, args=None):
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute(ddl)
            if insert:
                c.execute(insert, args or ())


def test_d301_operatiuni_e_activitate_demonstrabila(schema_gol):
    """Achizitia IC inregistrata in d301_operatiuni PROBEAZA ca firma a existat/operat in an."""
    db = schema_gol
    from core.control_incrucisat import existenta_firma_an
    _creaza(db, 'CREATE TABLE "%s".d301_operatiuni (id serial, an int, luna int)' % SCH,
            'INSERT INTO "%s".d301_operatiuni (an, luna) VALUES (2026, 6)' % SCH)
    with db.get_conn() as conn:
        assert existenta_firma_an(conn, SCH, 2026) is True, \
            "d301_operatiuni 2026 ignorat de existenta_firma_an (contradictie cu restanta D301)"
        assert existenta_firma_an(conn, SCH, 2025) is False, \
            "operatiune doar pe 2026 -> 2025 ramane fara premisa"


def test_casa_operatiuni_e_activitate_demonstrabila(schema_gol):
    """Operatiunile de casa datate = activitate (firma a tranzactionat in an)."""
    db = schema_gol
    from core.control_incrucisat import existenta_firma_an
    _creaza(db, 'CREATE TABLE "%s".casa_operatiuni (id serial, data date)' % SCH,
            'INSERT INTO "%s".casa_operatiuni (data) VALUES (%%s)' % SCH, ("2026-03-10",))
    with db.get_conn() as conn:
        assert existenta_firma_an(conn, SCH, 2026) is True, "casa_operatiuni 2026 ignorat"
        assert existenta_firma_an(conn, SCH, 2025) is False


def test_extras_banca_e_activitate_demonstrabila(schema_gol):
    """Liniile de extras de cont datate = activitate (firma a avut miscari bancare in an)."""
    db = schema_gol
    from core.control_incrucisat import existenta_firma_an
    _creaza(db, 'CREATE TABLE "%s".extras_linii (id serial, data date)' % SCH,
            'INSERT INTO "%s".extras_linii (data) VALUES (%%s)' % SCH, ("2026-05-20",))
    with db.get_conn() as conn:
        assert existenta_firma_an(conn, SCH, 2026) is True, "extras_linii 2026 ignorat"


def test_schema_fara_activitate_ramane_false(schema_gol):
    """Regresie: o schema fara niciun semn de activitate -> False (necunoscut, nu fabricat)."""
    db = schema_gol
    from core.control_incrucisat import existenta_firma_an
    with db.get_conn() as conn:
        assert existenta_firma_an(conn, SCH, 2026) is False
