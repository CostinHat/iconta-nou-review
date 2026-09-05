# -*- coding: utf-8 -*-
"""GARD D406 AccountType cablat in genereaza (T2, CATALOG_INVALIDITATE.md; 10.08.2026).

valideaza(res) avea o verificare AccountType (Activ/Pasiv/Bifunctional) pe care genereaza() NU o
chema (cod mort). Un AccountType in afara nomenclatorului era emis tacit -> DUK il respinge la
depunere. Cablat TINTIT in genereaza: pre-DUK -> ValueError care numeste contul.

MUTATIE (HEAD 8b74ccb): genereaza nu verifica AccountType -> pytest.raises PICA.
"""
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_accounttype"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool(); p = _db.pool(); c = p.getconn()
    try:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO \"%s\", public" % SCH)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,platitor_tva,tva_la_incasare,tip_decont) VALUES (1,%s,%s,true,false,'L')",
                        ("ZTEST SRL", "14399840"))
            cur.execute("UPDATE plan_conturi SET tip=%s WHERE simbol=%s", ("Neclasificat", "4111"))
        yield c
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback(); p.putconn(c)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_accounttype_invalid_ridica_numind_contul(conn):
    with pytest.raises(ValueError) as ei:
        d406.genereaza(conn, SCH, 2026, 8)
    msg = str(ei.value)
    assert "AccountType invalid" in msg and "4111" in msg, msg
