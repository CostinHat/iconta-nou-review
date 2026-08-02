# -*- coding: utf-8 -*-
"""Tichete culturale (Legea 165/2018 cap.V). Temeiuri VERDE: anaf_surse/RAPORT_verificare_temeiuri.md.
Tratament fiscal DIFERIT de tichetul de masa: impozit 10% pe valoarea nominala, FARA CAS/CASS/CAM
(CASS: art.157(2) excepteaza NUMAI masa+vacanta -> culturalul NU intra in CASS, verdict 11)."""
from decimal import Decimal
from datetime import date
import pytest
from core import common


# ---- Plafon semestrial: ferestre confirmate + blocaj GRI (verdict 16) ----
def test_plafon_cultural_ferestre_confirmate():
    assert common.plafon_cultural(date(2025, 5, 1))[0] == Decimal("220")                 # lunar apr-sep 2025
    assert common.plafon_cultural(date(2025, 5, 1), ocazional=True)[0] == Decimal("450")  # eveniment
    assert common.plafon_cultural(date(2026, 6, 1))[0] == Decimal("250")                 # lunar apr-sep 2026
    assert common.plafon_cultural(date(2026, 8, 1), ocazional=True)[0] == Decimal("490")  # eveniment


def test_plafon_cultural_fereastra_gri_blocheaza():
    # oct 2025 - mar 2026 = GRI (ordin mijloc stub) -> BLOCAJ, nu 240/470 tacit.
    for m in (date(2025, 10, 1), date(2025, 12, 1), date(2026, 3, 1)):
        with pytest.raises(common.PlafonCulturalIndisponibil) as ei:
            common.plafon_cultural(m)
        assert "PERIOADA_BLOCATA:" in str(ei.value)
        assert "GRI" in str(ei.value)


def test_plafon_cultural_semestru_fara_ordin_blocheaza():
    # inainte de apr 2025 si dupa sep 2026 (fara ordin descarcat) -> blocaj motivat.
    for m in (date(2025, 1, 1), date(2026, 11, 1)):
        with pytest.raises(common.PlafonCulturalIndisponibil):
            common.plafon_cultural(m)


# ---- Tratament fiscal in calcul_salariu: impozit 10%, FARA CASS (divergenta fata de masa) ----
def test_cultural_impozit_fara_cass():
    from core.salarizare import calcul_salariu
    SEM2 = date(2026, 9, 1)
    r0 = calcul_salariu(6000, la_data=SEM2)                        # fara cultural
    r1 = calcul_salariu(6000, la_data=SEM2, tichet_cultural=200)   # + 200 lei cultural
    assert r1["tichete_cultural"] == Decimal("200.00")
    # CASS pe tichete NU se schimba (culturalul nu intra in CASS - art.157(2), verdict 11)
    assert r1["cass_tichete"] == r0["cass_tichete"]
    assert r1["cass"] == r0["cass"]
    # impozit +20 (10% pe 200 nominal integral, fara cass de dedus)
    assert r1["impozit"] - r0["impozit"] == Decimal("20.00")
    # net scade cu impozitul cultural (nominalul nu e cash)
    assert r0["net"] - r1["net"] == Decimal("20.00")
    # angajatorul suporta valoarea nominala (o cumpara)
    assert r1["cost_angajator"] - r0["cost_angajator"] == Decimal("200.00")


def test_cultural_diferit_de_masa_pe_cass():
    # Etalon: aceeasi suma ca tichet de MASA da CASS; ca tichet CULTURAL nu da CASS.
    from core.salarizare import calcul_salariu
    SEM2 = date(2026, 9, 1)
    masa = calcul_salariu(6000, la_data=SEM2, tichet_valoare=40, tichet_zile=5)   # 5 x 40 = 200 lei masa (sub plafon 45)
    cult = calcul_salariu(6000, la_data=SEM2, tichet_cultural=200)                # 200 lei cultural
    # masa: cass pe 200 = 20; cultural: cass pe 200 = 0
    assert masa["cass_tichete"] == Decimal("20.00")
    assert cult["cass_tichete"] == Decimal("0.00")


# ---- beneficii_api.seteaza cultural: GARD-uri (validare INAINTE de conn -> unit, fara DB) ----
def test_cultural_seteaza_gri_blocat():
    # oct 2025 - mar 2026 = GRI -> BLOCAT motivat, nu 240/470 tacit (GARD OBLIGATORIU).
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2025, 12, "cultural", 100)
    assert "eroare" in r and "PERIOADA_BLOCATA" in r["eroare"] and "GRI" in r["eroare"]


