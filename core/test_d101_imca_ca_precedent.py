# -*- coding: utf-8 -*-
"""core/test_d101_imca_ca_precedent.py — gard D101 IMCA eligibilitate (C-4 transa 3).

BUG reparat: declaratii_api._d101 INJECTEAZA `ca_an_precedent_eur` in `manual`, dar genereaza()
scotea doar cota/d_grup/cod_obligatie -> cheia ajungea in `intrari` si calcul_d101 o respingea ca
"intrare necunoscuta" -> ORICE apel D101 prin API cu CA an precedent CRAPA (ValueError). In plus,
IMCA "unde se aplica" era inaccesibil pe calea DB.

FIX (temei CF art.18^1 alin.1): genereaza scoate ca_an_precedent_eur si porteaza eligibilitatea:
  - sub prag (<=50 mil euro) -> IMCA NU se aplica (cazul comun), generarea merge, P47=0;
  - peste prag fara P47 -> eroare CLARA (IMCA datorata, VT/Vs/I/A nederivate din balanta), NU crash criptic
    si NU omitere tacita (ar subevalua impozitul);
  - peste prag cu P47 furnizat -> se genereaza, P47 raportat.

RED pe cod vechi: testul (1) pica cu "intrari necunoscute". Mutatie: scoaterea pop-ului reintroduce crash-ul.
"""
import pytest
from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, duk as _duk, d101 as _d101, declaratii_api as _api

_SCHEMA = "ztest_d101_imca_ca"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_profit():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,regim_fiscal,"
                    "platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) "
                    "VALUES (1,'PROFIT SRL','14399840','Str. Test 1','Bucuresti','B','6202','real',"
                    "true,'L','Pop','Ion','administrator')")
                cur.execute("INSERT INTO inregistrari (data, status, sursa, descriere) "
                            "VALUES ('2026-06-15','validata','test','Vanzare') RETURNING id")
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'4111','707',100000)", (iid,))
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'607','401',60000)", (iid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ca_precedent_sub_prag_nu_crapa(conn_profit):
    """RED pe cod vechi: CA an precedent < 50 mil euro -> generarea NU trebuie sa crape; IMCA nu se aplica."""
    xml, res = _d101.genereaza(conn_profit, _SCHEMA, Perioada(2026), {"ca_an_precedent_eur": 1_000_000})
    assert res.P.get("P47", 0) == 0, "IMCA NU se aplica sub prag; P47=%r" % res.P.get("P47")
    assert res.P["P1"] == 100000  # baza contabila neafectata


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_api_path_ca_precedent_nu_crapa(conn_profit):
    """Calea REALA a bug-ului: declaratii_api._d101 injecteaza ca_an_precedent_eur -> nu mai crapa."""
    xml, res = _api._d101(conn_profit, _SCHEMA, {"an": 2026, "ca_an_precedent_eur": 2_000_000})
    assert res.an == 2026 and res.P.get("P47", 0) == 0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_peste_prag_fara_P47_eroare_clara(conn_profit):
    """Peste prag (>50 mil euro) fara P47 -> eroare CLARA IMCA (art.18^1), NU 'intrari necunoscute',
    NU omitere tacita (ar subevalua impozitul unei firme mari)."""
    with pytest.raises(ValueError) as ei:
        _d101.genereaza(conn_profit, _SCHEMA, Perioada(2026), {"ca_an_precedent_eur": 60_000_000})
    msg = str(ei.value)
    assert "IMCA" in msg and "18^1" in msg, "eroare neclara: %s" % msg
    assert "necunoscute" not in msg, "inca crapa criptic: %s" % msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_peste_prag_cu_P47_genereaza_DUK(conn_profit):
    """Peste prag cu P47 furnizat -> se genereaza, P47 raportat, DUK-valid."""
    xml, res = _d101.genereaza(conn_profit, _SCHEMA, Perioada(2026),
                               {"ca_an_precedent_eur": 60_000_000, "P47": 500000})
    assert res.P["P47"] == 500000
    r = _duk.valideaza(xml, "d101", an=2026)
    assert r["stare"] == "valid", "DUK a respins D101 cu P47(IMCA): %s" % r.get("erori")
