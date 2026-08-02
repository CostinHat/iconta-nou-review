# -*- coding: utf-8 -*-
"""D3 (02.08.2026): excesul de tichete de vacanta peste plafonul anual (6 sm) = venit salarial in BRUTUL
DECLARAT (S731) - regula DUK S74 recalc B4 din brut. Proba obligatorie: D112 cu exces trece DUKIntegrator."""
import pytest
from core import db as _db, tenant_provisioning as _tp, duk as _duk, beneficii_api as _ben, d112


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


_DBOK = _db_ok()
SCHEMA = "ztest_exces_van_d112"


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCHEMA))
                cur.execute("SET search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,email,telefon,"
                            "regim_fiscal,platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                            "(1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','BCR','RO49RNCB0000000000000001',"
                            "'a@b.ro','0700000000','profit',true,'L','Pop','Ion','administrator')")
                cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa,tichet_masa_valoare) "
                            "VALUES ('1900101410011','POPESCU','ION','2024-01-01',5000,8,'B',40) RETURNING id")
                sid = cur.fetchone()[0]
            yield c, sid
        finally:
            c.rollback()


@pytest.mark.skipif(not _DBOK or not _duk.poate_valida("d112"), reason="DB/DUK d112")
def test_d112_cu_exces_vacanta_valid_duk(conn):
    """D112 cu exces de vacanta (in brutul declarat) trece DUK; regresie: fara exces tot valid."""
    c, sid = conn
    x0, _ = d112.genereaza(c, SCHEMA, 2026, 6)
    r0 = _duk.valideaza(x0, "d112", an=2026, luna=6)
    assert r0["stare"] == "valid", "regresie fara exces: %s" % (r0.get("erori") or "")[:200]
    _ben.seteaza(c, SCHEMA, sid, 2026, 6, "vacanta", 30000)  # 30000 > 6*4050=24300 -> exces 5700
    x1, _ = d112.genereaza(c, SCHEMA, 2026, 6)
    r1 = _duk.valideaza(x1, "d112", an=2026, luna=6)
    assert r1["stare"] == "valid", "exces vacanta in brut respins de DUK: %s" % (r1.get("erori") or "")[:300]
