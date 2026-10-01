# -*- coding: utf-8 -*-
"""Tichete de cresa (Legea 165/2018 art.19). Tratament fiscal IDENTIC cu tichetul cultural: impozit 10% pe
valoarea nominala, FARA CAS/CASS/CAM (cresa in CF art.142 lit.r; exceptata din CASS art.157(2) care lasa doar
masa+vacanta). Plafon: 450/luna/copil (art.19(1)) INDEXAT semestrial (HG 1045/2018 art.33) - ferestrele datate din
common.plafon_cresa, citate verbatim din forma consolidata a HG 1045/2018 (30.09.2026). In afara lor: baza 450."""
import re
from decimal import Decimal
from datetime import date
import pytest
from core import common
from core.salarizare import calcul_salariu


@pytest.mark.parametrize("zi,valoare", [
    (date(2024, 3, 31), "450"),   # inainte de prima fereastra documentata: baza L165 art.19 alin.(1)
    (date(2024, 4, 1), "640"),    # Ordin 497/660/2024 art.1: „incepand cu luna aprilie 2024 ... este de 640 lei"
    (date(2024, 9, 30), "640"),   # idem art.2: „se aplica si pentru ... august 2024 si septembrie 2024"
    (date(2024, 10, 1), "660"),   # Ordin 5.339/2.025/2024 art.1: „incepand cu luna octombrie 2024 ... 660 lei"
    (date(2025, 3, 31), "660"),   # idem art.2: „februarie 2025 si martie 2025"
    (date(2025, 4, 1), "670"),    # Ordin 486/287/2025 art.1: „aprilie 2025 ... 670 lei"
    (date(2025, 10, 1), "710"),   # Ordin 1.602/2.007/2025 art.1: „octombrie 2025 ... 710 lei"
    (date(2026, 5, 1), "740"),    # Ordin 368/179/2026 art.1: „aprilie 2026 ... 740 lei"
    (date(2026, 9, 30), "740"),   # idem art.2: „august 2026 si septembrie 2026"
    (date(2026, 10, 1), "770"),   # Ordin 1.255/1.187/2026 art.1 (MO 830/30.09.2026): „octombrie 2026 ... 770 lei"
    (date(2027, 3, 31), "770"),   # idem art.2: „februarie 2027 si martie 2027"
    (date(2027, 4, 1), "450"),    # dupa ultima fereastra: NU se prelungeste tacit 770 -> baza 450, cu motiv
])
def test_plafon_cresa_pe_fereastra(zi, valoare):
    # MUTATIE: fereastra oct.2026 scoasa -> 01.10.2026 cade pe baza 450 -> pica; end 2027-03-31 -> 2027-12-31 -> pica.
    assert common.plafon_cresa(zi)[0] == Decimal(valoare)
    assert common.plafon_cresa(zi, nr_copii=2)[0] == Decimal(valoare) * 2


def test_plafon_cresa_cere_luna():
    # interdictia 3: plafonul se schimba de doua ori pe an - fara luna, nu se calculeaza pe „azi"
    with pytest.raises(ValueError):
        common.plafon_cresa(None)


def test_ferestrele_cresa_contigue_si_citate_verbatim():
    # Fiecare fereastra: temeiul e art.1 al ordinului, VERBATIM in forma consolidata a HG 1045/2018, si poarta
    # valoarea ferestrei; ferestrele se ating zi-la-zi (art.2 al fiecarui ordin acopera golul pana la urmatorul).
    from datetime import timedelta
    from core import scan_citate
    f = common._FERESTRE_CRESA
    for (s1, e1, v1, t1), (s2, _e2, _v2, _t2) in zip(f, f[1:]):
        assert e1 + timedelta(days=1) == s2, (e1, s2)
    for s, e, v, t in f:
        assert scan_citate._verbatim(t) is True, t
        assert re.search(r"este de %d lei" % int(v), t.text_citat), (t, v)


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


def test_cresa_seteaza_pe_LUNA_beneficiului():
    # Plafonul se ia pe luna beneficiului, nu pe azi: 770 e legal in oct.2026, nu in sept.2026 (740).
    # MUTATIE: plafon_cresa(date.today()) in loc de date(an, luna, 1) -> randul de septembrie nu mai pica.
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 9, "cresa", 750)   # > 740 (Ordin 368/179/2026)
    assert "eroare" in r and re.search(r"plafonul de 740", r["eroare"]) and re.search(r"09\.2026", r["eroare"])
    r = beneficii_api.seteaza(None, "s", 1, 2026, 10, "cresa", 780)  # > 770 (Ordin 1.255/1.187/2026)
    assert "eroare" in r and re.search(r"plafonul de 770", r["eroare"])


def test_cresa_seteaza_2_copii_peste_1480():
    from core import beneficii_api
    # mai 2026, 2 copii: 2 x 740 (Ordin 368/179/2026 art.1) = 1480 -> 1490 blocat
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cresa", 1490, nr_copii=2)
    assert "eroare" in r and re.search(r"plafonul de 1480", r["eroare"])


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
    # mai 2026 = fereastra 740 (Ordin 368/179/2026): 740 trece, 750 e blocat inainte de INSERT
    assert _ben.seteaza(c, _SCHEMA_CR, sid, 2026, 5, "cresa", 740).get("ok")
    r = _ben.seteaza(c, _SCHEMA_CR, sid, 2026, 5, "cresa", 750)
    assert "eroare" in r and "plafon" in r["eroare"]
