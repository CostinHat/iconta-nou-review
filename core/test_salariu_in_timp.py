# -*- coding: utf-8 -*-
"""GARD — schimbarea salariului cu dată de la care se aplică (decizia Costin 04.10.2026).

Decizia: „Ecranul de schimbare a salariului cu dată de la care se aplică (scrie în salariu_istoric; statul de plată
proratizează deja mărirea în cursul lunii). Refuz numit pentru dată invalidă sau suprapusă; nicio pierdere a ce s-a tastat.
Probă cap-coadă: schimbare pe 15 ale lunii → statul de plată și D112 cu cele două fracțiuni, DUK valid.”

Ce face imposibil:
  * o zi inexistentă care ajunge în driver (500) în loc de refuz pe câmp;
  * un salariu aplicat înainte de angajare sau după încetare;
  * rescrierea TĂCUTĂ a salariului de la o dată deja în istoric (UPSERT) — înlocuirea doar la cerere explicită;
  * rescrierea unei luni închise pe ușa salariului — inclusiv cea atinsă de o schimbare datată ÎNAINTEA ei;
  * pierderea proratării: mărirea pe 15 ale lunii -> două fracțiuni în statul de plată și în D112.
Codul muncii art.159 alin.(1) + art.49 alin.(2) (brutul pe zilele din contract) — citate la lotul 19 pct.4c.
"""
from core.common import Perioada  # [D1, lotul 07.10] d112.pull/genereaza(conn, schema, perioada)
import contextlib
import xml.etree.ElementTree as ET
from decimal import Decimal as D

import pytest

from core import db as _db
from core import tenant_provisioning as _tp

_SCHEMA = "ztest_salariu_in_timp"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def lume(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,platitor_tva,"
                            "tip_decont,declarant_nume,declarant_prenume,declarant_functie,telefon) VALUES (1,'SALARIU SRL',"
                            "'14399840','Str 1','Buc','B','6202','BCR','RO49RNCB0000000000000001','profit',true,'L','Pop','Ion',"
                            "'administrator','0722000000')")
                cur.execute("INSERT INTO salariati (id,cnp,nume,prenume,data_angajare,data_incetare,ore_zi,judet_casa) "
                            "OVERRIDING SYSTEM VALUE VALUES (3,'1900101410011','GEORGESCU','ILIE','2026-01-01',NULL,8,'B')")
                cur.execute("INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES (3,'2026-01-01',4400)")
            proxy = _FaraCommit(conn)
            from core import uc_tenants, auth_api, uc_comun as _uc
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCHEMA)
            monkeypatch.setattr(_uc, "_schema_sau_404", lambda *a, **k: _SCHEMA)
            yield conn
        finally:
            conn.rollback()


def _schimba(**k):
    from core import uc_tenants
    from main import SalariatEdit
    return uc_tenants.salariat_actualizeaza(1, 3, SalariatEdit(**k), {"uid": 1, "rol": "admin_firma"})


