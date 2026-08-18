# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 13] GARDA: D390 pe zero SEMNALEAZA achizitiile din d301_operatiuni.

Front 2 (audit tenant_006, 18.08.2026): D390 se construieste din facturi + linii manuale, NU din
d301_operatiuni (care n-are codT/codO furnizor pt cod A - vezi decizia de flux). Un neplatitor art.317 isi
inregistreaza achizitiile IC in ecranul D301; daca genereaza D390 fara sa le reflecte manual, D390 refuza
"pe zero". Mesajul GENERIC ("verifica facturile UE") era FALS/inselator - firma ARE operatiuni (in D301).
Acum refuzul semnaleaza operatiunile din D301 si indruma spre adaugarea manuala (Tip A). Mirror al refuzului
D301 care semnaleaza facturile IC neintroduse. Auto-derivarea d301->D390 ramane decizie de produs.
"""
import os
import re
import pytest


SCH = "_t_d390_%d" % os.getpid()


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


def test_achizitii_d301_numara_perioada():
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    from core.d390 import achizitii_d301
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)
            c.execute('CREATE SCHEMA "%s"' % SCH)
            c.execute('CREATE TABLE "%s".d301_operatiuni (id serial, an int, luna int, tip int, partener_tara varchar(2))' % SCH)
            c.execute('INSERT INTO "%s".d301_operatiuni (an, luna, tip) VALUES (2026, 6, 1)' % SCH)
    try:
        with db.get_conn() as conn:
            assert achizitii_d301(conn, SCH, 2026, 6) == 1, "achizitia din d301 (2026/6) nu e numarata"
            assert achizitii_d301(conn, SCH, 2026, 5) == 0, "luna fara achizitii -> 0"
            assert achizitii_d301(conn, SCH + "_inexistent", 2026, 6) == 0, "schema/tabela absenta -> 0 (nu crapa)"
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


@pytest.mark.parametrize("cui", ["95451848"])  # tenant_006 (Achizitii IC Neplatitor)
def test_d390_refuz_semnaleaza_d301_pe_tenant_006(cui):
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    from core import d390
    with db.get_conn() as cpub:
        with cpub.cursor() as c:
            c.execute("SELECT schema_name FROM public.tenants WHERE cui=%s ORDER BY id DESC LIMIT 1", (cui,))
            r = c.fetchone()
    if not r:
        pytest.skip("tenant_006 neseeduit")
    schema = r[0]
    with db.get_conn(schema) as conn:
        # tenant_006 are 1 d301_operatiuni pe 6/2026, 0 facturi -> D390 refuza CU semnalarea d301
        with pytest.raises(ValueError) as exc:
            d390.genereaza(conn, schema, 2026, 6)
        msg = str(exc.value)
        assert "d301" in msg.lower(), \
            "refuzul D390 pe zero NU semnaleaza operatiunile din D301 (mesaj generic inselator): %s" % msg
        assert "manual" in msg.lower(), "mesajul nu indruma spre adaugarea manuala (Tip A)"
