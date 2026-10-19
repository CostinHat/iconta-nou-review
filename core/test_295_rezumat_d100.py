# -*- coding: utf-8 -*-
"""295 — D100 pasul 2: „Rezumat” cu baza de calcul (comanda Costin 16.10.2026, completarea 290–295, verbatim în DECIZII): „D100 pasul 2
arată doar obligația (cod 121, 10 lei, cota 1), fără baza de calcul: veniturile perioadei pe conturi și eventualele deduceri. Adaugă
«Rezumat» ca la D112.” Temei: CF art.53 (baza micro: veniturile din orice sursă, reducerile comerciale acordate se scad — `repo_d100`),
CF art.41 (profitul, cumulat). Schemă efemeră, anulată la final."""
import pytest

from core import db as _db
from core import d100 as _d100
from core import tenant_provisioning as _tp
from core.common import Perioada
from core.test_d100_reconciliere import _db_ok, _profil, _venit

_SCHEMA = "efemer_295"


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_295_rezumatul_d100_micro_arata_veniturile_pe_conturi_si_deducerile(conn):
    """MUTAȚIE: `res.sinteza = sinteza_d100(...)` scos din `genereaza` -> Rezumatul gol -> pică."""
    with conn.cursor() as cur:
        _profil(cur, "micro")
        _venit(cur, "2026-08-15", 800, "704")
        _venit(cur, "2026-09-02", 200, "766")
        cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES ('2026-09-10','r','validata') RETURNING id")
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'709','4111',50)",
                    (cur.fetchone()[0],))
    _xml, res = _d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    assert [(o.cod_oblig, o.suma_dat) for o in res.obligatii] == [("121", 10)]          # 950 x 1% = 9,50 -> 10 (rotunjire aritmetică)
    assert res.sinteza[1:] == ["cont 704: 800,00 lei", "cont 709 (se scade): -50,00 lei", "cont 766: 200,00 lei",
                               "Deduceri din bază: 709, 50,00 lei.",
                               "Baza impozabilă: 950,00 lei × cota 1% = cod 121: 10 lei (rotunjit la leu)."], res.sinteza
    assert res.sinteza[0].startswith("Baza de calcul T3/2026")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_295_rezumatul_d100_profit_arata_cumulatul(conn):
    with conn.cursor() as cur:
        _profil(cur, "profit")
        _venit(cur, "2026-08-15", 10000)
    _xml, res = _d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    # [376–378, comanda Costin 8.2] rezultatul fiscal cumulat (CF art.19 alin.(1)), iar de plată = cumulat − declarat (OPANAF 587/2016
    # anexa 4 pct.3.1.2); fiecare rând al calculului e în rezumat
    assert res.sinteza[1:4] == ["rezultatul contabil: 10.000,00 lei (venituri 10.000,00 − cheltuieli 0,00)",
                                "deduceri: 0,00 lei; venituri neimpozabile: 0,00 lei; cheltuieli nedeductibile: 0,00 lei",
                                "profitul impozabil cumulat: 10.000,00 lei; impozitul cumulat: 1.600,00 lei"], res.sinteza
    assert res.sinteza[-1] == "de plată pe T3/2026: 1.600,00 lei − 0,00 lei = 1.600,00 lei", res.sinteza