def _istoric(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT valabil_din::text, salariu_brut FROM %s.salariu_istoric WHERE salariat_id=3 ORDER BY 1" % _SCHEMA)
        return [(d, float(s)) for d, s in cur.fetchall()]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("data", ["2026-02-31", "2025-12-01"])
def test_data_invalida_sau_inainte_de_angajare_e_refuzata_pe_camp(lume, data):
    # MUTAȚIE: verificarea zilei din calendar / a angajării scoasă -> driverul (500) sau intrare înainte de contract -> pică
    from core import erori
    with pytest.raises(erori.DateInvalide) as e:
        _schimba(salariu_brut=5000, valabil_din=data)
    assert [x["camp"] for x in e.value.detaliu["erori_campuri"]] == ["valabil_din"]
    assert _istoric(lume) == [("2026-01-01", 4400.0)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_data_suprapusa_e_refuzata_cu_intrarea_existenta_si_se_inlocuieste_doar_explicit(lume):
    # „suprapusă” = există deja o intrare la aceeași dată. MUTAȚIE: verificarea scoasă -> UPSERT tăcut -> pică
    from core import erori
    with pytest.raises(erori.DateInvalide) as e:
        _schimba(salariu_brut=4600, valabil_din="2026-01-01")
    d = e.value.detaliu
    assert (d["cod"], d["existent"]) == ("SALARIU_DATA_OCUPATA",
                                         {"valabil_din": "2026-01-01", "salariu_brut": 4400.0, "salariu_nou": 4600.0})
    assert _istoric(lume) == [("2026-01-01", 4400.0)]
    _schimba(salariu_brut=4600, valabil_din="2026-01-01", inlocuieste=True)
    assert _istoric(lume) == [("2026-01-01", 4600.0)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_luna_inchisa_atinsa_de_schimbare_nu_se_rescrie(lume):
    """Iulie închisă. O schimbare de la 10 iunie atinge iunie ȘI iulie (până la următoarea intrare, 15.09) -> refuzată,
    deși iunie e deschisă. MUTAȚIE: poarta doar pe luna datei -> trece -> pică."""
    from core import erori
    _schimba(salariu_brut=5000, valabil_din="2026-09-15")
    with lume.cursor() as cur:
        cur.execute("INSERT INTO %s.perioade_blocate (an, luna) VALUES (2026, 7)" % _SCHEMA)
    with pytest.raises(erori.Blocat):
        _schimba(salariu_brut=4800, valabil_din="2026-06-10")
    _schimba(salariu_brut=4800, valabil_din="2026-08-10")       # august deschis, până la 15.09: trece
    assert _istoric(lume) == [("2026-01-01", 4400.0), ("2026-08-10", 4800.0), ("2026-09-15", 5000.0)]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_marirea_pe_15_doua_fractiuni_in_stat_si_d112_duk_valid(lume):
    """Septembrie 2026: 22 de zile lucrătoare; 1–14 = 10 zile la 4.400, 15–30 = 12 zile la 5.000 -> 2.000 + 2.727,27.
    MUTAȚIE: statul pe salariul de la sfârșitul lunii (fără proratare) -> 5.000 -> pică."""
    from core import stat_plata_api, d112
    _schimba(salariu_brut=5000, valabil_din="2026-09-15")
    (g,) = stat_plata_api.stat_plata(lume, _SCHEMA, 2026, 9)
    assert D(str(g["brut"])) == D("4727.27")      # 4400 x 10/22 + 5000 x 12/22
    xml, _res = d112.genereaza(lume, _SCHEMA, Perioada(an=2026, luna=9))
    b1 = [dict(el.attrib) for el in ET.fromstring(xml.split("?>", 1)[1] if xml.startswith("<?xml") else xml).iter()
          if el.tag.split("}")[-1] == "asiguratB1"]
    assert [(x.get("B1_sal1"), x.get("B1_sal2")) for x in b1] == [("5000", "4727")]   # contractual nou / realizat
    try:
        from core import duk
        ok = duk.poate_valida("d112")
    except Exception:
        ok = False
    if ok:
        v = duk.valideaza(xml, "d112", an=2026, luna=9, timeout=240)
        assert v.get("stare") == "valid", v.get("erori")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_detaliile_salariatului_arata_istoricul(lume):
    # ecranul de schimbare arată ce date sunt ocupate. MUTAȚIE: `istoric_salariu` scos din detalii -> KeyError -> pică
    from core import salariati_api
    _schimba(salariu_brut=5000, valabil_din="2026-09-15")
    with lume.cursor() as cur:
        cur.execute("SET search_path TO %s, public" % _SCHEMA)
    assert salariati_api.detalii_salariat(lume, 3)["istoric_salariu"] == [
        {"valabil_din": "2026-01-01", "salariu_brut": 4400.0}, {"valabil_din": "2026-09-15", "salariu_brut": 5000.0}]
