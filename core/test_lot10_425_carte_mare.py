# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 425 — cartea mare / fișa contului] Comanda Costin 10.1, verbatim: „Când fișierul are soldurile inițiale ale anului
și rulajele, ele intră ca sold inițial și sume precedente, cu toate conturile care au rulaj. Când are doar solduri finale, comportamentul
de acum rămâne”. Balanța o aplică (`documente_api.balanta`); Cartea mare — prin înlocuitorul ei legal, Fișa de cont pentru operațiuni
diverse (OMFP 2634/2015, Anexa 2: „Registrul Cartea mare poate fi inlocuit cu Fisa de cont pentru operatiuni diverse.”) — pornea de la
zero. Acum: `fisa_cont.sold_initial_preluat`, din `core/rulaje_preluate` (aceeași regulă ca balanța).

Profil (schemă efemeră din `tenant_template.sql`, ROLLBACK): balanța de deschidere la 30.09.2026 — 4111: sold la 1 ianuarie 1.000 D,
rulaje 5.000 D / 4.000 C, sold final 2.000 D; 5121: numai rulaje (300 / 300), sold 0; o notă validată pe 05.10: 4111 = 704 500.
"""
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp, fisa_cont as _fc, documente_api as _da

_SCHEMA = "test_lot10_425_carte_mare"
D = Decimal


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta, si_an_debit, si_an_credit, "
                            "rulaj_an_debit, rulaj_an_credit) VALUES ('4111', 2000, 0, '2026-09-30', 1000, 0, 5000, 4000), "
                            "('5121', 0, 0, '2026-09-30', 0, 0, 300, 300)")
                cur.execute("INSERT INTO inregistrari (data, status, sursa, descriere) VALUES ('2026-10-05','validata','test','vanzare') "
                            "RETURNING id")
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'4111','704',500)",
                            (cur.fetchone()[0],))
            yield c
        finally:
            c.rollback()


def _fisa(c, cont, an, luna=None):
    si, rul = _fc.sold_initial_preluat(c, _SCHEMA, cont, an, luna)
    return _fc.fisa_cont(c, _SCHEMA, cont, an, luna, sold_initial=si, rulaj_preluat=rul)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_anul_preluarii_cu_rulaje_porneste_de_la_1_ianuarie(conn):
    f = _fisa(conn, "4111", 2026)
    # „ele intră ca sold inițial și sume precedente”: sold inițial = soldul de la 1 ianuarie, primul rând = rulajul preluat
    assert f["sold_initial"] == D("1000.00"), f["sold_initial"]
    r0 = f["randuri"][0]
    assert (r0.debit, r0.credit, r0.jurnal) == (D("5000.00"), D("4000.00"), "preluare"), r0
    assert (f["total_debit"], f["total_credit"]) == (D("5500.00"), D("4000.00"))
    # soldul final = cel al balanței (aceeași regulă): 1.000 + 5.000 − 4.000 + 500
    assert (f["sold_final"], f["sens_sold_final"]) == (D("2500.00"), "D")
    bal = {r["cont"]: r for r in _da.balanta(conn, _SCHEMA, 2026, 10)}
    assert (bal["4111"]["si_d"], bal["4111"]["sf_d"]) == (1000.0, 2500.0), bal["4111"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_luna_de_dupa_preluare_porneste_din_soldul_final(conn):
    # fereastra octombrie nu cuprinde [01.01, 30.09]: rulajele preluate nu se pot împărți pe luni -> soldul final de la preluare
    f = _fisa(conn, "4111", 2026, 10)
    assert f["sold_initial"] == D("2000.00") and all(r.jurnal != "preluare" for r in f["randuri"])
    assert f["sold_final"] == D("2500.00")
    # noiembrie: soldul preluat + nota din octombrie (notele validate dinaintea ferestrei)
    assert _fisa(conn, "4111", 2026, 11)["sold_initial"] == D("2500.00")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_fara_rulaje_comportamentul_ramane(conn):
    with conn.cursor() as cur:
        cur.execute("UPDATE solduri_initiale SET si_an_debit = NULL, si_an_credit = NULL, rulaj_an_debit = NULL, rulaj_an_credit = NULL")
    # „Când are doar solduri finale, comportamentul de acum rămâne” — balanța pornește din soldul final preluat; fișa la fel
    f = _fisa(conn, "4111", 2026)
    assert f["sold_initial"] == D("2000.00") and all(r.jurnal != "preluare" for r in f["randuri"])
    assert f["sold_final"] == D("2500.00")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_conturile_cu_rulaj_numai_in_balanta_apar_in_lista(conn):
    # „cu toate conturile care au rulaj”: 5121 are rulaj numai în balanța de deschidere
    assert {"4111", "704", "5121"} <= set(_fc.conturi_cu_miscare(conn, _SCHEMA, 2026))
    assert "5121" not in _fc.conturi_cu_miscare(conn, _SCHEMA, 2026, 10)
