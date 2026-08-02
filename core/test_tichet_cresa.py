# -*- coding: utf-8 -*-
"""Tichete de cresa (Legea 165/2018 art.19). Tratament fiscal IDENTIC cu tichetul cultural: impozit 10% pe
valoarea nominala, FARA CAS/CASS/CAM (cresa in CF art.142 lit.r; exceptata din CASS art.157(2) care lasa doar
masa+vacanta). Plafon: 450/luna/copil (art.19(1)), baza confirmata; indexarea (740) e GRI (verdict 17), neaplicata."""
from decimal import Decimal
from datetime import date
import pytest
from core import common
from core.salarizare import calcul_salariu


def test_plafon_cresa_450_per_copil():
    assert common.plafon_cresa(date(2026, 5, 1))[0] == Decimal("450")        # 1 copil (default)
    assert common.plafon_cresa(date(2026, 5, 1), nr_copii=2)[0] == Decimal("900")
    assert common.plafon_cresa(date(2026, 5, 1), nr_copii=3)[0] == Decimal("1350")


def test_cresa_impozit_fara_cass():
    SEM2 = date(2026, 9, 1)
    r0 = calcul_salariu(6000, la_data=SEM2)
    r1 = calcul_salariu(6000, la_data=SEM2, tichet_cresa=400)
    assert r1["tichete_cresa"] == Decimal("400.00")
    assert r1["cass_tichete"] == r0["cass_tichete"]        # cresa NU adauga cass (art.157(2))
    assert r1["cass"] == r0["cass"]
    assert r1["impozit"] - r0["impozit"] == Decimal("40.00")   # 10% pe 400
    assert r0["net"] - r1["net"] == Decimal("40.00")
    assert r1["cost_angajator"] - r0["cost_angajator"] == Decimal("400.00")


def test_cresa_in_registru_fara_cass():
    from core import salarizare
    reg = salarizare.BILETE_VALOARE_TRATAMENT
    assert reg["cresa"]["cass"] is False                   # ca cultural, spre deosebire de masa/vacanta
    assert reg["cresa"]["impozit"].startswith("10%")


# ---- beneficii_api.seteaza cresa: GARD-uri (validare inainte de conn -> unit) ----
def test_cresa_seteaza_multiplu_de_10():
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cresa", 155)
    assert "eroare" in r and "multiplu" in r["eroare"]


def test_cresa_seteaza_peste_plafon_1_copil_blocheaza_indexarea():
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cresa", 700)  # >450 (baza 1 copil); 740 indexat = GRI
    assert "eroare" in r and "plafon" in r["eroare"] and "GRI" in r["eroare"]


def test_cresa_seteaza_2_copii_peste_900():
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cresa", 1000, nr_copii=2)  # plafon 900
    assert "eroare" in r and "plafon" in r["eroare"]


# ---- Integrare DB: constrangerea accepta cresa + seteaza valid (<=450) ----
from core import db as _db, tenant_provisioning as _tp, beneficii_api as _ben

_SCHEMA_CR = "ztest_cresa"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DBOK = _db_ok()


@pytest.fixture
def conn_cr():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_CR)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_CR))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_CR)
                cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa) "
                            "VALUES ('1900101410011','POP','ION','2024-01-01',5000,8,'B') RETURNING id")
                sid = cur.fetchone()[0]
            yield c, sid
        finally:
            c.rollback()


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_cresa_db_roundtrip_baza_450(conn_cr):
    c, sid = conn_cr
    assert _ben.seteaza(c, _SCHEMA_CR, sid, 2026, 5, "cresa", 450).get("ok")   # baza 450 (1 copil) -> ok
    assert float(_ben.lista_luna(c, _SCHEMA_CR, 2026, 5, "cresa").get(sid, 0)) == 450.0
    # peste baza (indexare GRI) blocat inainte de INSERT
    r = _ben.seteaza(c, _SCHEMA_CR, sid, 2026, 5, "cresa", 460)
    assert "eroare" in r and "plafon" in r["eroare"]