def test_cultural_seteaza_multiplu_de_10():
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cultural", 155)  # 155 nu e multiplu de 10
    assert "eroare" in r and "multiplu" in r["eroare"]


def test_cultural_seteaza_peste_plafon():
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cultural", 300)  # >250 (plafon lunar apr-sep 2026)
    assert "eroare" in r and "plafon" in r["eroare"]


def test_cultural_seteaza_eveniment_invalid():
    from core import beneficii_api
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cultural", 100, eveniment="paste")
    assert "eroare" in r and "ocazional" in r["eroare"]


def test_cultural_seteaza_ocazional_peste_plafon_eveniment():
    from core import beneficii_api
    # ocazional apr-sep 2026: plafon eveniment 490; 500 depaseste
    r = beneficii_api.seteaza(None, "s", 1, 2026, 5, "cultural", 500, eveniment="ocazional")
    assert "eroare" in r and "plafon" in r["eroare"]


# ============================================================
#  Integrare DB (schema efemera din template) — constrangere cultural + seteaza + GRI pe DB.
# ============================================================
from core import db as _db, tenant_provisioning as _tp, beneficii_api as _ben

_SCHEMA_C = "ztest_cultural"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DBOK = _db_ok()


@pytest.fixture
def conn_cult():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_C)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_C))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_C)
                cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa) "
                            "VALUES ('1900101410011','POPESCU','ION','2024-01-01',5000,8,'B') RETURNING id")
                sid = cur.fetchone()[0]
            yield c, sid
        finally:
            c.rollback()


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_cultural_db_roundtrip(conn_cult):
    c, sid = conn_cult
    # lunar apr-sep 2026 (plafon 250) -> ok
    assert _ben.seteaza(c, _SCHEMA_C, sid, 2026, 5, "cultural", 200).get("ok")
    assert float(_ben.lista_luna(c, _SCHEMA_C, 2026, 5, "cultural").get(sid, 0)) == 200.0
    # + ocazional (plafon eveniment 490) -> se cumuleaza pe salariat/luna
    assert _ben.seteaza(c, _SCHEMA_C, sid, 2026, 5, "cultural", 400, eveniment="ocazional").get("ok")
    assert float(_ben.lista_luna(c, _SCHEMA_C, 2026, 5, "cultural").get(sid, 0)) == 600.0


@pytest.mark.skipif(not _DBOK, reason="DB indisponibil")
def test_cultural_db_gri_blocat_inainte_de_insert(conn_cult):
    c, sid = conn_cult
    r = _ben.seteaza(c, _SCHEMA_C, sid, 2025, 12, "cultural", 100)  # GRI -> blocat, nu ajunge la INSERT
    assert "eroare" in r and "GRI" in r["eroare"]
    assert _ben.lista_luna(c, _SCHEMA_C, 2025, 12, "cultural") == {}  # nimic inserat


# ============================================================
#  GARD: fiecare bilet de valoare declara EXPLICIT cele 4 tratamente + sursa plafonului.
# ============================================================
def test_bilete_valoare_declara_toate_tratamentele():
    from core import salarizare, beneficii_api
    reg = salarizare.BILETE_VALOARE_TRATAMENT
    tipuri = set(beneficii_api.TIPURI) | {"masa"}   # one-off (vacanta/cadou/cultural) + masa (config salariat)
    for tip in tipuri:
        assert tip in reg, "bilet de valoare fara tratament fiscal declarat: %r (declara-l in BILETE_VALOARE_TRATAMENT)" % tip
        e = reg[tip]
        for k in ("impozit", "cas", "cass", "cam", "plafon_sursa", "temei"):
            assert k in e, "%s: tratamentul %r nedeclarat" % (tip, k)


def test_cultural_nu_are_cass_in_registru():
    # Divergenta esentiala vs etalon: culturalul NU are CASS (art.157(2)); masa/vacanta AU.
    from core import salarizare
    reg = salarizare.BILETE_VALOARE_TRATAMENT
    assert reg["cultural"]["cass"] is False
    assert reg["masa"]["cass"] == "10%"
    assert reg["vacanta"]["cass"] == "10%"
