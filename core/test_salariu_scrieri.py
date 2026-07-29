# -*- coding: utf-8 -*-
"""Teste PASUL 2b: scrierile salariului trec pe salariu_istoric (SURSA UNICA); citirile pe curent."""
import pytest

from core import db as _db, tenant_provisioning as _tp
from core import salariati_api as sa
from core import d112

SCHEMA_T = "ztest_salariu_scrieri"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def conn():
    """Schema efemera + search_path (salariati_api ruleaza necalificat), ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
            yield c
        finally:
            c.rollback()


def _creeaza(conn, brut=4050):
    return sa.creeaza_salariat(conn, nume="POP", prenume="I", cnp="1900101410011",
                               data_angajare="2026-01-01", salariu_brut=brut,
                               tip_norma="intreaga")["salariat_id"]


def test_crearea_scrie_salariul_in_istoric(conn):
    sid = _creeaza(conn, 4050)
    with conn.cursor() as cur:
        cur.execute("SELECT valabil_din, salariu_brut FROM salariu_istoric WHERE salariat_id=%s", (sid,))
        rows = cur.fetchall()
    assert len(rows) == 1 and float(rows[0][1]) == 4050   # pe istoric, la data angajarii (2026-01-01)
    assert str(rows[0][0]) == "2026-01-01"
    assert float(sa.detalii_salariat(conn, sid)["salariu_brut"]) == 4050   # detalii citeste din istoric


def test_editarea_salariului_adauga_intrare_noua_nu_suprascrie(conn):
    sid = _creeaza(conn, 4050)
    sa.actualizeaza_salariat(conn, sid, salariu_brut=5000, valabil_din="2026-06-16")
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM salariu_istoric WHERE salariat_id=%s", (sid,))
        assert cur.fetchone()[0] == 2   # SCHIMBARE = intrare noua, nu UPDATE (istoricul se pastreaza)
    assert float(sa.lista_salariati(conn)[0]["salariu_brut"]) == 5000   # lista arata CURENTUL


def test_facilitate_prorata_la_marire_prin_API(conn):
    # Cap-coada: marire la mijloc de luna prin API -> D112 prorateaza facilitatea pe zilele la minim (lit.a).
    sid = _creeaza(conn, 4050)
    sa.actualizeaza_salariat(conn, sid, salariu_brut=5000, valabil_din="2026-06-16")
    _, sal = d112.pull(conn, SCHEMA_T, 2026, 6)
    assert round(float(sal[0]["facilitate"]), 2) == round(300 * 10 / 21, 2)   # 142.86 (zile la minim 1-15 iun)


def test_importul_nu_referi_activ_si_scrie_istoricul():
    # REGRESIE: importul avea 'activ' in INSERT (coloana retrasa PASUL 1) fara niciun test -> a scapat.
    from core import salariati_import_api as imp
    import inspect
    src = inspect.getsource(imp)
    bloc = src[src.index("INSERT INTO salariati"):]
    coloane = bloc[:bloc.index("VALUES")]
    assert "activ" not in coloane, "importul inca referi coloana 'activ' retrasa"
    assert "seteaza" in src, "importul nu scrie salariul in salariu_istoric"
